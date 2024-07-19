"""Main module."""

# library modules
import asyncio
import random
import time
import sys
import traceback
import functools
from typing import Callable, List, Dict, Any
from pprint import pformat
from pydantic import BaseModel

from agptools.helpers import build_uri
from agptools.logs import logger
from agptools.progress import Progress

from syncmodels.crud import parse_duri
from syncmodels.storage import (
    Storage,
    WaveStorage,
    tf,
    esc,
    REG_SPLIT_PATH,
    SurrealConnectionPool,
)
from syncmodels.definitions import URI, JSON, UID, WAVE, ORG_KEY

# ---------------------------------------------------------
# local imports
# ---------------------------------------------------------
from ..definitions import MONOTONIC_KEY

# ---------------------------------------------------------
# models / mappers
# ---------------------------------------------------------
# from ..models.swarmtube import SwarmtubeApp
# from .. import mappers
# from ..models.enums import *
# from ..definitions import TAG_KEY

# ---------------------------------------------------------
# Loggers
# ---------------------------------------------------------

log = logger(__name__)


class Event(BaseModel):
    "TBD"
    wave: WAVE
    uid: UID
    payload: Any = None


class Broker:
    "Basic Broker capabilities"

    def __init__(self):
        self.subscriptions: Dict[UID, List[Callable]] = {}

    async def start(self):
        "any action related to start broker operations"

    async def stop(self):
        "any action related to stop broker operations"

    async def subscribe(self, uid: UID, callback: Callable):
        "TBD"
        inventory = self.subscriptions.setdefault(uid, [])
        if callback not in inventory:
            inventory.append(callback)

    async def unsubscribe(self, uid: UID, callback: Callable):
        "TBD"
        inventory = self.subscriptions.setdefault(uid, [])
        if callback in inventory:
            inventory.remove(callback)


class iAgent(object):
    def __init__(
        self,
        uid,
        broker: Broker,
        storage: WaveStorage,
        meta=None,
        *args,
        **kw,
    ):
        self.uid = uid
        self.broker = broker
        self.storage = storage

        self.state = ST_INIT
        self.meta = {} if meta is None else meta
        super().__init__(*args, **kw)

    async def main(self):
        "main loop"
        # await super().main()
        await self._start_live()
        while self.state < ST_STOPPED:
            await self._idle()
        await self._stop_live()

    async def _start_live(self):
        log.info("[%s] _start_live", self.uid)

    async def _stop_live(self):
        log.info("[%s] _stop_live", self.uid)

    async def _idle(self):
        log.debug("[%s] alive", self.uid)
        await asyncio.sleep(2)


class Tube(iAgent):
    """Represents the concept of a stream of events that
    can be located by a UID or searching metadata
    """

    uid: UID

    def __init__(
        self,
        uid: UID,
        sources: List[UID],
        broker: Broker,
        storage: Storage,
        meta=None,
    ):
        super().__init__(uid=uid, broker=broker, storage=storage, meta=meta)
        self.sources = sources
        assert isinstance(
            self.storage, WaveStorage
        ), "needed for subscriptions"


