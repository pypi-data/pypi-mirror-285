from datetime import datetime, date
from typing import Union

from tortoise import Model, fields, transactions, connections
from tortoise.expressions import Q

from nsanic.libs import tool_dt
from nsanic.libs.consts import GLOBAL_TZ

GeneratorClass = None


class DBModel(Model):
    _SPLIT_TABLES = set()
    '''当前分表集合'''
    _SPLIT_SUFFIX = {1: 'str', 2: 'y%Y', 3: 'y%Ym%m', 4: 'y%Yw%w', 5: 'y%Ym%md%d'}
    '''表名后缀类型映射 1--自定义标记 2--按日期年标记 3--按日期年月标记 4--按日期年周标记 5--按日期年月日标记'''
    _split_type = 0
    '''分表模式 0--不分表 1--自定义标记分表 2--按年分表 3--按月分表 4--按周分表 5--按日分表'''
    _split_field = 'created'
    '''分表字段或标记字符串'''

    created = fields.BigIntField(null=True, index=True, default=0, description='创建时间')

    class Meta:
        abstract = True

    @classmethod
    def sheet_name(cls, suffix: Union[str, int, float, datetime, date] = None, tz: str = GLOBAL_TZ):
        """
        数据表名 
        :param suffix: 当前待设置的后缀或后缀数据
        :param tz: 指定按日期分表数据的时区
        """
        tb_name = cls._meta.db_table or cls.__name__.lower()
        if cls._split_type:
            if cls._split_type not in cls._SPLIT_SUFFIX:
                raise Exception('Invalid split table type.')
            if (cls._split_type == 1) or (isinstance(suffix, str)):
                tb_name = f"{tb_name}_{suffix}"
            else:
                fmt = cls._SPLIT_SUFFIX.get(cls._split_type)
                tb_name = f"{tb_name}_{tool_dt.dt_str(suffix, fmt=fmt, tz=tz)}"
        return tb_name

    @classmethod
    def pk_name(cls):
        return cls._meta.db_pk_column

    @classmethod
    def check_field(cls, field: str):
        return field in cls._meta.db_fields

    @classmethod
    def out_fields(cls, forbids: Union[list, tuple, set] = None):
        """禁止部分字段输出"""
        return [name for name in cls._meta.db_fields if name not in forbids] if forbids else cls._meta.db_fields

    @classmethod
    def get_meta_db(cls, db_key: str = None):
        if db_key:
            conn = connections.get(db_key)
            if not conn:
                raise Exception(f'Can not found {db_key} db config, please confirm the config is exist.')
        elif len(connections.db_config) == 1:
            db_key = next(iter(connections.db_config.keys()))
            conn = connections.get(db_key)
        else:
            return connections.get('default')
        if type(conn).__name__ == 'TransactionWrapper':
            return conn._parent
        return conn

    @classmethod
    def __check_orders(cls, orders: Union[str, list, tuple]):
        if orders:
            if isinstance(orders, str):
                orders = [orders]
            new_order = []
            for key in orders:
                key_str = key[1:] if key[0] in ('-', '+') else key
                (key_str in cls._meta.db_fields) and new_order.append(key)
            return new_order
        return []

    @classmethod
    def __fetch_generator_class(cls):
        global GeneratorClass
        if GeneratorClass:
            return GeneratorClass
        dialect = cls._meta.db.schema_generator.DIALECT
        if dialect == 'postgres':
            from nsanic.orm.pgsql_generator import PgSqlGenerator
            GeneratorClass = PgSqlGenerator
        elif dialect == 'mysql':
            from nsanic.orm.mysql_generator import MySqlGenerator
            GeneratorClass = MySqlGenerator
        elif dialect == 'mssql':
            from nsanic.orm.mssql_generator import MsSqlGenerator
            GeneratorClass = MsSqlGenerator
        return GeneratorClass

    @classmethod
    def get_tb_name(cls, tb_suffix: str):
        base_name = cls._meta.db_table or cls.__name__.lower()
        tb_name = f"{base_name}{tb_suffix}"
        return tb_name

    @classmethod
    def get_split_suffix(cls, split: Union[str, int, float, datetime, date], param: dict, tz: str = GLOBAL_TZ):
        """
        获取字典参数的分表后缀
        :param split: 分表标记或标记位数据
        :param param: 查询参数
        :param tz: 按日期分表数据的时区
        """
        if not cls._split_type:
            return ''
        if cls._split_type not in cls._SPLIT_SUFFIX:
            raise Exception('Invalid split table type.')
        if cls._split_type == 1:
            return f'_{split}'
        if not split:
            split = cls._split_field
        kval = (param.get(split) or param.get(f'{split}__gte') or param.get(f'{split}__lte')
                or param.get(f'{split}__gt') or param.get(f'{split}__lt')) or tool_dt.cur_time(tz=tz)
        return f'_{tool_dt.dt_str(kval, fmt=cls._SPLIT_SUFFIX.get(cls._split_type), tz=tz)}'

    @classmethod
    def gen_simple_query(
            cls,
            param: dict = None,
            field: Union[tuple, list, set] = None,
            exclude: Union[tuple, list, set] = None,
            groups: Union[str, list, tuple] = None,
            orders: Union[str, list, tuple] = None,
            limit=0,
            with_del=False,
            split: Union[str, int, float, datetime, date] = None,
            db_key: str = None,
            tz: str = GLOBAL_TZ):
        suffix = cls.get_split_suffix(split, param, tz=tz)
        db = cls.get_meta_db(db_key)
        cls._meta.db_table = cls._meta.basetable._table_name = cls.get_tb_name(suffix)
        q_set = cls.filter(sta_del=False).using_db(db) if (hasattr(cls, 'sta_del')) and (not with_del) else \
            cls.all(using_db=db)
        if param:
            q_set = q_set.filter(Q(**param))
        if groups:
            if isinstance(groups, str):
                groups = [groups]
            q_set = q_set.group_by(*groups)
        orders = cls.__check_orders(orders)
        if orders:
            q_set = q_set.order_by(*orders)
        out_field = [f for f in field if f in cls._meta.db_fields] if field else (
            [v for v in cls._meta.db_fields if v not in exclude] if exclude else [])
        if limit:
            q_set = q_set.limit(limit)
        return q_set, out_field

    @classmethod
    async def check_table(cls, tb_suffix: str, db_key: str = None):
        base_name = cls._meta.db_table or cls.__name__.lower()
        tb_name = f"{base_name}{tb_suffix}"
        db = cls.get_meta_db(db_key)
        if tb_name not in cls._SPLIT_TABLES:
            _creator = cls.__fetch_generator_class()
            if not _creator:
                raise Exception(f'未定义的表创建模式：{cls._meta.db.schema_generator.DIALECT}')
            cls._meta.db_table = tb_name
            _sql_dict = _creator(db).get_table_sql_new(cls)
            if not _sql_dict:
                raise Exception(f'无法生成建表模型：{_sql_dict}')
            sql = _sql_dict.get('table_creation_string')
            if not sql:
                raise Exception(f'无法生成创建表SQL：{_sql_dict}')
            await cls._meta.db.execute_script(sql)
            cls._SPLIT_TABLES.add(tb_name)
            cls._meta.db_table = base_name

    @classmethod
    async def fetch_on_page(
            cls,
            param: dict = None,
            page=1,
            size=20,
            field: Union[tuple, list, set] = None,
            exclude: Union[tuple, list, set] = None,
            groups: Union[str, list, tuple] = None,
            orders: Union[str, list, tuple] = '-created',
            split: Union[str, int, float, datetime, date] = None,
            with_count: int = 1,
            db_key: str = None,
            tz: str = GLOBAL_TZ):
        """
        简单分页查询
        :param param:字典形式的查询参数, __lte __gte 等可自行通过key构造
        :param page: 页数
        :param size: 分页大小
        :param field: 指定输出的字段（优先）
        :param exclude: 指定不输出的字段
        :param groups: 分组字段
        :param orders: 排序字段
        :param split: 分表标记 设置分表类型为1时生效，
        :param with_count: 是否进行数量查询 0-否 1-精确数量 2-模糊数量(针对大表)
        :param db_key: 采用的数据库配置
        :param tz: 指定按日期分表采用的时区
        """
        q_set, out_field = cls.gen_simple_query(
            param=param, field=field, exclude=exclude, groups=groups, orders=orders, split=split, db_key=db_key, tz=tz)
        if page < 1:
            page = 1
        offset = (page - 1) * size
        total = 0
        if with_count:
            total = await q_set.count()
        data_list = await q_set.limit(size).offset(offset).values(*out_field)
        return data_list, total

    @classmethod
    async def get_by_pk(
            cls,
            val: Union[int, str],
            field: Union[tuple, list] = None,
            exclude: Union[tuple, list] = None,
            split: Union[str, int, float, datetime, date] = None,
            db_key: str = None,
            tz: str = GLOBAL_TZ):
        """
        通过唯一主键查询
        :param val: 主键值
        :param field: 指定输出的字段
        :param exclude: 指定排除的字段
        :param split: 分表标记 设置分表类型为1时生效，
        :param db_key: 指定数据库配置名
        :param tz: 按日期分表时指定的时区
        """
        if not cls._meta.db_pk_column:
            raise Exception(f'Current sheet {cls.sheet_name()} has no set primary key')
        query_model, f_list = cls.gen_simple_query(
            {cls.pk_name(): val}, field=field, exclude=exclude, split=split, limit=1, db_key=db_key, tz=tz)
        info = await query_model.values(*f_list)
        return info[0] if info else None

    @classmethod
    async def get_by_dict(
            cls,
            param: dict = None,
            field: Union[tuple, list, set] = None,
            exclude: Union[tuple, list, set] = None,
            groups: Union[str, list, tuple] = None,
            orders: Union[str, list, tuple] = '-created',
            split: Union[str, int, float, datetime, date] = None,
            limit=0,
            db_key: str = None,
            tz: str = GLOBAL_TZ):
        query_model, out_filed = cls.gen_simple_query(
            param=param, field=field, exclude=exclude, groups=groups, orders=orders, split=split,
            limit=limit, db_key=db_key, tz=tz)
        dlist = await query_model.values(*out_filed)
        if limit == 1:
            return dlist[0] if dlist else None
        return dlist

    @classmethod
    async def get_count(
            cls,
            param: dict = None,
            with_del=False,
            split: Union[str, int, float, datetime, date] = None,
            db_key: str = None,
            tz: str = GLOBAL_TZ):
        query_model, _ = cls.gen_simple_query(param=param, with_del=with_del, split=split, db_key=db_key, tz=tz)
        return await query_model.count()

    @classmethod
    async def add_one(cls, param: dict, fun_success=None, db_key: str = None):
        """
        自动分表模式创建
        公共 新增或更新 值为None采用默认值

        :param param: 字典数据模型
        :param fun_success: 执行成功后的补充处理函数 协程函数 参数为生成的Model模型
        :param db_key: 指定数据库配置
        """
        if cls._split_type:
            raise Exception('分表模型不能使用该方式添加数据')
        cur_time = tool_dt.cur_time()
        param['created'] = cur_time
        ('updated' in cls._meta.db_fields) and param.update({'updated': cur_time})
        new_dict = {field: val for field, val in param.items() if (field in cls._meta.db_fields) and (val is not None)}
        if not new_dict:
            return None
        db = cls.get_meta_db(db_key)
        row = await cls.create(using_db=db, **new_dict)
        if row:
            callable(fun_success) and await fun_success(row)
            return row
        return None

    @classmethod
    async def update_by_pk(
            cls,
            pk_val: Union[int, str],
            param: dict,
            old_data: dict = None,
            fun_success=None,
            split: Union[str, int, float, datetime, date] = None,
            db_key: str = None,
            tz: str = GLOBAL_TZ):
        if not cls._meta.db_pk_column:
            raise Exception(f'Current sheet {cls.sheet_name()} has no set primary key')
        if not old_data:
            if fun_success:
                raise Exception(f'Must be get [old_data] param for execute the function')
            new_dict = {k: v for k, v in param.items() if (k in cls._meta.db_fields) and (v is not None)}
            split_param = {cls._split_field: split} if (cls._split_field not in param) else param
            suffix = cls.get_split_suffix(split, split_param, tz=tz)
        else:
            new_dict = {k: v for k, v in param.items() if (
                    (k in cls._meta.db_fields) and (v is not None)) and (old_data.get(k) != v)}
            split_param = {cls._split_field: split} if (cls._split_field not in old_data) else old_data
            suffix = cls.get_split_suffix(split, split_param, tz=tz)
        ('created' in new_dict) and new_dict.pop('created')
        if new_dict:
            ('updated' in cls._meta.db_fields) and new_dict.update({'updated': tool_dt.cur_time()})
            db = cls.get_meta_db(db_key)
            cls._meta.db_table = cls._meta.basetable._table_name = cls.get_tb_name(suffix)
            sta = await cls.filter(**{cls._meta.db_pk_column: pk_val}).using_db(db).limit(1).update(**new_dict)
            if sta:
                if callable(fun_success):
                    old_data.update(**new_dict)
                    await fun_success(old_data)
                return new_dict
            return False
        return None

    @classmethod
    async def update_by_cond(
            cls,
            param: dict,
            upinfo: dict,
            limit=1,
            split: Union[str, int, float, datetime, date] = None,
            fun_success=None,
            db_key: str = None,
            tz: str = GLOBAL_TZ):
        new_dict = {k: v for k, v in upinfo.items() if (k in cls._meta.db_fields) and (v is not None)}
        created = ('created' in new_dict) and new_dict.pop('created')
        if new_dict:
            ('updated' in cls._meta.db_fields) and new_dict.update({'updated': tool_dt.cur_time()})
            query_model, _ = cls.gen_simple_query(param, limit=limit, split=split, db_key=db_key, tz=tz)
            sta = await query_model.update(**new_dict)
            if sta:
                created and new_dict.update({'created': created})
                callable(fun_success) and await fun_success(new_dict)
                return new_dict
            return False
        return None

    @classmethod
    async def del_by_pk(
            cls,
            pk_val: Union[int, str],
            force=False,
            split: Union[str, int, float, datetime, date] = None,
            db_key: str = None,
            tz: str = GLOBAL_TZ,
            fun_success=None,
            fun_ags: Union[list, tuple] = None):
        if not cls._meta.db_pk_column:
            raise Exception(f'Current sheet {cls.sheet_name()} has no set primary key')
        if fun_ags is None:
            fun_ags = ()
        suffix = cls.get_split_suffix(split, {cls._split_field: split}, tz=tz)
        cls._meta.db_table = cls._meta.basetable._table_name = cls.get_tb_name(suffix)
        if (not hasattr(cls, 'sta_del')) or force:
            db = cls.get_meta_db(db_key)
            sta = await cls.filter(**{cls._meta.db_pk_column: pk_val}).using_db(db).limit(1).delete()
            if sta:
                callable(fun_success) and await fun_success(*fun_ags)
                return True
            return False
        db = cls.get_meta_db(db_key)
        sta = await cls.filter(**{cls._meta.db_pk_column: pk_val}).using_db(db).limit(1).update(sta_del=True)
        if sta:
            callable(fun_success) and await fun_success(*fun_ags)
            return True
        return False

    @classmethod
    async def del_by_cond(
            cls,
            param: dict,
            limit=1,
            force=False,
            split: Union[str, int, float, datetime, date] = None,
            db_key: str = None,
            tz: str = GLOBAL_TZ,
            fun_success=None,
            fun_ags: Union[list, tuple] = None):
        if fun_ags is None:
            fun_ags = ()
        query_model, _ = cls.gen_simple_query(param, limit=limit, with_del=force, split=split, db_key=db_key, tz=tz)
        if (not hasattr(cls, 'sta_del')) or force:
            sta = await query_model.delete()
            if sta:
                callable(fun_success) and await fun_success(*fun_ags)
                return True
            return False
        sta = await query_model.update(sta_del=True)
        if sta:
            callable(fun_success) and await fun_success(*fun_ags)
            return True
        return False

    @classmethod
    async def split_bulk_insert(
            cls,
            data: Union[list, tuple],
            split: Union[str, int, float, datetime, date] = None,
            db_key: str = None,
            tz: str = GLOBAL_TZ):
        if not cls._split_type:
            raise Exception(f'当前数据模型未指定分表模式：{cls.__name__}')
        model_map = {}
        for item in data:
            if isinstance(item, dict):
                (not item.get('created')) and item.update({'created': tool_dt.cur_time()})
                suffix = cls.get_split_suffix(split or cls._split_field, item, tz=tz)
                model_map[suffix].append(cls(**item)) if suffix in model_map else model_map.update(
                    {suffix: [cls(**item)]})
            else:
                (not getattr(item, 'created', None)) and setattr(item, 'created', tool_dt.cur_time())
                suffix = cls.get_split_suffix(
                    split or cls._split_field, {cls._split_field: getattr(item, cls._split_field, None)}, tz=tz)
                model_map[suffix].append(item) if suffix in model_map else model_map.update({suffix: [item]})
            await cls.check_table(suffix, db_key)
        db = cls.get_meta_db(db_key)
        async with transactions.in_transaction(db_key or 'default'):
            for k, v in model_map.items():
                cls._meta.db_table = cls._meta.basetable._table_name = cls.get_tb_name(k)
                await cls.bulk_create(v, using_db=db)

    @classmethod
    async def split_add_one(
            cls,
            data: dict,
            split: Union[str, int, float, datetime, date] = None,
            fun_success=None,
            db_key: str = None,
            tz: str = GLOBAL_TZ):
        if not cls._split_type:
            raise Exception(f'当前数据模型未指定分表模式：{cls.__name__}')
        new_d = {field: val for field, val in data.items() if (field in cls._meta.db_fields) and (val is not None)}
        if not new_d:
            return None
        (not new_d.get('created')) and new_d.update({'created': tool_dt.cur_time()})
        suffix = cls.get_split_suffix(split or cls._split_field, data, tz=tz)
        await cls.check_table(suffix, db_key)
        db = cls.get_meta_db(db_key)
        cls._meta.db_table = cls._meta.basetable._table_name = cls.get_tb_name(suffix)
        row = await cls.create(using_db=db, **new_d)
        if row:
            callable(fun_success) and await fun_success(row)
            return row
        return None
