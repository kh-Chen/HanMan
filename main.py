from http.server import HTTPServer
import schedule

import reader_server
import spider

if __name__ == '__main__':
    schedule.every().day.at("04:00").do(spider.start)
    server = HTTPServer(reader_server.host, reader_server.RequestHandler)
    print("Starting server, listen at: %s:%s" % reader_server.host)
    server.serve_forever()