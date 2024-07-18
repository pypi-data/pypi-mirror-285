import tornado.web
from api.tornado import PublishHandler
def make_app():
    return tornado.web.Application([
        (r'/greet', PublishHandler)
    ])