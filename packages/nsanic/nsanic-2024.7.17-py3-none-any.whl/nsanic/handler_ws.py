from typing import Union

from nsanic.exception import WsRpsMsg
from nsanic.base_conf import BaseConf
from nsanic.libs.component import ConfDI
from nsanic import verify
from nsanic.libs.consts import Code


class WsHandler(ConfDI):
    CMD_FUN_MAP = {}

    def __init__(self, conf: BaseConf, cmd_type: int):
        self.conf = conf
        self.__cmd_type = cmd_type

    @property
    def cmd_type(self):
        return self.__cmd_type

    async def funapi(self, cmd, uinfo, data):
        fun = self.CMD_FUN_MAP.get(cmd)
        if fun:
            try:
                data = await fun(uinfo, data)
            except WsRpsMsg as msg:
                return cmd, msg.data, msg.code, msg.hint
            else:
                return cmd, data, self.sta_code.FAIL, ''
        return cmd, None, self.conf.STA_CODE.FAIL, 'unspecified message.'

    async def off_line(self, ukey: Union[int, str]):
        """掉线处理逻辑"""
        pass

    def sendmsg(self, code: Code = None, data: Union[dict, list] = None, hint='success'):
        if not code:
            code = self.sta_code.PASS
        raise WsRpsMsg(code, data, hint=hint)

    def vf_str(self, val, require=False, default='', turn=0, minlen: int = None, maxlen: int = None, p_name=''):
        sta, val_info = verify.vstr(
            val, require=require, default=default, turn=turn, minlen=minlen, maxlen=maxlen, p_name=p_name)
        return val_info if sta else self.sendmsg(code=self.conf.STA_CODE.ERR_ARG, hint=val_info)

    def vf_int(self, v, require=False, default=0, minval: int = None, maxval: int = None, inner=True, p_name=''):
        sta, val_info = verify.vint(
            v, require=require, default=default, minval=minval, maxval=maxval, inner=inner, p_name=p_name)
        return val_info if sta else self.sendmsg(code=self.conf.STA_CODE.ERR_ARG, hint=val_info)

    def vf_float(self, val, require=False, default=None, keep_val=3, minval: float or int = None,
                 maxval: float or int = None, inner=True, p_name=''):
        sta, val_info = verify.vfloat(
            val, require=require, default=default, keep_val=keep_val, minval=minval, maxval=maxval,
            inner=inner, p_name=p_name)
        return val_info if sta else self.sendmsg(code=self.conf.STA_CODE.ERR_ARG, hint=val_info)

    def vf_time(self, val, require=False, default=None, time_min=None, time_max=None, inner=True, p_name=''):
        sta, val_info = verify.vdatetime(
            val, require=require, default=default, time_min=time_min, time_max=time_max, inner=inner, p_name=p_name)
        return val_info if sta else self.sendmsg(code=self.conf.STA_CODE.ERR_ARG, hint=val_info)
