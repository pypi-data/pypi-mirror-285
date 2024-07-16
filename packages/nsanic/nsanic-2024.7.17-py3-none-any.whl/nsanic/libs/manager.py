from typing import Union


class WsConnector:
    """Websocket连接管理器"""

    _WS_MAP = {}
    conf = None

    @classmethod
    def set_conf(cls, conf):
        cls.conf = conf

    @classmethod
    def all_ws(cls):
        return cls._WS_MAP.values()

    @classmethod
    def get_ws(cls, key: Union[str, int, bytes]):
        return cls._WS_MAP.get(key)

    @classmethod
    async def set_ws(cls, key: Union[str, int, bytes], ws, key_info: str):
        """更新连接，如果存在旧连接会关闭旧连接"""
        old_ws = cls.get_ws(key)
        cls._WS_MAP[key] = ws
        if old_ws:
            cls.conf and cls.conf.rds and await cls.conf.rds.drop_hash(
                cls.conf.WS_ONLINE_INFO, getattr(old_ws, 'uinfo', ''))
            await old_ws.close()
        cls.conf and cls.conf.rds and await cls.conf.rds.set_hash(cls.conf.WS_ONLINE_INFO, key, key_info)

    @classmethod
    async def close_ws(cls, key: Union[str, int, bytes], msg: Union[str, bytes] = None):
        ws = cls.get_ws(key)
        if ws:
            cls._WS_MAP.pop(key)
            msg and await ws.send(msg)
            await ws.close()
        cls.conf and cls.conf.rds and await cls.conf.rds.drop_hash(cls.conf.WS_ONLINE_INFO, key)

    @classmethod
    async def call_offline(cls, ukey: Union[int, str]):
        await cls.close_ws(ukey)


class HeaderSet:

    RESP_TYPE = {
        'JSON': 'application/json',
        'MSGPACK': 'text/msgpack',
        'TEXT': 'text/plain',
        'HTML': 'text/html',
        'PROTO': 'application/octet-stream',
    }

    @classmethod
    def out(cls, conf):
        tp = cls.RESP_TYPE.get(conf.RESP_TYPE)
        if not tp:
            raise Exception('无效的响应类型配置')
        if conf.RESP_TYPE != 'MSGPACK':
            tp += f';charset={conf.CHARSET}'
        headers = {
            'Content-Type': tp,
            'Access-Control-Allow-Methods': ','.join(conf.ALLOW_METHOD),
            'Access-Control-Max-Age': conf.ORIGIN_MAX_AGE,
            'Access-Control-Allow-Headers': '*' if '*' in conf.ALLOW_HEADER else ','.join(conf.ALLOW_HEADER),
            'Access-Control-Allow-Origin': '*' if '*' in conf.ALLOW_ORIGIN else ','.join(conf.ALLOW_ORIGIN),
            'Access-Control-Allow-Credentials': conf.ALLOW_CREDENTIALS
        }
        return headers
