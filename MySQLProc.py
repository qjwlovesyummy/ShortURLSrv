import pymysql
import LogProc as log
import Const


host = '101.132.67.39'
port = 3306
user = 'root'
passwd = '19930423Love'
dbname = 'shorturlsrv'


class MySQLClient(object):

    def __init__(self, timeout=10, autocommit=True):
        try:
            self.dbc = pymysql.connect(host=host, port=port, user=user, passwd=passwd,
                                       db=dbname, cursorclass=pymysql.cursors.DictCursor, connect_timeout=timeout)
            self.autocommit = autocommit
            self.dbc.autocommit(self.autocommit)
        except Exception as ex:
            log.WriteLogMsg(log.LogType.LogEXCEPTION, 'MySQL DB connect failed, Exception: ' + str(ex))
            self.dbc = None

    def __enter__(self):
        try:
            if not self.dbc:
                self.cursor = None
            else:
                self.cursor = self.dbc.cursor()
            return self if self.cursor else None
        except Exception as ex:
            log.WriteLogMsg(log.LogType.LogEXCEPTION, ' get MySQL cursor failed, Exception: ' + str(ex))
            return None

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.dbc:
            self.dbc.close()

    def executenonquery(self, sql, args=None):
        '''
        execute sql
        :param sql: sql
        :param args: arguments
        :return: affected row number
        '''
        try:
            if sql == '':
                return 0
            if not self.cursor:
                return 0

            if args is None:
                rownum = self.cursor.execute(sql)
            else:
                rownum = self.cursor.execute(sql, args)
            return rownum
        except Exception as ex:
            log.WriteLogMsg(log.LogType.LogEXCEPTION, 'Execute SQL failed, Exception: ' + str(ex))
            return -1

    def executequery(self, sql, args=None):
        '''
        get data with sql
        :param sql: sql
        :param args: arguments
        :return: list of data
        '''
        try:
            if sql == '':
                return None
            if not self.cursor:
                return None

            if args is None:
                self.cursor.execute(sql)
            else:
                self.cursor.execute(sql, args)
            ret = self.cursor.fetchall()

            return ret
        except Exception as ex:
            log.WriteLogMsg(log.LogType.LogEXCEPTION, 'Execute SQL failed, Exception: ' + str(ex))
            return None

    def commit(self):
        '''
        transaction commit
        :return: None
        '''
        if self.autocommit:
            return

        if self.dbc and self.cursor:
            self.dbc.commit()
            return

    def rollback(self):
        '''
        transaction commit
        :return: None
        '''
        if self.autocommit:
            return

        if self.dbc and self.cursor:
            self.dbc.rollback()
            return
