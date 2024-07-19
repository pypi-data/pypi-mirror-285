from django.http import HttpResponse
from quickQrLib.middleware_util.token_utils import TokenUtils

from django.utils.deprecation import MiddlewareMixin
class TokenRefreshMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response
        self.count = 0
        self.token_generator = TokenUtils()
        self.ignore_paths = ['/user-mngmt/token/refresh/', '/token/refresh/', '/user-mngmt/token/', '/token/', '/user-mngmt/token/verify/', '/token/verify/', '/user-mngmt/login/', '/login/','/metrics', '/metrics/', '/user-mngmt/forgot-password/', '/admin/', '/admin/login/', '/user-mngmt/forgot-password/', '/forgot-password/', '/health/']

    def process_request(self, request):
        self.count += 1
        print(f"Request #{self.count} - {request.path}")
        if request.path in self.ignore_paths:
            return self.get_response(request)
        response, continue_on = self.refresh_access_token(request)
        if continue_on:
            print("\nContinue on is TRUE\n")
            if response == "Access Token is still valid":
                print(f"\nresponse: {response}\n")
                return self.get_response(request)
            else:
                print(f"Token Refresh Success: {response}")
                try: 
                    request.META['HTTP_AUTHORIZATION'] = f'Bearer {response}'   
                    print (f"New Authorization Header created: {request.META['HTTP_AUTHORIZATION']}")
                    # Set a custom header to indicate token refresh success
                    request.META['X-Token-Refreshed'] = 'true'
                    print (f"New Header created: {request.META['X-Token-Refreshed']}")   
                    return self.get_response(request)             
                except Exception as e:
                    print(f"Error creating header in success: {e}")
                    return HttpResponse({"ERROR:", e}, status=401)                
        elif not continue_on:
            print(f"Token Refresh Error: {response}")
            try:
                # Set a custom header to indicate token refresh failure
                request.META['X-Token-Refreshed'] = 'false'
                print (f"New Header created: {request.META['X-Token-Refreshed']}")
            except Exception as e:
                print(f"Error creating header in failed: {e}")
            return HttpResponse({"ERROR:", response}, status=401)            
        else:
            if response != "Access Token is still valid":
                return HttpResponse({"ERROR:", response}, status=401)        
        
    def refresh_access_token(self, request):
        print("\n====================\nInside refresh_access_token\n====================\n")
        try:
            access_token = request.META.get('HTTP_AUTHORIZATION', None)
            refresh_token = request.META.get('HTTP_REFRESH_TOKEN', None)   
            if refresh_token:
                not_blacklisted = self.token_generator.check_blacklist(refresh_token)
                #returns True on token not blacklisted, False on token blacklisted, None on token not found
                if not not_blacklisted:
                    return "ERROR: Refresh Token is blacklisted", False
                if not_blacklisted is None:
                    return "ERROR: Refresh Token is invalid", False
                # token_expired = self.token_generator.is_token_expired(refresh_token)
                token_valid = self.token_generator.validate_token(refresh_token)
                if not token_valid:
                    print(f"Refresh Token is expired")
                    return "ERROR: Refresh Token has expired", False # THIS TRIGGERS A FORCED LOGOUT
            else:
                print(f"No refresh token")
                return "No refresh token", False
            if access_token:            
                not_blacklisted = self.token_generator.check_blacklist(access_token)
                #returns True on token not blacklisted, False on token blacklisted, None on token not found
                if not not_blacklisted:
                    print(f"Access Token is blacklisted")
                    return "ERROR: Token is blacklisted", False
                if not_blacklisted is None:
                    print (f"Access Token is invalid")
                    return "ERROR: Token is invalid", False
                token_expired = self.token_generator.is_token_expired(access_token)
                if token_expired:
                    print(f"Access Token is expired")
                    access_token = self.token_generator.refresh_access_token(refresh_token)
                    if access_token:
                        print("Token Refreshed")
                        return access_token, True
                    else:
                        print("Invalid Access token")
                        return "ERROR: Invalid Access token", False
                else:
                    print("Access Token is still valid")
                    return "Access Token is still valid", True
            else:
                print(f"No access token")
                return "No access token", False
        except Exception as e:
            print(f'Error: {e}')
            return f"ERROR: {e}", False

    def process_response(self, request, response):
        # print (f"\n++++++++++++++\nResponse #{self.count} - {response.status_code}\nResponse Msg: - {str(response.content)}\n++++++++++++++++\n")
        print (f"\n++++++++++++++\nResponse #{self.count} - {response.status_code}\n++++++++++++++++\n")
        return response
    