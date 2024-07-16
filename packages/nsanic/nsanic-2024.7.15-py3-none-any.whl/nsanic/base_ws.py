import asyncio
import os
import traceback
from asyncio import queues
from typing import Union

from sanic import Request
from sanic.exceptions import WebsocketClosed
from sanic.server.protocols.websocket_protocol import WebSocketProtocol

from nsanic.libs import tool, tool_ws, tool_dt
from nsanic.libs.component import ConfDI
from nsanic.libs.manager import WsConnector


class BaseWsView(ConfDI):
    off_queue = queues.Queue()
    '''掉线玩家队列'''
    CMD_MAP = {}
    '''服务命令映射'''
    ws_manager = WsConnector

    dft_type: Union[int, str] = 1
    '''系统默认消息类型'''
    beat_code: Union[int, str] = 1
    '''心跳消息标码'''
    reject_code: Union[int, str] = 2
    '''弹回消息标码'''
    max_history_queue = 100
    '''最大历史消息数量'''
    delay_fail = 5
    '''授权或无效连接响应延时（秒）降低无效连接资源反复创建的开销'''

    def __init__(self):
        self.ws_manager.set_conf(self.conf)
        self.CMD_MAP = {k: v(self.conf, k) for k, v in self.CMD_MAP.items()}
        self.fun_pack_msg: callable = tool_ws.pack_msg
        self.fun_parse_msg: callable = tool_ws.parse_msg
        self.delay_pre = round(self.delay_fail * 0.6, 2)
        self.delay_aft = round(self.delay_fail * 0.4, 2)

    @classmethod
    def init_ws(cls):
        return cls()

    @property
    def channel(self):
        return f'PUBSUB_{self.conf.SERVER_NAME.upper()}_{self.conf.SERVER_ID.upper()}_{os.getpid()}'

    def history_queue(self, uid: int):
        return f'HISTORY_MSG_{self.conf.SERVER_ID.upper()}_{uid}'

    @staticmethod
    def get_ukey(uinfo):
        return uinfo.get('uid') or uinfo.get('id') or uinfo.get('userid') if isinstance(uinfo, dict) else uinfo

    def init_loop_task(self):
        loop = asyncio.get_running_loop()
        loop.create_task(self.listen_offline_queue())

    async def listen_offline_queue(self):
        while 1:
            off_ws = await self.off_queue.get()
            if off_ws and hasattr(off_ws, 'uinfo'):
                u_key = off_ws.uinfo
                cur_ws = self.ws_manager.get_ws(u_key)
                if cur_ws and (cur_ws.ws_proto.id == off_ws.ws_proto.id):
                    await self.ws_manager.call_offline(u_key)
                for k, v in self.CMD_MAP.items():
                    try:
                        await v.off_line(u_key)
                    except Exception as err:
                        self.log.error(f'用户掉线处理出错：{u_key}, {err}')

    async def client_listen(self, ws, uinfo):
        while 1:
            c_type, c_code, data, extra = self.fun_parse_msg(await ws.recv(), log_fun=self.log.error)
            if c_type and (c_type == self.dft_type) and (c_code == self.beat_code):
                await ws.send(self.fun_pack_msg(
                    self.dft_type, self.beat_code, data=data, code=self.conf.STA_CODE.PASS, req=extra))
                continue
            fun = self.CMD_MAP.get(c_type)
            if fun and callable(fun.funapi):
                msg_arr = None
                try:
                    msg_arr = await fun.funapi(c_code, uinfo, data)
                    await ws.send(self.fun_pack_msg(c_type, *msg_arr, req=extra))
                except WebsocketClosed:
                    msg_arr and await self.save_as_history(uinfo, self.fun_pack_msg(c_type, *msg_arr, req=extra))
                    return await self.ws_manager.call_offline(self.get_ukey(uinfo))
                except Exception as err:
                    msg_arr and await self.save_as_history(uinfo, self.fun_pack_msg(c_type, *msg_arr, req=extra))
                    self.log.error(f'{err}:{traceback.format_exc()}')
                    await ws.send(self.fun_pack_msg(
                        c_type, c_code, code=self.conf.STA_CODE.FAIL, req=extra, hint='A error cause failed'))
            else:
                await ws.send(self.fun_pack_msg(
                    self.dft_type, self.reject_code, code=self.conf.STA_CODE.FAIL, hint='Unspecified message'))

    async def wsrouter(self, req: Request, ws):
        """Websocket路由服务"""
        uinfo = await self.wsauth(req, ws)
        if not uinfo:
            self.delay_aft and (await asyncio.sleep(self.delay_aft))
            return await ws.close()
        if not await self.check_ws_conn(uinfo, req, ws):
            self.delay_aft and (await asyncio.sleep(self.delay_aft))
            return await ws.close()
        await self.update_status(uinfo)
        await self.filter_history_msg(ws, uinfo)
        await self.client_listen(ws, uinfo)

    async def save_as_history(self, uinfo, msg):
        """处理未发送成功的消息"""
        if not isinstance(msg, str):
            msg = tool.json_encode(msg, u_byte=True)
        if msg:
            ukey = self.get_ukey(uinfo)
            key_name = self.history_queue(ukey)
            await self.rds.lqpush(key_name, [msg])
            if await self.rds.qlen(key_name) > self.max_history_queue:
                _ = await self.rds.rqpop(key_name)

    async def filter_history_msg(self, ws, uinfo):
        ukey = self.get_ukey(uinfo)
        msg_list = await self.rds.qrpop(self.history_queue(ukey), count=self.max_history_queue)
        if not msg_list:
            return
        if isinstance(msg_list, str):
            msg_list = [msg_list]
        for msg in msg_list:
            if msg:
                try:
                    await ws.send(msg)
                except Exception as err:
                    self.log.error(f'推送历史消息失败，重新入队: {err}')
                    await self.save_as_history(ukey, msg)
                    break

    async def check_ws_conn(self, uinfo, req, ws):
        timestamp = req.headers.get('Timestamp') or req.args.get('Timestamp')
        if not timestamp:
            self.delay_pre and (await asyncio.sleep(self.delay_pre))
            await ws.send(self.fun_pack_msg(
                self.dft_type, self.reject_code, code=self.conf.STA_CODE.FAIL, hint='missing params,reject'))
            return
        ukey = self.get_ukey(uinfo)
        timestamp = int(timestamp)
        if timestamp > int(tool_dt.cur_dt().timestamp()):
            self.delay_pre and (await asyncio.sleep(self.delay_pre))
            await ws.send(self.fun_pack_msg(
                self.dft_type, self.reject_code, code=self.conf.STA_CODE.FAIL, hint='error params,reject'))
            return
        old_info = await self.rds.get_hash(self.conf.WS_ONLINE_INFO, ukey)
        if old_info:
            old_arr = old_info.split(b'--' if isinstance(old_info, bytes) else '--')
            if int(old_arr[1]) >= timestamp:
                self.delay_pre and (await asyncio.sleep(self.delay_pre))
                await ws.send(self.fun_pack_msg(
                    self.dft_type, self.reject_code, code=self.conf.STA_CODE.FAIL, hint='invalid connection,reject'))
                return
        setattr(ws, 'uinfo', ukey)
        await self.ws_manager.set_ws(ukey, ws, f'{self.channel}--{timestamp}')
        return True

    async def update_status(self, uinfo):
        """更新用户监听的频道信息 更新连接状态等相关内容写在这里"""
        pass

    async def wsauth(self, req, ws) -> (object, dict, str, int):
        """基础接口认证处理 接入/认证等"""
        print(ws, req)
        raise Exception(f'接口未指定授权，不允许访问,当前监听：{self.channel}')
        pass


