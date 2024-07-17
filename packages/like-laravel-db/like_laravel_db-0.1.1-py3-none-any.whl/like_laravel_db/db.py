from .mysql_comm import UsingMysql


def check_multi_list(check_list):
    if type(check_list) != list:
        return 0
    if type(check_list[0]) == list:
        return 2
    return 1


def check_field_need_escape(field_val):
    ignore_list = ['as', 'count(', 'COUNT(']
    return any(ignore_str in field_val for ignore_str in ignore_list)


def escape_name(field_val):
    if check_field_need_escape(field_val):
        return field_val
    field_val = field_val.replace('`', '', -1)
    sl = field_val.split('.')
    nl = []
    for s in sl:
        nl.append('`%s`' % s)
    return '.'.join(nl)


def escape_name_list(field_val_list):
    rl = []
    for field_val in field_val_list:
        rl.append(escape_name(field_val))
    return rl


def raw_sql(sql, connect=''):
    with UsingMysql(connect) as um:
        um.cursor.execute(sql)
        data = um.cursor.fetchall()
        return data


def quo_filter(sql_str):
    if type(sql_str) == str:
        return sql_str.replace('\'', '\\\'').replace('\"', '\\\"')
    return sql_str


class DB(object):
    last_sql = ''

    def __init__(self):
        self._connect = ''
        self._table_name = ''
        self._where = []
        self._or_where = []
        self._limit = 0
        self._offset = 0
        self._select = []
        self._join = []
        self._order_by = []
        self._group_by = ''
        self._last_sql = ''

    def table(self, table_name):
        self._table_name = escape_name(table_name)
        return self

    def connect(self, connect):
        """
        对应不同mysql配置节点 默认为newlaw
        :param connect:
        :return:
        """
        self._connect = connect
        return self

    def where(self, where):
        if check_multi_list(where) == 2:
            self._where = self._where + where
        else:
            self._where.append(where)
        return self

    def or_where(self, where):
        if check_multi_list(where) == 2:
            self._or_where = self._or_where + where
        else:
            self._or_where.append(where)
        return self

    def limit(self, limit):
        self._limit = limit
        return self

    def offset(self, offset):
        self._offset = offset
        return self

    def select(self, select):
        if type(select) == list:
            self._select = escape_name_list(select)
        return self

    def group_by(self, group_field):
        if group_field:
            self._group_by = group_field
        return self

    def join(self, join_table, join_field1, operator, join_field2):
        self._join_common('JOIN', join_table, join_field1, operator, join_field2)
        return self

    def left_join(self, join_table, join_field1, operator, join_field2):
        self._join_common('LEFT JOIN', join_table, join_field1, operator, join_field2)
        return self

    def _join_common(self, join_type, join_table, join_field1, operator, join_field2):
        format_params = (
            join_type, escape_name(join_table), escape_name(join_field1), operator, escape_name(join_field2))
        join_str = '%s %s ON %s %s %s' % format_params
        self._join.append(join_str)

    def order_by(self, field_name, order_type='ASC'):
        self._order_by.append('%s %s' % (escape_name(field_name), order_type))
        return self

    def _get_where_common(self, operation_type='AND'):
        return_list = []
        where_list = self._where if operation_type == 'AND' else self._or_where
        for w in where_list:
            if type(w) == str:
                return_list.append('(%s)' % (w,))
            if type(w) == list:
                if len(w) == 1:
                    return_list.append('(%s)' % (w[0],))
                if len(w) == 2:
                    return_list.append("(%s = '%s')" % (w[0], quo_filter(w[1])))
                if len(w) == 3:
                    if w[1] in ['in', 'not in']:
                        return_list.append("(%s %s %s)" % (w[0], w[1], w[2]))
                    else:
                        return_list.append("(%s %s '%s')" % (w[0], w[1], quo_filter(w[2])))
        join_s = ' %s ' % operation_type
        return join_s.join(return_list)

    def _get_where_str(self):
        and_where_str = self._get_where_common('AND')
        or_where_str = self._get_where_common('OR')

        where_str = []
        if and_where_str:
            where_str.append('(%s)' % and_where_str)
        if or_where_str:
            where_str.append('(%s)' % or_where_str)
        return ' AND '.join(where_str)

    def _get_table_str(self, is_count=False):
        if self._table_name == '':
            return ''

        if is_count:
            select_str = 'count(*) as count'
        elif len(self._select) > 0:
            select_str = ','.join(self._select)
        else:
            select_str = '*'

        return 'SELECT %s FROM %s %s' % (select_str, self._table_name, ' , '.join(self._join))

    def _get_group_by_str(self):
        if len(self._group_by) == 0:
            return ''
        return 'GROUP BY %s' % self._group_by

    def _get_limit_str(self, is_first=False):
        if is_first:
            self._limit = 1
        elif self._limit == 0:
            return ''
        return 'LIMIT %s OFFSET %s' % (self._limit, self._offset)

    def _get_order_by_str(self):
        if len(self._order_by) == 0:
            return ''
        return 'ORDER BY %s' % ','.join(self._order_by)

    def _get_sql_str(self, is_first=False, is_count=False):
        table_str = self._get_table_str(is_count)
        if table_str == '':
            return ''

        where_str = self._get_where_str()
        if where_str:
            where_str = ' WHERE %s' % where_str

        group_str = self._get_group_by_str()
        limit_str = self._get_limit_str(is_first)
        order_by_str = self._get_order_by_str()

        return '%s %s %s %s %s' % (table_str, where_str, group_str, order_by_str, limit_str)

    def first(self, is_first=True, is_count=False):
        with UsingMysql(self._connect) as um:
            sql = self._get_sql_str(is_first, is_count)
            if sql == '':
                return {}
            # print(sql)
            DB.last_sql = sql
            um.cursor.execute(sql)
            data = um.cursor.fetchone()
            return data if data else {}

    def count(self):
        data = self.first(is_first=True, is_count=True)
        return data.get('count', 0)

    def all(self):
        with UsingMysql(self._connect) as um:
            sql = self._get_sql_str()
            if sql == '':
                return []
            # print(sql)
            DB.last_sql = sql
            um.cursor.execute(sql)
            data = um.cursor.fetchall()
            return data if data else []
