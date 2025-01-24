from functools import wraps
from django.http import JsonResponse
from django.shortcuts import redirect
from rest_framework import status
from .models import CustomTokenAuthentication
from rest_framework.decorators import authentication_classes

@authentication_classes([CustomTokenAuthentication])
def check_login(view_func):
    @wraps(view_func) 
    def wrapper(request, *args, **kwargs):
        
        if not request.user.id:
            try:  
                authentication = CustomTokenAuthentication()
                if authentication.authenticate(request):
                    return redirect('/')
                else:
                    return view_func(request, *args, **kwargs)
            except Exception as e:
                return view_func(request, *args, **kwargs)
            
            return view_func(request, *args, **kwargs)
        
        return redirect('/')
    return wrapper

def login_required(view_func):
    @wraps(view_func) 
    def wrapper(request, *args, **kwargs):

        if not request.user.id:
            try:
                authentication = CustomTokenAuthentication()
                if authentication.authenticate(request):
                    user,auth = authentication.authenticate(request)
                else:
                    return redirect('/login/')
            except Exception as e:
                return JsonResponse({'error':'Login required ','error':str(e)},status=status.HTTP_401_UNAUTHORIZED) 
            request.user=user
            if not request.user:
                return redirect('/login/')
        return view_func(request, *args, **kwargs)
    return wrapper