class RdsWS(BaseWsView):

    def __init__(self):
        super().__init__()

    def init_loop_task(self):
        loop = asyncio.get_running_loop()
        loop.create_task(self.__init_rds_listen())
        loop.create_task(self.listen_offline_queue())

    async def __init_rds_listen(self):
        try:
            sub_obj = await self.rds.pub_sub([self.channel, self.conf.CHANNEL_SYSTEM])
        except Exception as err:
            self.log.error(f'{self.channel}订阅消息频道出错,5秒后即将重启监听任务：{err}')
            await asyncio.sleep(5)
            return self.init_loop_task()
        while 1:
            try:
                t, c, m = await sub_obj.parse_response()
            except Exception as err:
                self.log.error(f'{self.channel}监听任务出错,10秒后即将重启监听任务：{err}')
                await asyncio.sleep(10)
                break
            if t == 'message':
                if c == self.channel:
                    arg = self.parse_channel_msg(m)
                    arg and (await self.on_receive_channel_msg(*arg))
                    continue
                if c == self.conf.CHANNEL_SYSTEM:
                    arg = self.parse_channel_msg(m)
                    arg.pop(-1)
                    await self.on_receive_channel_msg(*arg, receiver=-1)
                    continue
        # 监听失败 5秒后重启监听任务
        await asyncio.sleep(5)
        self.init_loop_task()

    @staticmethod
    def parse_channel_msg(msg: str):
        """通道监听消消息解析 如有需要可重写"""
        msg = tool.json_parse(msg)
        if (not msg) or not (isinstance(msg, dict)):
            return
        c_type, c_code, data, u = msg.get('t'), msg.get('c'), msg.get('d'), (msg.get('u') or -1)
        if not c_type:
            return
        return [c_type, c_code, data, u]

    async def on_receive_channel_msg(self, c_type: Union[int, str], c_code, data, receiver):
        """接收处理指定频道的订阅消息"""
        if not receiver:
            return
        if receiver == -1:
            for ws in self.ws_manager.all_ws():
                try:
                    ws and (await ws.send(
                        self.fun_pack_msg(c_type, c_code, data=data, code=self.conf.STA_CODE.PASS)))
                except Exception as err:
                    self.log.info(f'公共消息推送失败：{err}')
                    pass
            return
        ws = self.ws_manager.get_ws(receiver)
        if not ws:
            return await self.save_as_history(
                receiver, self.fun_pack_msg(c_type, c_code, data=data, code=self.conf.STA_CODE.PASS))
        try:
            return await ws.send(self.fun_pack_msg(c_type, c_code,  data=data, code=self.conf.STA_CODE.PASS))
        except Exception as err:
            self.log.info(f'发送目标消息失败,receiver:{receiver},data:{data},错误信息：{err}')
        return await self.save_as_history(
            receiver, self.fun_pack_msg(c_type, c_code, data=data, code=self.conf.STA_CODE.PASS))


class WsProtocol(WebSocketProtocol):

    def connection_lost(self, exc):
        async def to_queue(ws):
            await RdsWS.off_queue.put(ws)

        super(WsProtocol, self).connection_lost(exc)
        if self.websocket is not None:
            loop = asyncio.get_running_loop()
            loop.create_task(to_queue(self.websocket))
