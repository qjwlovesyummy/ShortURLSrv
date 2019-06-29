import LogProc as log
import http
import re
import Utils
import Const
import json


def ProcessClientData(paths, params, headers, client_address):
    try:
        if not paths or len(paths) != 1:
            return False, http.HTTPStatus.BAD_REQUEST, ''

        if paths[0] == 'geturl' and params and params['fullurl']:
            if not re.match('(http|https)://[^\s]', params['fullurl'][0]):
                return False, http.HTTPStatus.BAD_REQUEST, ''
            if 'key' in params.keys():
                if not re.match('[a-zA-Z0-9]{2,8}', params['key'][0]):
                    return False, http.HTTPStatus.BAD_REQUEST, ''
            if 'urllen' in params.keys():
                if int(params['urllen'][0]) <= 0 or int(params['urllen'][0]) >= 9:
                    return False, http.HTTPStatus.BAD_REQUEST, ''
            if 'expire' in params.keys() and isinstance(params['expire'][0], int):
                if params['expire'][0] < 0:
                    return False, http.HTTPStatus.BAD_REQUEST, ''

            succ, shortUrl, msg = Utils.GenShortFromLong(params['fullurl'][0], key=params['key'][0] if 'key' in params.keys() else '',
                                                         urllen=params['urllen'][0] if 'urllen' in params.keys() else Const.def_keylen,
                                                         expire=params['expire'][0] if 'expire' in params.keys() else Const.def_expire)
            if not succ:
                datarsp = {'Status': 1, 'Data': msg}
            else:
                datarsp = {'Status': 0, 'Data': Const.local_domain + '/' + shortUrl}
            return True, http.HTTPStatus.OK, json.dumps(datarsp)
        else:
            succ, fullURL, msg = Utils.GetLongFromShort(paths[0], headers['User-Agent'] if 'User-Agent' in headers.keys() else '', client_address)
            if succ:
                return True, http.HTTPStatus.TEMPORARY_REDIRECT, fullURL
            else:
                return False, http.HTTPStatus.NOT_FOUND, ''

    except Exception as ex:
        log.WriteLogMsg(log.LogType.LogEXCEPTION, 'Prcess Data Failed, Exception: ' + str(ex))
        return False, http.HTTPStatus.INTERNAL_SERVER_ERROR, ''
