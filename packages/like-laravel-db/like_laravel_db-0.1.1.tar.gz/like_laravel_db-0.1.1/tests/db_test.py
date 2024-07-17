import sys

sys.path.append("../")
import unittest
from like_laravel_db import db, config


class DbTestCase(unittest.TestCase):
    def test_first(self):
        config.MysqlConfig().set_config(host='127.0.0.1', port=3309, user='viewonly', password='686GTjkf9966',
                                        db='newlaw')
        print(db.DB().table('tax').first())

    def test_conn(self):
        config.MysqlConfig().set_config(config_tag='newlaw', host='127.0.0.1', port=3309, user='viewonly',
                                        password='686GTjkf9966', db='newlaw')
        config.MysqlConfig().set_config(config_tag='migration', host='10.123.4.218', port=3306, user='viewonly',
                                        password='686GTjkf9966', db='migration')
        print(db.DB().connect('newlaw').table('tax').first())
        print(db.DB().connect('migration').table('other_attached').first())