class App(iAgent):
    "TBD"

    def __init__(self, uid="app", *args, **kw):
        super().__init__(uid=uid, *args, **kw)
        self.tubes = {}
        self.tasks = {}
        self.loop = None
        self.t0 = 0

    async def _start_live(self):
        assert self.loop is None
        self.loop = asyncio.get_running_loop()
        self.t0 = self.loop.time()

        # start broker and storage
        await self.storage.start()
        await self.broker.start()

        # start tubes
        for uid, tube in self.tubes.items():
            log.info("- starting: [%s]", uid)
            self.tasks[uid] = self.loop.create_task(tube.main(), name=uid)

    async def _stop_live(self):
        # requests fibers to TERM
        for uid, tube in self.tubes.items():
            log.info("- term: [%s]", uid)
            tube.state = ST_STOPPED

        # wait and clear stopped for 5 secs
        t0 = self.loop.time()
        while self.tasks and self.loop.time() - t0 < 5:
            for uid, task in list(self.tasks.items()):
                if task.done():
                    self.tasks.pop(uid)
                    log.info("- end: [%s]", uid)
            await asyncio.sleep(0.5)

        # kill remaining
        for uid, task in self.tasks.items():
            log.info("- kill: [%s]", uid)
            task.cancel()

        # wait and clear stopped for 5 secs
        t0 = self.loop.time()
        while self.tasks and self.loop.time() - t0 < 5:
            for uid, task in list(self.tasks.items()):
                if task.done():
                    self.tasks.pop(uid)
                    log.info("- finished: [%s]", uid)
            await asyncio.sleep(0.5)

        # stop broker and storage
        await self.storage.stop()
        await self.broker.stop()

    def must_stop(self):
        return False

    def add(self, *tubes):
        for tube in tubes:
            self.tubes[tube.uid] = tube

    def run(self):
        asyncio.run(self.main())

    async def _idle(self):
        await super()._idle()
        if self.must_stop():
            self.state = ST_STOPPED
            log.info("[%s] want stop", self.uid)


ST_INIT = 0
ST_HISTORICAL = 1
ST_SWITCHING = 2
ST_LIVE = 3
ST_STOPPED = 4


class Clock(Tube):
    "A tube that emit a clock tick"
    counter: int

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.counter = 0

    async def _start_live(self):
        await super()._start_live()

    async def _stop_live(self):
        await super()._stop_live()

    async def _idle(self):
        await super()._idle()
        self.counter += 1
        edge = {
            # MONOTONIC_KEY: time.time(),  # TODO: let the storage set this value?
            #'uid': uid,
            "payload": self.counter,
        }
        await self.storage.put(self.uid, edge)


class SwarmTubeException(Exception):
    "base for all SwarmTube Exceptions"


class SkipWave(SwarmTubeException):
    """the item can't be processed but we
    need to advance the Wave to the next one
    """


class RetryWave(SwarmTubeException):
    """the item can't be processed but we
    need to retry later on, so the Wave
    doesn't jump to the next one
    """


