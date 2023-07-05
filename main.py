from http.server import HTTPServer
from threading import Thread

import reader_server
import spider

if __name__ == '__main__':
    timer = Thread(target=spider.timer)
    timer.start()
    server = HTTPServer(reader_server.host, reader_server.RequestHandler)
    print("Starting server, listen at: %s:%s" % reader_server.host)
    server.serve_forever()