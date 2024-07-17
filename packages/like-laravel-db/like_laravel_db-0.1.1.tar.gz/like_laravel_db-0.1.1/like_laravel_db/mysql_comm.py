from timeit import default_timer
import pymysql
from dbutils.pooled_db import PooledDB
from .utils import get_hash_key
from .config import MysqlConfig


# 单例连接池
class MysqlPool:
    _instance = None
    __pool = {}

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def free(cls):
        cls._instance = None
        cls.__pool = {}

    def get_mysql_pool(self, config) -> PooledDB:
        """
        需要根据不同的配置 初始化不同的数据库连接池
        :param config:
        """
        obj_key = get_hash_key('%s_%s' % ('mysql_pool_key', config))
        if obj_key not in self.__pool:
            print('连接池: %s 初始化.' % obj_key)
            self.__pool[obj_key] = PooledDB(creator=pymysql,
                                            maxconnections=config['maxConnection'],
                                            mincached=config['minCached'],
                                            maxcached=config['maxCached'],
                                            maxshared=config['maxShared'],
                                            blocking=config['blocking'],
                                            maxusage=config['maxUsage'],
                                            setsession=config['setSession'],
                                            charset=config['charset'],
                                            host=config['host'],
                                            port=config['port'],
                                            database=config['db'],
                                            user=config['user'],
                                            password=config['password'],
                                            )
        return self.__pool[obj_key]


# 统计记录日志
class UsingMysql(object):
    def __init__(self, connect, commit=True, log_time=False, log_label='总用时'):
        self._connect = connect
        self._log_time = log_time
        self._commit = commit
        self._log_label = log_label

    def __enter__(self):
        # 如果需要记录时间
        if self._log_time is True:
            self._start = default_timer()
            self._conn_spent = 0

        # 在进入的时候自动获取连接和cursor
        mysql_config = MysqlConfig().get_config(self._connect)
        mysql_pool = MysqlPool().get_mysql_pool(mysql_config)
        conn = mysql_pool.connection()  # 通过数据连接池
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        conn.autocommit = False

        self._conn = conn
        self._cursor = cursor

        # 如果需要记录时间
        if self._log_time is True:
            self._get_conn_spent = default_timer() - self._start

        return self

    def __exit__(self, *exc_info):
        # 提交事务
        if self._commit:
            self._conn.commit()
        # 在退出的时候自动关闭连接和cursor
        self._cursor.close()
        self._conn.close()

        if self._log_time is True:
            spent = default_timer() - self._start
            print('-- %s: %.6f 秒(get_conn:%.6f)' % (self._log_label, spent, self._get_conn_spent))

    @property
    def cursor(self):
        return self._cursor
