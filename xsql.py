# coding:utf-8

def _check_args(func):
    def wrapper(self, *args, **kwargs):
        if args[0].count("%s") != len(args)-1:
            raise Exception("not match key:" + args[0])
        return func(self, *args, **kwargs)
    return wrapper

class Sql(object):

    OP_INSERT = 1
    OP_UPDATE = 2
    OP_DEL = 3
    OP_QUERY = 4
    PLACEHOLDER = "%s"  # 普通变量使用占位符 where("a=%s",1)
    PLACEHOLDER_IN = "(%s)"  # 数组变量站位符 where("a in (%s)", [1,2,3]) 

    def __init__(self, table_name):
        self.__tab_name = table_name
        self.__fields = []
        self.__wheres = []
        self.__values = []
        self.__updates = []
        self.__args = []
        self.__op = Sql.OP_QUERY #
        self.__sql = "" 
    
    def fields(self, *select_fields):
        self.__fields = select_fields
        return self

    def where(self, key, *values):
        return self.__where_with_condition("AND", key, values)

    def where_or(self, key, *values):
        return self.__where_with_condition("OR", key, values)

    def values(self, *values):
        self.__op = Sql.OP_INSERT
        if len(values) != len(self.__fields):
            raise Exception("not match values and fields")
        arr = []
        for v in values:
            if isinstance(v,(int, float)):
                arr.append(str(v))
            else:
                arr.append("%s")
                self.__args.append(v)
        self.__values.append("({})".format(",".join(arr)))
        return self

    def update(self, key, value=None):
        self.__op = Sql.OP_UPDATE
        if isinstance(value, (int, float)):
            key = key.replace(self.PLACEHOLDER, str(value))
        elif value:
            self.__args.append(value)
        self.__updates.append(key)
        return self

    def sql(self):
        if self.__sql:
            return self.__sql, self.__args
        sql_str = ""
        args = []
        if self.__op == Sql.OP_QUERY:
            sql_str, args = self._query_str()
        elif self.__op == Sql.OP_INSERT:
            sql_str, args = self._insert_str()
        elif self.__op == Sql.OP_UPDATE:
            sql_str, args = self._update_str()
        self.__sql = sql_str
        return sql_str,args

    def _update_str(self):
        sql = "UPDATE {} SET ".format(self.__tab_name) + ",".join(self.__updates)
        if len(self.__wheres) == 0:
            return sql, self.__args
        sql += " WHERE"
        for v in self.__wheres:
            sql += v[0]
            self.__args.extend(v[1])
        return sql, self.__args

    def _query_str(self):
        if len(self.__fields) == 0:
            self.__fields = ["*"]
        sql = "SELECT {} FROM {} ".format(",".join(self.__fields), self.__tab_name)
        if len(self.__wheres) == 0:
            return sql, self.__args
        sql += "WHERE"
        for v in self.__wheres:
            sql += v[0]
            self.__args.extend(v[1])
        return sql, self.__args
    
    def _insert_str(self):
        sql = "INSERT INTO {}({}) VALUES".format(self.__tab_name, ",".join(self.__fields))
        sql += ",".join(self.__values)
        return sql, self.__args

    @classmethod
    def __match_key_with_in(cls, key, count):
        arr = ["%s" for i in range(count)]
        return key.replace(cls.PLACEHOLDER_IN, "({})".format(",".join(arr)), 1)

    @classmethod
    def __match_key_value(cls, key, value):
        key = key
        values = []
        if isinstance(value, (int, float)):
            key = key.replace(cls.PLACEHOLDER, str(value), 1)
        elif isinstance(value, str):
            values.append(value)
        elif isinstance(value, (list, tuple)):
            key = cls.__match_key_with_in(key, len(value))
            for v in value:
                key, sub_values = cls.__match_key_value(key, v)
                values.extend(sub_values)
        return key, values

    def __where_with_condition(self,condition, key, *values):
        new_values = []
        for v in values:
            key, sub_values = self.__match_key_value(key, v)
            new_values.extend(sub_values)
        if len(self.__wheres) == 0:
            self.__wheres.append((' (' + key + ')', new_values))
        else:
            self.__wheres.append((' ' + condition +' (' + key + ')', new_values))
        return self

if __name__ == '__main__':
    s = Sql("test").update("a=%s", 5).where("c=%s",1).where_or("d=%s","111")
    print(s.sql()[0])
    print(s.sql()[1])
    