class Particle(Tube):
    "TBD"
    MAX_EVENTS = 1024
    _live = Dict[UID, List[Event]] | None
    _historical = Dict[UID, List[Event]] | None

    RETRY_DELAY = 15

    def __init__(
        self, uid: UID, sources: List[UID], broker: Broker, storage: Storage
    ):
        super().__init__(
            uid, sources=sources, broker=broker, storage=storage
        )
        # self.uid = uid
        # self.sources = sources
        # self.broker = broker
        # self.storage = storage
        self._wave = {}
        self._live = {}
        self._historical = {}
        self._live_activity = asyncio.Queue()
        self._need_resync = False
        self._milk = []
        self.metrics = Progress()
        for uri in self.sources:
            self._live[uri] = []
            self._historical[uri] = []

    async def main(self):
        "TBD"
        self._need_resync = True
        # self.metrics.start()
        while self._need_resync:
            self._need_resync = False
            await self._start_live()
            await self._start_historical()

        log.info("=" * 70)
        log.info("[%s] >> Idle", self.uid)
        log.info("=" * 70)

        while self.state < ST_STOPPED:
            try:
                event = await asyncio.wait_for(
                    self._live_activity.get(), timeout=2.0
                )
                _uid, _wave, edge = self.pop_edge(self._live)
                if edge:
                    await self.dispatch(edge)
                    # self._wave[_uid] = _wave
                else:
                    assert not all(
                        self._live.values()
                    ), "some input must be missing here!"
                    break
            except asyncio.TimeoutError:
                pass  #  No live data has been received
            except Exception as why:
                log.error(why)
                log.error(
                    "".join(traceback.format_exception(*sys.exc_info()))
                )

            # self._live_activity.clear()

            self.metrics.update(n=0)

        await self._stop_live()

    async def _start_live(self):
        "TBD"
        log.info("[%s] ++ Requesting LIVE STREAMING", self.uid)

        for uid in self.sources:
            await self.broker.subscribe(uid, self.live)

    async def _stop_live(self):
        "TBD"
        for uid in self.sources:
            await self.broker.unsubscribe(uid, self.live)

    async def _start_historical(self):
        "TBD"
        self.state = ST_HISTORICAL
        self._wave = await self.storage.last_waves(self.sources, self.uid)
        assert isinstance(self._wave, Dict), "missing await?"

        # self._wave = {uid: _wave for uid in self.sources}
        buffer = self._historical
        self._milk = list(self.sources)
        log.info("-" * 70)
        log.info("[%s] -- Switching to HISTORICAL", self.uid)
        log.info("-" * 70)
        while self.state < ST_LIVE:
            # load some historical data
            n = 0
            while self._milk:
                uid = self._milk.pop()
                data = await self.storage.storage.since(
                    uid, self._wave[uid], max_results=self.MAX_EVENTS
                )
                if data:
                    buffer[uid].extend(data)
                    n += len(data)
                    self._wave[uid] = data[-1][MONOTONIC_KEY]
                    break

            if n == 0:  # no more historical data
                # move live data to historical and try to continue until
                # we get a state with no more historical data and no more live data
                self.state = ST_SWITCHING
                # time.sleep(0.9)
                assert id(buffer) != id(self._live)
                for uid, _buff in self._live.items():
                    _hist = self._historical[uid]
                    while True:
                        try:
                            candidate = _buff.pop(0)
                            if candidate[MONOTONIC_KEY] > self._wave[uid]:
                                _hist.append(candidate)
                                n += 1
                            else:
                                # this live event has been captured by historical polling
                                # so is already processed
                                # print(f"*** already processed: --> {candidate}")
                                pass
                        except IndexError:
                            break
                if n == 0:
                    log.info("*" * 70)
                    log.info(
                        "[%s] ** Switching to LIVE STREAMING **", self.uid
                    )
                    log.info("*" * 70)
                    self.metrics.update(n=0, force=True)
                    self.state = ST_LIVE

            # try to process buffer
            while self.state < ST_LIVE:
                _uid, _wave, edge = self.pop_edge(buffer)
                assert _wave is None or isinstance(
                    _wave, int
                ), "must be an integer"
                if edge:
                    await self.dispatch(edge)
                    if not buffer[uid]:  # request more data
                        self._milk.append(_uid)
                elif self.state == ST_SWITCHING:
                    break
                else:
                    break  # continue loading more historical
            # check if we have an overflow while processing historical data
            if self._need_resync:
                log.info(
                    "[%s] *** ---> Request Stopping Streaming due OVERFLOW",
                    self.uid,
                )
                await self._stop_live()

    def live(self, _uri: UID, event: Dict):
        "TBD"
        uri = _uri['uri']
        if len(self._live[uri]) >= self.MAX_EVENTS:
            self._need_resync = True
            return

        # wave_uri = parse_duri(event['id'])
        if MONOTONIC_KEY not in event:
            m = REG_SPLIT_PATH.match(event['id'])
            if m:
                event[MONOTONIC_KEY] = m.groupdict()['id']

        self._live[uri].append(event)
        self._live_activity.put_nowait(event)

        if self.state == ST_LIVE:
            pass
            # try process events until the edge is incomplete
            # while self.state < ST_STOPPED:
            # _uid, _wave, edge = self.pop_edge(self._live)
            # if edge:
            # self.dispatch(edge)
            ## self._wave[_uid] = _wave
            # else:
            # assert not all(
            # self._live.values()
            # ), "some input must be missing here!"
            # break

        elif len(self._live[uri]) >= self.MAX_EVENTS:
            # request stop streaming and a new re-sync process
            self._need_resync = True

    def pop_edge(self, buffer):
        "analyze buffer and return edge if all data is available for processing next step"
        # TODO: implement a policy delegation criteria to know when edge is ready to be processed
        waves = {}
        for uri, data in buffer.items():
            if data:
                waves[uri] = data[0][MONOTONIC_KEY]

        # have we all needed data?
        if len(waves) == len(self.sources):
            _uid, _wave, edge = self._pop_policy(buffer, waves)
            self._wave[_uid] = _wave
            return _uid, _wave, edge
        return None, None, None

    def _pop_policy(self, buffer, waves):
        """Default policy is to make the minimal step for computation.
        - get the minimal wave
        - drop the input related with the minimal wave
        - return a custom `edge` for computation
        """
        edge = {}
        _wave = min(waves.values())
        for uid, data in buffer.items():
            item = data[0]
            if _wave == item[MONOTONIC_KEY]:
                data.pop(0)
                _uid = uid
            edge[uid] = item

        edge[MONOTONIC_KEY] = _wave
        return _uid, _wave, edge

    async def dispatch(self, edge):
        "TBD"
        # build the data to be processed
        # split metadata (".*__" fields by now) and each
        # input stream
        # TODO: review the criteria for keywords filtering
        ikeys = set([k for k in edge if k.endswith("__")])
        ekeys = ikeys.symmetric_difference(edge)
        assert ekeys, "no payload in the edge?"

        # set found metadata
        data = {k: edge[k] for k in ikeys}
        while self.state < ST_STOPPED:
            log.info("[%s] -> dispatch", self.uid)
            log.info("%s", pformat(edge))
            try:
                # do the computation
                payload = await self._compute(edge, ekeys)
                if payload is None:
                    log.info("[%s] <- dispatch: SKIP due NO DATA", self.uid)
                else:
                    data.update(payload)
                    # store results
                    # and shift sync / waves info
                    await self.storage.put(self.uid, **data)
                    N = sum([len(_) for _ in self._live.values()])
                    self.metrics.update(buffer=N)
                    log.info("[%s] <- dispatch:", self.uid)
                    log.info("%s", pformat(data))

                wave = data.get(MONOTONIC_KEY)  # Must exist!
                if wave:
                    await self.storage.update_sync_wave(
                        self.sources,
                        self.uid,
                        wave,
                    )
                else:
                    log.error("data %s has no %s key", data, MONOTONIC_KEY)
                break  #  let continue with next wave
            except SkipWave as why:
                # some error is produced, but we want to jump to the next wave
                wave = data.get(MONOTONIC_KEY)  # Must exist!
                if wave:
                    log.info("Skip wave [%s], reason: %s", wave, why)

                    await self.storage.update_sync_wave(
                        self.sources,
                        self.uid,
                        wave,
                    )
                else:
                    log.error("data %s has no %s key!", data, MONOTONIC_KEY)
                break  #  let continue with next wave
            except RetryWave as why:
                delay = self.RETRY_DELAY
                for msg in why.args:
                    log.info("Retry wave, reason: %s", msg)
                    if isinstance(msg, dict):
                        delay = msg.get("delay", self.RETRY_DELAY)
                log.warning(
                    "%s._compute() has failed but is needed a retry (%s secs)",
                    str(self),
                    delay,
                )
                await asyncio.sleep(delay)
            except Exception as why:
                log.error(why)
                log.error(
                    "".join(traceback.format_exception(*sys.exc_info()))
                )
                delay = self.RETRY_DELAY * 10
                log.warning(
                    "%s._compute() has failed for an UNEXPECTED reason. "
                    "Wave edge can't be moved forward, retry in (%s secs)",
                    str(self),
                    delay,
                )
                await asyncio.sleep(delay)

    async def _compute(self, edge, ekeys):
        """
        Return None if we don't want to store info
        """
        raise NotImplementedError()


