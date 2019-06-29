import MySQLProc as mysql
import LogProc as log
import Const
from datetime import datetime
import time
import hashlib

CHARSET = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
           '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
           'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

tn_prefix = 'tb_url_'


def GenShortFromLong(longURL, key, urllen, expire):
    shortURL = ''
    expire = int(expire)
    try:
        Const.db_lock.acquire()
        with mysql.MySQLClient(autocommit=False) as sqlcmd:
            if not sqlcmd:
                log.WriteLogMsg(log.LogType.LogFAIL, 'DB Connection Failed')
                return False, longURL, '系统异常, 请稍后再试'

            # 存在自定义短链
            if key != '':
                oct_num, ix = STToOct(key)
                full_table_name = Const.dbname + '.' + tn_prefix + str(ix)

                # 检查表是否存在
                full_table_name = Const.dbname + '.' + tn_prefix + str(ix)
                cmdText = 'select TABLE_ID from information_schema.INNODB_TABLES where name=%(table_name)s'
                args = {
                    'table_name': Const.dbname + '/' + tn_prefix + str(ix)
                }
                result = sqlcmd.executequery(cmdText, args)
                if not result:
                    cmdText = 'create table if not exists ' + full_table_name + ' ( ' \
                                                                                'id bigint primary key, ' \
                                                                                'short_url varchar(50) default \'\' not null, ' \
                                                                                'full_url text not null, ' \
                                                                                'expire bigint default 0 null, ' \
                                                                                'visited bigint default 0 not null ' \
                                                                                '); '
                    sqlcmd.executenonquery(cmdText)
                    cmdText = 'create index %s on %s (expire asc); ' % (tn_prefix + str(ix) + '_expire', full_table_name)
                    sqlcmd.executenonquery(cmdText)

                cmdText = 'select id, short_url, full_url, expire from ' + full_table_name + ' where id=%(id)s'
                args = {
                    'id': oct_num
                }
                result = sqlcmd.executequery(cmdText, args)

                # 存在, 判断已有记录情况
                if result and len(result) > 0:

                    # 重复请求短链
                    if result[0]['full_url'] == longURL:
                        cmdText = 'update ' + full_table_name + ' set expire=%(expire)s where id=%(id)s'  # 续期
                        args = {
                            'id': oct_num,
                            'expire': datetime.now().timestamp() + expire
                        }
                        sqlcmd.executenonquery(cmdText, args)
                        sqlcmd.commit()
                        return True, result[0]['short_url'], ''

                    # 自定义短链重复但前一记录已过期
                    elif result[0]['expire'] < datetime.now().timestamp() and result[0]['expire'] != 0:
                        cmdText = 'update tb_url_custom set full_url=%(full_url)s, expire=%(expire)s where id=%(id)s'
                        args = {
                            'id': oct_num,
                            'full_url': longURL,
                            'expire': datetime.now().timestamp() + expire
                        }
                        sqlcmd.executenonquery(cmdText, args)
                        sqlcmd.commit()
                        return True, result[0]['short_url'], ''

                    # 自定义短链重复
                    else:
                        return False, longURL, '自定义key重复'

                # 不存在, 直接在当前表中添加
                else:
                    cmdText = 'insert into ' + full_table_name + ' (id, short_url, full_url, expire) values (%s, %s, %s, %s)'
                    args = (oct_num, key, longURL, datetime.now().timestamp() + expire)
                    sqlcmd.executenonquery(cmdText, args)
                    sqlcmd.commit()
                    return True, key, ''

            else:
                cmdText = 'insert into tb_control (type, value) ' \
                          'select %(Type)s, 0 from dual ' \
                          'where not exists (select ID from tb_control where type=%(Type)s)'
                args = {
                    'Type': 'maxID'
                }
                sqlcmd.executenonquery(cmdText, args)

                cmdText = 'select value+1 as next from tb_control where type=%(Type)s'
                args = {
                    'Type': 'maxID'
                }
                result = sqlcmd.executequery(cmdText, args)

                if result and len(result) > 0:
                    next_value = result[0]['next']
                else:
                    return False, longURL, '系统异常, 请稍后再试'

                shortURL = OctToST(next_value)
                # 存在自定义长度时补0
                if int(urllen) != 0:
                    if int(urllen) < len(shortURL):
                        return False, longURL, '自定义长度过短, 请修改或使用自定义key.'
                    else:
                        while len(shortURL) < int(urllen):
                            shortURL = CHARSET[0] + shortURL

                # 检查表是否存在
                full_table_name = Const.dbname + '.' + tn_prefix + str(next_value % len(CHARSET))
                cmdText = 'select TABLE_ID from information_schema.INNODB_TABLES where name=%(table_name)s'
                args = {
                    'table_name': Const.dbname + '/' + tn_prefix + str(next_value % len(CHARSET))
                }
                result = sqlcmd.executequery(cmdText, args)
                if not result:
                    cmdText = 'create table if not exists ' + full_table_name + ' ( ' \
                              'id bigint primary key, ' \
                              'short_url varchar(50) default \'\' not null, ' \
                              'full_url text not null, ' \
                              'expire bigint default 0 null, ' \
                              'visited bigint default 0 not null ' \
                              '); '
                    sqlcmd.executenonquery(cmdText)
                    cmdText = 'create index %s on %s (expire asc); ' % (tn_prefix + str(next_value % len(CHARSET)) + '_expire', full_table_name)
                    sqlcmd.executenonquery(cmdText)

                cmdText = 'insert into ' + full_table_name + ' (id, short_url, full_url, expire) values (%s, %s, %s, %s)'
                args = (next_value, shortURL, longURL, datetime.now().timestamp() + expire)
                sqlcmd.executenonquery(cmdText, args)

                cmdText = 'update tb_control set value=value+1 where type=%(Type)s'
                args = {
                    'Type': 'maxID'
                }
                sqlcmd.executequery(cmdText, args)
                sqlcmd.commit()

        return True, shortURL, ''
    except Exception as ex:
        log.WriteLogMsg(log.LogType.LogEXCEPTION, 'Generate Short URL Failed, Exception: ' + str(ex))
        sqlcmd.rollback()
        return False, longURL, '系统异常'
    finally:
        Const.db_lock.release()
        pass


