"""
 `FIWARE` support classes
"""

import asyncio
import json
import re
import sys
import traceback
from datetime import datetime

import aiohttp


from agptools.logs import logger
from agptools.helpers import DATE, camel_case_split

from syncmodels.definitions import (
    ORG_KEY,
    REG_PRIVATE_KEY,
    MONOTONIC_KEY,
    ID_KEY,
)
from syncmodels.crud import tf, esc, parse_duri

from swarmtube import __version__
from ..logic.swarmtube import (
    Particle,
    SkipWave,
    RetryWave,
)


log = logger(__file__)


class OrionParticleSync(Particle):
    """Generic Particle to synchronize data with Orion"""

    MAPPER = None
    EXCLUDE = set(["id", "type"])
    TYPES = {
        "ts": "timestamp",
        "date": "timestamp",
        "location": "geo:point",
        str: "string",
        float: "float",
        int: "integer",
    }
    TIMEOUT_INFO = aiohttp.ClientTimeout(
        total=None,
        # total timeout (time consists connection establishment for a new connection
        # or waiting for a free connection from a pool if pool connection limits are exceeded)
        # default value is 5 minutes, set to `None` or `0` for unlimited timeout
        sock_connect=15,
        # Maximal number of seconds for connecting to a peer for a new connection,
        # not given from a pool. See also connect.
        sock_read=15,
        # Maximal number of seconds for reading a portion of data from a peer
    )

    # TODO: set by config / yaml
    TARGET_URL = "https://orion.ccoc.spec-cibernos.com/v2/entities"
    # Note: for batch update use the following url (doesn't apply right now as is one to one)
    # url = "https://orion.ccoc.spec-cibernos.com/v2/op/update?options=flowControl"

    HEADERS = {
        "Content-Type": "application/json",
        "fiware-service": "fs_ccoc",
        "fiware-servicepath": "/beacons/traces",
        "User-Agent": f"OrionParticleSync/{__version__}",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
    }
    SERVICE_PATH = ""  # Need to be overridden by the user or use default pattern generation

    @classmethod
    def get_service_path(cls):
        name = cls.SERVICE_PATH or cls.__name__

        for ban in 'Orion', 'Particle', 'Sync', 'Tube':
            name = name.replace(ban, '')

        tokens = [""] + camel_case_split(name)
        name = '/'.join(tokens).lower()
        return name

    def __init__(self, uid, sources, broker, storage, target_url=None):
        super().__init__(uid, sources, broker, storage)
        self.target_url = target_url or self.TARGET_URL
        self.HEADERS = self.HEADERS.copy()
        self.HEADERS["User-Agent"] = (
            f"{self.__class__.__name__}/{__version__}"
        )
        self.HEADERS["fiware-servicepath"] = self.get_service_path()

    def _guess_type(self, key, value):
        type_ = self.TYPES.get(key)
        if type_ is None:
            if isinstance(value, str):
                x = DATE(value)
                if isinstance(x, datetime):
                    return "timestamp"
            # return default value of 'string'
            type_ = self.TYPES.get(value.__class__, "string")
        return type_

    def _to_fiware(self, data):
        """Create a json for Orion based on given data"""

        # "type" --> entity_type: beacons.traces
        # TODO: force ALT_KEY existence
        # fquid = data[ORG_KEY]
        fquid = data.get(ORG_KEY) or data["_path"]

        _uri = parse_duri(fquid)
        entity_id = _uri[ID_KEY]

        # entity_id = tf(entity_id)
        # entity_id = esc(entity_id)
        data["id"] = entity_id
        # data["id"] = str(data[MONOTONIC_KEY])  # --> entity_id

        date = datetime.fromtimestamp(data[MONOTONIC_KEY] / 1000000000)
        # data['ts'] = date.strfmt("%Y-%m-%d %H:%M:%S.%f %z")
        # data['ts'] = date.strftime("%Y-%m-%dT%H:%M:%S.%f")
        data["ts"] = date.strftime("%Y-%m-%dT%H:%M:%S")  # --> entity_ts

        try:
            data["location"] = "{lat},{lng}".format_map(data)
        except KeyError:
            pass

        data.setdefault(
            "type", self.get_service_path().replace("/", ".")[1:]
        )

        # check if a validation MAPPER is defined
        if self.MAPPER:
            item = self.MAPPER.pydantic(data)
            if item:
                data = item.model_dump(mode="json")
        else:
            # filter any private key when pydantic models are
            # not helping us, so if we need to publish a private
            # key, create a pydantic model that contains the key
            # and this purge will not be executed
            for key in list(data):
                if re.match(REG_PRIVATE_KEY, key):
                    data.pop(key)
        # try to translate all found fields
        for key, value in data.items():
            if key in self.EXCLUDE:
                # payload["id"] = {
                # "value": payload["id"],
                # "type": "string",
                # }
                # payload["type"] = {
                # "value": payload["type"],
                # "type": "string",
                # }
                continue
            data[key] = {
                "value": value,
                "type": self._guess_type(key, value),
            }
        # if False:
        # data2["ts"] = {
        # "value": data2["ts"],
        # "type": "timestamp",
        # }
        # data2["mac"] = {
        # "value": data2["mac"],
        # "type": "string",
        # }
        # data2["date"] = {
        # "value": data2["date"],
        # "type": "timestamp",
        # }
        # data2["publish_date"] = {
        # "value": data2["publish_date"],
        # "type": "timestamp",
        # }
        # data2["device_id"] = {
        # "value": data2["device_id"],
        # "type": "string",
        # }
        # data2["location"] = {
        # "value": data2["location"],
        # "type": "geo:point",
        # }
        # for key, value in data.items():
        # if value != data2[key]:
        # log.error("[%s]: %s != %s", key, value, data2[key])
        return data

    async def _post(self, data):
        """
        400: {'error': 'BadRequest', 'description': 'Invalid characters in attribute type'}
        400: {'error': 'BadRequest', 'description': 'a component of ServicePath contains an illegal character'}
        422: {'error': 'Unprocessable', 'description': 'Already Exists'}

        """
        for tries in range(1, 15):
            try:
                async with aiohttp.ClientSession() as session:
                    # log.info(f"{self.app_url}{path}: {query_data}")
                    async with session.post(
                        # TODO: fiware-servicepath is based on data item + headers
                        self.target_url,
                        data=data,
                        headers=self.HEADERS,
                    ) as response:
                        if response.status < 300:
                            # result = await response.json()
                            # meta = result["meta"]
                            # stream = result["result"]

                            stream = await response.json()
                            meta = response.headers
                            return stream, meta

                        elif response.status < 500:
                            # not recoverable
                            # we need to advance the wave cursor
                            result = await response.json()
                            log.error(
                                "%s: %s --> %s",
                                response.status,
                                data,
                                result,
                            )
                            log.error(result)
                            msg = {
                                "reason": result,
                                "url": self.target_url,
                                "data": data,
                            }
                            raise SkipWave(msg)
                        else:
                            # need to retry later on
                            # DO NOT advance the wave cursor
                            result = await response.json()
                            log.error(
                                "%s: %s --> %s",
                                response.status,
                                data,
                                result,
                            )
                            log.error(result)
                            msg = {
                                "reason": result,
                                "url": self.target_url,
                                "data": data,
                                "delay": 15,
                            }
                            raise RetryWave(msg)  #  retry in 15 secs

            except aiohttp.ClientError as why:
                log.error(why)
                log.error(
                    "".join(traceback.format_exception(*sys.exc_info()))
                )

            log.warning("retry: %s: %s", tries, data)
            await asyncio.sleep(0.5)

    async def _compute(self, edge, ekeys):
        """
        # TODO: looks like is a batch insertion! <-----

        Example
        {
        "actionType": "APPEND",
        "entities": [
            {
                "id": "TL1",
                "type": "totem.views",
                "ts": {
                    "value": "2024-03-06 09:43:11",
                    "type": "timestamp"
                },
                "conteo": {
                    "value": 9,
                    "type": "integer"
                },
                "component": {
                    "value": "C11 - TOTEMS",
                    "type": "string"
                },
                "place": {
                    "value": "LUCENTUM",
                    "type": "string"
                },
                "location": {
                    "type": "geo:point",
                    "value": "38.365156979723906,-0.438225677848391"
                }
            }
        ]
        }
        """
        assert len(ekeys) == 1, "Beacon Stream must have just 1 input tube"

        # returning None so no data is really needed to sync
        # just advance the TubeSync wave mark

        for tube_name in ekeys:
            data = edge[tube_name]

            # FIWARE composing data
            payload = self._to_fiware(data)
            if payload:
                raw = json.dumps(payload)
                stream, meta = await self._post(raw)
                return stream  # None

        return None
