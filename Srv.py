import http
from http import server as httpserver
from socketserver import ThreadingMixIn
import LogProc as log
import Process
from urllib import parse


class ShortURLSrv(object):

    def __init__(self):
        self.host = '0.0.0.0'
        self.port = 10086
        self.server = None

    def start(self):
        try:
            self.server = ThreadingHTTPServer((self.host, self.port), WebRequestHandler)
            self.server.serve_forever()
            log.WriteLogMsg(log.LogType.LogSUCCESS, 'http server started successfully at port %s!' % str(self.port))
            return True
        except Exception as ex:
            log.WriteLogMsg(log.LogType.LogEXCEPTION, 'http server start failed, Exception: ' + str(ex))
            return False

    def stop(self):
        try:
            if self.server:
                self.server.server_close()
            return True
        except Exception as ex:
            log.WriteLogMsg(log.LogType.LogEXCEPTION, 'http server stop failed, Exception: ' + str(ex))
            return False


class ThreadingHTTPServer(ThreadingMixIn, httpserver.HTTPServer):
    pass


class WebRequestHandler(httpserver.BaseHTTPRequestHandler):

    def do_POST(self):
        log.WriteLogMsg(log.LogType.LogFAIL, 'Unsupported Request Method [POST]')
        RspCode = http.HTTPStatus.METHOD_NOT_ALLOWED
        self.send_error(RspCode)

    def do_PUT(self):
        log.WriteLogMsg(log.LogType.LogFAIL, 'Unsupported Request Method [PUT]')
        RspCode = http.HTTPStatus.METHOD_NOT_ALLOWED
        self.send_error(RspCode)

    def do_GET(self):
        self.ProcessRequest()

    def ProcessRequest(self):
        RspCode = http.HTTPStatus.OK
        RspStr = ''

        try:
            path = self.path
            if '?' in path:
                path = path[0:path.index('?')]
            paths = list(filter(lambda t: t != '', path.split('/')))

            params = parse.parse_qs(parse.urlparse(self.path).query)

            Succ, RspCode, RspStr = Process.ProcessClientData(paths, params, self.headers, self.client_address)

        except Exception as ex:
            RspCode = http.HTTPStatus.INTERNAL_SERVER_ERROR
            log.WriteLogMsg(log.LogType.LogEXCEPTION, 'process request failed, Exception: ' + str(ex))
        finally:
            if RspCode == http.HTTPStatus.OK:
                self.send_response(RspCode)
                self.end_headers()
                self.wfile.write(RspStr.encode(encoding='utf-8'))
            elif RspCode == http.HTTPStatus.TEMPORARY_REDIRECT:
                self.send_response(RspCode)
                self.send_header('Location', RspStr)
                self.end_headers()
            else:
                self.send_error(RspCode)
                self.wfile.write(RspStr.encode(encoding='utf-8'))

