from rest_framework_simplejwt.tokens import AccessToken, RefreshToken, UntypedToken, Token
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
import requests
import base64
import json
import time
from django.core.cache import cache
import redis
import jwt
from jwt.exceptions import DecodeError
from rest_framework_simplejwt.settings import api_settings

 
# Assuming your Redis server is running locally
# redis_host = env('REDIS_HOST')
# redis_port = env('REDIS_PORT')
redis_host = 'localhost'
redis_port = 30001
redis_db = 0  # Assuming you're using the default database
 
# Create the connection
redis_conn = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db)
 
class TokenUtils:    
    @classmethod
    def get_tokens_for_user_inline(cls, user):
        token = RefreshToken.for_user(user)
        return str(token), str(token.access_token)        
       
    @classmethod
    def get_tokens_for_user(cls, user):
        token_obtain_url = 'http://localhost/user-mngmt/token/'  # take out to env file
        data = {
            'email': user.email,            
            'user_id': user.id,
            'emp_id': user.emp_id
        }
        try:
            print(f"Data: {data}")
            response = requests.post(token_obtain_url, data=data)
            print(f"Response: {response}")
            response_data = response.json()
            access_token = response_data.get('access', None)
            refresh_token = response_data.get('refresh', None)
 
            if access_token and refresh_token:
                print (f"No access token: {access_token} and refresh token: {refresh_token}")
                return access_token, refresh_token
            else:
                return None, None
        except Exception as e:
            print(f'Token Obtain Error: {e}')
            return None, None
       
    @classmethod
    def refresh_access_token(cls, refresh_token):
        try:
            token = RefreshToken(refresh_token)
            new_access_token = str(token.access_token)
            return new_access_token
        except Exception as e:
            print(f'Token Refresh Error: {e}')
            return None
   
    @classmethod
    def verify_token(cls, access_token):
        try:
            token = AccessToken(access_token)
            success, info = token.verify()
            return success, info
        except Exception as e:
            print(f'Token Verify Error: {e}')
            return False, str(e)
         
    @classmethod
    def decode_token(cls, token):
        try:
            # Decode token to inspect the payload without verifying the signature
            verifying_key = api_settings.VERIFYING_KEY
            decoded_token = jwt.decode(token, verifying_key, algorithms=['RS256'], options={"verify_signature": True})            
            return decoded_token
        except jwt.InvalidSignatureError as e:
            print(f"Invalid Signature Error: {e}")
            return None
        except DecodeError as e:
            print(f"Invalid token: {e}")
            return None        
        except Exception as e:
            print(f"Error decoding token: {e}")
            return None
   
    @classmethod
    def get_expiry(cls, jwt_token):
        import datetime
        print(F"Inisde get_expiry: {jwt_token}")
        if type(jwt_token) == dict:
            payload = jwt_token.get('exp', None)
            print(f"\nPayload: {payload}")
            return payload
        else:
            payload = jwt_token.split('.')[1]
            # Add padding to fix incorrect token length
            payload += '=' * (-len(payload) % 4)
            decoded_payload = base64.b64decode(payload)
            payload_json = json.loads(decoded_payload)
            print(f"\nPayload JSON: {payload_json}")
            #Convert exp to datetime
            expiry = payload_json['exp']
            # Convert Unix timestamp to datetime object
            expiry_datetime = datetime.datetime.fromtimestamp(expiry)
            print(f"\nExpiry: {expiry_datetime}")
            return payload_json['exp']
   
    @classmethod
    def is_token_expired(cls, jwt_token):
        expiry = cls.get_expiry(jwt_token)
        check_time = time.time()        
        return check_time > expiry
        
    @classmethod
    def validate_token(cls, token):
        try:  
            # Validate token by creating an UntypedToken instance
            decoded_token = cls.decode_token(token)
            generic_token = UntypedToken(token, verify=True)
            verify = generic_token.verify()
            if not decoded_token:
                raise jwt.InvalidSignatureError  
            if verify:
                print(f"Token verified: {verify}")
                raise InvalidToken(verify)   
            if cls.is_token_expired(decoded_token):
                print(f"Token expired: {decoded_token}")
                raise TokenError('Token expired')       
            return True
        except InvalidToken as e:
            print(f"Token validation error: {e}")
            return False
        except TokenError as e:
            print(f"Token error in Validate Token: {e}")
            return False
        except jwt.InvalidSignatureError as e:
            print(f"Invalid Signature Error: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error during token validation: {e}")
            return False
 
    @classmethod
    def check_blacklist(cls, token):
        # print(f"\nChecking blacklist for token\n")
        # decoded_token = json.loads()
        # if decoded_token:
        #     jti = decoded_token.get('jti', None)
        #     jti = jti.encode('utf-8')
        #     redis_list = cls.get_blacklist(token)
        #     if jti in redis_list:
        #         return False
        #     if jti:              
        #         return redis_conn.get(jti) is None
        #     else:
        #         return None
        return True
        # return True
 
    @classmethod
    def get_blacklist(cls, token):
        list_redis = redis_conn.keys('*')
        decoded_list = []
        for key in list_redis:
            key = key.decode('utf-8')
            decoded_list.append(key)
        return decoded_list