def GetLongFromShort(shortURL, agent, client_ip):
    fullURL = ''
    try:
        with mysql.MySQLClient() as sqlcmd:
            if not sqlcmd:
                log.WriteLogMsg(log.LogType.LogFAIL, 'DB Connection Failed')
                return False, fullURL, '系统异常, 请稍后再试'

            oct_num, ix = STToOct(shortURL)
            full_table_name = Const.dbname + '.' + tn_prefix + str(ix)

            # 检查表是否存在
            cmdText = 'select TABLE_ID from information_schema.INNODB_TABLES where name=%(table_name)s'
            args = {
                'table_name': Const.dbname + '/' + tn_prefix + str(ix)
            }
            result = sqlcmd.executequery(cmdText, args)
            if not result:
                return False, '', '未找到该链接'

            cmdText = 'select id, short_url, full_url, expire from ' + full_table_name + ' where id=%(id)s'
            args = {
                'id': oct_num
            }
            result = sqlcmd.executequery(cmdText, args)
            if not result:
                return False, '', '未找到该链接'

            if result[0]['expire'] <= datetime.now().timestamp():
                return False, '', '该链接已过期'

            cmdText = 'update ' + full_table_name + ' set visited=visited+1 where id=%(id)s'
            args = {
                'id': oct_num
            }
            sqlcmd.executenonquery(cmdText, args)

            fullURL = result[0]['full_url']

            # 检查计次表是否存在
            date = datetime.now().strftime('%Y%m%d')
            cmdText = 'select TABLE_ID from information_schema.INNODB_TABLES where name=%(table_name)s'
            args = {
                'table_name': Const.dbname + '/tb_record_' + date
            }
            result = sqlcmd.executequery(cmdText, args)
            if not result:
                cmdText = 'create table if not exists tb_record_' + date + '( ' \
                          'id binary(16) not null primary key, ' \
                          'short_url varchar(50) default \'\' not null, ' \
                          'ip int not null, ' \
                          'agent varchar(200) not null, ' \
                          'visit_count int default 0 not null ' \
                          ');'
                sqlcmd.executenonquery(cmdText)

            cmdText = 'replace into tb_record_' + date + ' (id, short_url, ip, agent, visit_count) ' \
                      'select 0x'+hashlib.md5((shortURL + client_ip[0] + agent).encode(encoding='utf-8')).hexdigest()+', %(short_url)s, %(ip)s, %(agent)s, ' \
                      '(select coalesce(sum(visit_count), 0)+1 from tb_record_' + date + ' where id=0x'+hashlib.md5((shortURL + client_ip[0] + agent).encode(encoding='utf-8')).hexdigest()+');'
            args = {
                # 'id': bytes.fromhex(hashlib.md5((shortURL + client_ip[0] + agent).encode(encoding='utf-8')).hexdigest()),
                'short_url': shortURL,
                'ip': sum([256**j * int(i) for j, i in enumerate(client_ip[0].split('.')[::-1])]),
                'agent': agent
            }
            sqlcmd.executenonquery(cmdText, args)

            return True, fullURL, ''
    except Exception as ex:
        log.WriteLogMsg(log.LogType.LogEXCEPTION, 'Get Full URL Failed, Exception: ' + str(ex))
        return False, '', '系统异常'


def doClearing(interval):
    while True:
        try:
            if datetime.now().hour not in [2, 3, 4]:
                time.sleep(interval)
                continue

            with mysql.MySQLClient() as sqlcmd:
                if not sqlcmd:
                    log.WriteLogMsg(log.LogType.LogFAIL, 'DB Connection Failed')
                    time.sleep(interval)
                    continue

                cmdText = 'select table_name from information_schema.Tables where table_name like \'tb_url_%\' order by table_name;'
                result = sqlcmd.executequery(cmdText)

                if result:
                    for tablename in result:
                        cmdText = 'delete from ' + tablename + ' where expire<%(expire)s and expire>0'
                        args = {
                            'expire': datetime.now().timestamp()
                        }
                        sqlcmd.executequery(cmdText, args)
                        log.WriteLogMsg(log.LogType.LogSUCCESS, 'table ' + tablename + ' clearing completed.')

        except Exception as ex:
            log.WriteLogMsg(log.LogType.LogEXCEPTION, 'Do Cleaning Failed, Exception: ' + str(ex))

        time.sleep(interval)


def OctToST(oct_num):
    ret = ''
    i = 0
    while True:
        if oct_num // pow(len(CHARSET), i) == 0:
            ret += CHARSET[oct_num // pow(len(CHARSET), i)]
            break
        else:
            ret += CHARSET[oct_num // pow(len(CHARSET), i)]
            i += 1

    if ret != 0:
        ret = ret[0:len(ret)-1]
    return ret[::-1]


def STToOct(ST):
    ret = 0
    for i in range(0, len(str(ST))):
        ret += CHARSET.index(str(ST)[i]) * pow(len(CHARSET), len(str(ST)) - 1 - i)

    return ret, ret % len(CHARSET)
