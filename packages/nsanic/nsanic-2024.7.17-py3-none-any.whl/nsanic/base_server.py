import asyncio

from sanic import Sanic
from tortoise.contrib.sanic import register_tortoise

from nsanic.base_conf import BaseConf
from nsanic.libs import consts


class InitServer:

    def __init__(
            self,
            conf,
            mws: (list, tuple) = None,
            bps: (list, tuple) = None,
            excps: (list, tuple) = None,
            start_evts: list = None,
            stop_evts: list = None):
        self.__conf: BaseConf = conf
        self.__conf.set_conf()
        consts.GLOBAL_TZ = conf.TIME_ZONE
        self.__start_evts = start_evts or []
        self.__stop_evts = stop_evts or []
        self.__server = Sanic(self.__conf.SERVER_NAME, log_config=self.__conf.log_conf())
        self.__server.update_config(self.__conf)
        self.__loop_tasks = []
        if self.__conf.db_conf:
            register_tortoise(self.__server, config=self.__conf.db_conf())
        for mdw_fun in mws or []:
            mdw_fun.set_conf(self.__conf)
            self.__server.middleware(mdw_fun.main)
        for bp_cls in bps or []:
            bp_cls.set_conf(self.__conf)
            bp_cls.load_default_api()
            hasattr(bp_cls, 'init_loop_task') and self.__loop_tasks.append(bp_cls)
            self.__server.blueprint(bp_cls.bpo)
        for expt_fun in excps or []:
            expt_fun.set_conf(self.__conf)
            self.__server.error_handler.add(Exception, expt_fun.catch_req)
        self.__server.register_listener(self.__after_server_start, 'after_server_start')
        self.__server.register_listener(self.__before_server_stop, 'before_server_stop')

    async def __after_server_start(self, req, loop):
        self.__conf.rds and self.__conf.rds.set_looping()
        await asyncio.sleep(1)
        for task in self.__loop_tasks:
            task.init_loop_task()
        for fun in self.__start_evts:
            (await fun(req, loop)) if asyncio.iscoroutinefunction(fun) else fun(req, loop)

    async def __before_server_stop(self, req, loop):
        for fun in self.__stop_evts:
            await fun(req, loop)

    @property
    def main(self):
        return self.__server

    def add_signal(self, signal_map: dict):
        """信号注册"""
        if not signal_map:
            return
        for k, v in signal_map.items():
            callable(v) and self.__server.add_signal(v, k)

    def add_start_event(self, events):
        if callable(events):
            self.__start_evts.append(events)
        if isinstance(events, (list, tuple)):
            self.__start_evts.extend(events)

    def add_stop_event(self, events):
        if callable(events):
            self.__stop_evts.append(events)
        if isinstance(events, (list, tuple)):
            self.__stop_evts.extend(events)

    def run(self, protocol=None):

        self.__server.run(
            host=self.__conf.HOST,
            port=self.__conf.RUN_PORT,
            workers=self.__conf.RUN_WORKER if not self.__conf.RUN_FAST else 1,
            fast=self.__conf.RUN_FAST,
            debug=self.__conf.DEBUG_MODE,
            access_log=self.__conf.ACCESS_LOG,
            protocol=protocol
        )
