from .utils import get_hash_key


# mysql 配置
class MysqlConfig:
    """
        :param mincached:连接池中空闲连接的初始数量
        :param maxcached:连接池中空闲连接的最大数量
        :param maxshared:共享连接的最大数量
        :param maxconnections:创建连接池的最大数量
        :param blocking:超过最大连接数量时候的表现，为True等待连接数量下降，为false直接报错处理
        :param maxusage:单个连接的最大重复使用次数
        :param setsession:optional list of SQL commands that may serve to prepare
            the session, e.g. ["set datestyle to ...", "set time zone ..."]
        :param reset:how connections should be reset when returned to the pool
            (False or None to rollback transcations started with begin(),
            True to always issue a rollback for safety's sake)
        :param host:数据库ip地址
        :param port:数据库端口
        :param db:库名
        :param user:用户名
        :param password:密码
        :param charset:字符编码
    """

    _instance = None
    _config_dict = {}

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def set_config(self, config_tag='', host='', db='', user='', password='', port='', charset='utf8mb4', min_cached=5,
                   max_cached=50, max_shared=0, max_connection=100, max_usage=100):
        config = {
            'host': host,
            'port': port,
            'db': db,
            'user': user,
            'password': password,
            'charset': charset,
            'minCached': min_cached,
            'maxCached': max_cached,
            'maxShared': max_shared,
            'maxConnection': max_connection,
            'maxUsage': max_usage,
            'blocking': True,
            'reset': True,
            'setSession': None,
        }

        config_hash_key = get_hash_key('%s_%s' % ('mysql_config_key', config_tag))
        self._config_dict[config_hash_key] = config

    def get_config(self, config_tag=''):
        config_hash_key = get_hash_key('%s_%s' % ('mysql_config_key', config_tag))
        return self._config_dict.get(config_hash_key, {})
