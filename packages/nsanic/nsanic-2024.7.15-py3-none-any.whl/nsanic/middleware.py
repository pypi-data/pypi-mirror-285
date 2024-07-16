from sanic import Request, HTTPResponse

from nsanic.libs.component import ConfDI
from nsanic.libs.manager import HeaderSet


class CorsMiddle(ConfDI):

    @classmethod
    async def main(cls, req: Request):
        """通用跨域适配"""
        if req.method == 'OPTIONS':
            headers = HeaderSet.out(cls.conf)
            if ('*' not in cls.conf.ALLOW_ORIGIN) and (req.server_name not in cls.conf.ALLOW_ORIGIN):
                return HTTPResponse('', status=403, headers=headers)
            return HTTPResponse('', status=204, headers=headers)
