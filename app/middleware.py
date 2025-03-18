from django.shortcuts import render

class Custom404Middleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if response.status_code != 200 and response.status_code != 302:
            print(response)
            return render(request, 'error.html',  status=404)
 
        return response