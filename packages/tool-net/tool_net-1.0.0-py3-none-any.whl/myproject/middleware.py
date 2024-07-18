from django.http import JsonResponse
import json
class ApiResponseMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['Access-Control-Allow-Origin'] = '*'
        if isinstance(response, JsonResponse):
            content = response.content.decode('utf-8')
            data = json.loads(content)
            response_data = {'code': 200, 'msg': 'ok', 'data': data}
            response = JsonResponse(response_data)
        return response