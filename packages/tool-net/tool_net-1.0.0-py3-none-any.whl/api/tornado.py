import tornado.web
import json

class PublishHandler(tornado.web.RequestHandler):
    def post(self):
        print(self.get_body_argument('name'))
        print(self.get_body_arguments('name'))
        data = {"status": '200', "msg": 'ok', 'code': 200 }
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(data))