# ---------------------------------------------------------
# Surreal Implementation
# ---------------------------------------------------------
from surrealist import Surreal


class Subscription(BaseModel):
    "live queries callbacks to be fired"
    lq_uid: UID
    callbacks: List[Callable]


class SurrealBroker(Broker):
    "pub / sub broker based on surreal"

    def __init__(self, url):
        super().__init__()
        self.url = url
        # TODO: missing surreal credentials
        self.connection_pool = SurrealConnectionPool(url)
        self._live_queries = {}
        log.info("broker will use [%s]", self.url)

    async def subscribe(self, uri: URI, callback: Callable):
        "TBD"
        await super().subscribe(uri, callback)

        _uri = parse_duri(uri)
        _sub_uri = dict(_uri)
        _sub_uri['path'] = f"/{_sub_uri['_path']}"
        # sub_uri = build_uri(**_sub_uri)

        table = tf(_sub_uri['_path'])
        if not (lq := self._live_queries.get(table)):
            # TODO: table or uri (fquid)?
            handler = functools.partial(self.dispatch, table)

            key = (_uri["fscheme"], _uri["host"])
            pool = self.connection_pool
            connection = pool.connections.get(key) or await pool._connect(
                *key
            )
            assert connection, "surreal connection has failed"

            # TODO: I think this is unnecessary
            info = connection.session_info().result
            namespace, database = _uri['fscheme'], _uri['host']
            if info['ns'] != namespace or info['db'] != database:
                connection.use(namespace, database)

            res = connection.live(table, callback=handler)
            lq_uid = res.result

            lq = self._live_queries[table] = Subscription(
                lq_uid=lq_uid, callbacks=[]
            )

        lq.callbacks.append((callback, _uri))

    async def unsubscribe(self, uri: URI, callback: Callable):
        "TBD"
        await super().unsubscribe(uri, callback)

        _uri = parse_duri(uri)
        _sub_uri = dict(_uri)
        _sub_uri['path'] = f"/{_sub_uri['_path']}"
        # sub_uri = build_uri(**_sub_uri)

        table = tf(_sub_uri['_path'])
        if lq := self._live_queries.get(table):
            lq.callbacks.remove((callback, _uri))
            if not lq.callbacks:

                key = (_uri["fscheme"], _uri["host"])
                pool = self.connection_pool
                connection = pool.connections.get(
                    key
                ) or await pool._connect(*key)
                assert connection, "surreal connection has failed"

                # TODO: I think this is unnecessary
                info = connection.session_info().result
                namespace, database = _uri['fscheme'], _uri['host']
                if info['ns'] != namespace or info['db'] != database:
                    connection.use(namespace, database)

                connection.kill(lq.lq_uid)
                self._live_queries.pop(table)
        else:
            pass

    def dispatch(self, uid: str, res):
        "process an event from broker"
        result = res["result"]
        assert result["action"] in (
            "CREATE",
            "UPDATE",
        )
        # event = Event(uid=uid, **result['result'])
        event = result["result"]
        for callback, _uri in self._live_queries[uid].callbacks:
            if _uri.get('id') in (event.get(ORG_KEY), None):
                callback(_uri, event)


# ---------------------------------------------------------
# Example of a Particle Implementation
# ---------------------------------------------------------
class PlusOne(Particle):
    "Example of a Particle Implementation that adds 1 to the payload"

    async def _compute(self, edge, ekeys):
        s = 0
        for k in ekeys:
            s += edge[k]["payload"]

        s /= len(ekeys)
        s += random.random()
        data = {
            self.uid: s,
        }
        return data


class TempDiff(Particle):
    """Example of a Particle Implementation that computes
    the difference between the first and the last value"""

    async def _compute(self, edge, ekeys):
        X = [edge[k]["payload"] for k in ekeys]
        y = X[0] - X[-1]
        return y


# ---------------------------------------------------------
class TubeSync(Particle):
    """Do nothing special, but synchronize data"""
