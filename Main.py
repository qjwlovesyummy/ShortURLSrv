from Srv import ShortURLSrv
import Const
import threading
import Utils

Server = ShortURLSrv()

if __name__ == '__main__':

    # 服务地址
    Const.local_domain = 'http://127.0.0.1:10086'
    Const.dbname = 'shorturlsrv'
    # 数据库操作锁
    Const.db_lock = threading.Lock()
    # 默认过期时间(s)
    Const.def_expire = 3600 * 24 * 3  # 三天
    # 默认短链key的长度
    Const.def_keylen = 7

    WebSrvThread = threading.Thread(target=Server.start)
    WebSrvThread.start()

    ClearingThread = threading.Thread(target=Utils.doClearing, args=(30, ))
    ClearingThread.start()
