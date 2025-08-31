from django.http import HttpResponseServerError

def trigger_500(request):
    return HttpResponseServerError("Testing 500 error")
