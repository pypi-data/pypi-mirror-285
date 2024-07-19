import requests
import base64
import json
import time
import jwt
import logging
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.state import token_backend
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken, UntypedToken
from django.contrib.auth import get_user_model
from django.conf import settings

logger = logging.getLogger(__name__)

class CustomeUser:
    def __init__(self, user_id):
        self.id = user_id
        self.username = f"user_{user_id}"

class CustomJWTAuthentication(JWTAuthentication):
    """
    Custom authentication class that extends JWTAuthentication.
    This class handles the authentication process using JWT tokens.
    """

    def __init__(self, url=None, *args, **kwargs):
        self.url = url
        super().__init__(*args, **kwargs)

    def authenticate(self, request):
        """
        Authenticates the request using JWT token.
        
        Args:
            request (HttpRequest): The request object.
            url (str): The URL to send the token for validation.
        
        Returns:
            tuple: A tuple containing the authenticated user and the raw token.
        
        Raises:
            AuthenticationFailed: If the authorization credentials were not provided or the token is invalid.
        """
        if self.url is None:
            self.url = 'http://localhost:8001/jwt/token/verify/'
        header = self.get_header(request)
        if header is None:
            logger.error("Header not provided ")
            raise AuthenticationFailed("Header not provided")

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            logger.error("Authorization credentials were not provided")
            raise AuthenticationFailed("Authorization credentials were not provided")
        
        try:          
            validated_token = token_backend.decode(raw_token, verify=True)
            user_id = validated_token.get('user_id', None)
        except Exception as e:
            logger.error(f"Invalid token: {e}")
            print(f"Invalid token: {e}")
            raise InvalidToken(e) from e
        if not validated_token or user_id is None:
            logger.error("Invalid token or No user ID found.")
            raise InvalidToken("Invalid token or No user ID found.")
        if hasattr(settings, 'AUTH_USER_MODEL'):
            AppUser = get_user_model()
            try:
                app_user = AppUser.get_app_users_by_id(user_id)
            except Exception as e:
                logger.error(f"Error fetching user: {e}")
                print(f"Error fetching user: {e}")
                raise AuthenticationFailed("Invalid user") from e
        else:
            app_user = CustomeUser(user_id)
        request.user = app_user
        return super().authenticate(request)