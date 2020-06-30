import mysql.connector


class MyDb():

    VERSION = '2019-10-31 14:44:03@xj'

    def __init__(self, table_name):
        if table_name == '':
            raise ValueError('table name is must')
        else:
            self.conn     = mysql.connector.connect(host='192.168.0.178', user='root', password='root', database='test');
            self.table    = table_name
            self.cursor   = self.conn.cursor()
            self.init_key()
            self.columns  = self.get_columns()
            self.last_sql = None
    
    def init_key(self):
        self.limitSql = ''
        self.orderSql = ''
        self.key_word = ''
    
    def get_columns(self):
        sql = "SELECT column_name FROM information_schema.columns WHERE table_name='{}'".format(self.table)
        self.cursor.execute(sql)
        res = self.cursor.fetchall()
        self.columns = []
        for info in res:
            self.columns.append(info[0])
        return self.columns
    
    def add(self, data, check_filed=''):
        filed = []
        res = []
        for key in data.keys():
            filed.append(key)
            res.append(data[key])
        filed_str = ''
        res_str = ''
        for i in range(len(filed)):
            if i == len(filed)-1:
                filed_str = '{}{}'.format(filed_str, filed[i])
                res_str = '{}"{}"'.format(res_str, res[i])
            else:
                filed_str = '{}{}{}'.format(filed_str, filed[i], ',')
                res_str = '{}{}{}{}{}'.format(res_str, '"', res[i], '"', ',')
        if check_filed == '':
            try:
                self.exec_sql( "INSERT INTO {} ({}) values ({})".format( self.table, filed_str, res_str ), True )
            except:
                print('err')
            else:
                print("insert into {} ({}) values ({})".format(self.table,filed_str,res_str))
                # self.conn.commit()
        else:   # 需要检查字段是否唯一
            filter = {}
            filter[check_filed] = data[check_filed]
            if not self.where(filter).select():
                try:
                    self.exec_sql("INSERT INTO {} ({}) values ({})".format(self.table,filed_str,res_str),True)
                except:
                    print('add err')
                else:
                    print("insert success")
                    # self.conn.commit()
            else:
                print('exists')
        
    def exec_sql(self, sql, commit=False):
        try:
            self.cursor.execute(sql)
        except:
            return False
        else:
            if commit:
                self.conn.commit()
            self.last_sql = sql
            return self.cursor.rowcount
    
    def select(self, *args):
        if len(args) > 0:
            columns = ''
            for i in range( len(args) ):
                columns = columns + args[i]
                if i < len(args)-1:
                    columns = columns + ','
        else:
            raise Exception('key word is empty!')
        sql = "SELECT {} FROM {}".format( columns, self.table ) + self.analyzeKeyWord()
        if self.orderSql != '':
            sql = sql + self.orderSql
        if self.limitSql != '':
            sql = sql + self.limitSql
        self.last_sql = sql
        self.cursor.execute(sql)
        self.init_key()
        res = self.cursor.fetchall()
        if len(res) > 0:
            return res
        else:
            return False

    def close(self):
        self.cursor.close()
        self.conn.close()
    
    def where(self, data):
        self.key_word = data
        return self    
    
    def analyzeKeyWord(self):
        if not self.key_word:
            sql = ''
        else:
            if isinstance(self.key_word, dict):
                sqls = []
                for key in self.key_word:
                    sqls.append("{}='{}'".format(key, self.key_word[key]))
                sql = ' WHERE '
                for i in range(len(sqls)):
                    sql = "{}{}".format(sql, sqls[i])
                    if i < len(sqls)-1:
                        sql = "{} AND ".format(sql)
            elif isinstance(self.key_word, str):
                sql = " {} {}".format('WHERE', self.key_word)
        return sql
    
    def delete(self):
        if self.analyzeKeyWord() == '':
            print("can't delete all")
        else:
            sql = 'DELETE FROM {} '.format(self.table) + self.analyzeKeyWord()
            self.exec_sql(sql, True)
            self.init_key()
        
    def analyzeData(self, data):
        sqls = []
        sql = ''
        for key in data:
            sqls.append("{}='{}'".format(key, data[key]))
        for i in range(len(sqls)):
            sql = "{}{}".format(sql, sqls[i])
            if i < len(sqls)-1:
                sql = "{}{}".format(sql, ',')
        return sql
    
    def update(self, data):
        if not self.key_word:
            return False
            self.init_key()
        else:
            sql='UPDATE {} SET {} '.format(self.table, self.analyzeData(data)) + self.analyzeKeyWord()
            self.init_key()
            return self.exec_sql(sql, True)
    
    def orderby(self, str1):
        if str1 != '':
            self.orderSql = " ORDER BY {}".format(str1)
        return self
    
    def limit(self, start, end=''):
        if end == '':
            self.limitSql = ' LIMIT {}'.format(start)
        else:
            self.limitSql = ' LIMIT {},{}'.format(start, end)
        return self


class Image(MyDb):
    def __init__(self):
        super().__init__('think_image')


class Title(MyDb):
    def __init__(self):
        super().__init__('think_title')


class Work(MyDb):
    def __init__(self):
        super().__init__('think_work')


class User(MyDb):
    def __init__(self):
        super().__init__('think_user')


class Content(MyDb):
    def __init__(self):
        super().__init__('think_content')
