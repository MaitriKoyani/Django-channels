from django.utils.deprecation import MiddlewareMixin
from rest_framework.exceptions import AuthenticationFailed
from chat.models import Member,UserToken

class CustomTokenMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Check for token in the request (header, cookie, etc.)        
        token = request.COOKIES.get('token')
        if not token:
            return None  
        if token.startswith('Token '):
            token = token[6:]  
        try:
            
            mtoken = UserToken.objects.filter(token=token).first()
            
            if mtoken:
                print(mtoken.user)
                request.user = mtoken.user
                print(request.user)
            else:
                return None
        except Exception as e:  
            raise AuthenticationFailed('Invalid or expired token.',e)
        

from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
import json
from django.shortcuts import redirect

class CustomAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):

        headers = dict(scope["headers"])

        cookie_header = headers.get(b"cookie", b"").decode()
        
        def get_cookie_value(cookie_string, key):
            cookies = dict(item.split("=", 1) for item in cookie_string.split("; ") if "=" in item)
       
            return cookies.get(key)
        token = get_cookie_value(cookie_header, "token")

        if token:
            user = await self.get_user_from_token(token)
            scope['user'] = user
        else:
            scope['user'] = None
        
        # Proceed with the connection
        await super().__call__(scope, receive, send)

    @database_sync_to_async
    def get_user_from_token(self, token):

        from chat.models import UserToken
        try:
            token = UserToken.objects.get(token=token)
            user = token.user
            return user
        except Member.DoesNotExist:
            return None

