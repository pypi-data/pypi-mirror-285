from datetime import timezone
from dateutil.parser import parse
from rest_framework import status
from rest_framework.response import Response

class CheckPermissionsHelper:
    @staticmethod
    def verify_permissions(permission_name, crud_permission, permission=None):
        if permission.get('name') == permission_name and permission.get('crud_permissions') == crud_permission:
            return True       
        return False   
    
    @staticmethod
    def validate_expiry_date(expiry_date_time_str):
        """
        Validates that the expiry date is in the future and in the format YYYY-MM-DD HH:MM:SS AM/PM.
    
        Raises:
            ValidationError: If the expiry date is not valid.
        """
        try:
            expiry_date_time = parse(expiry_date_time_str)
        except ValueError:
            return False
        if expiry_date_time < timezone.now():
            return False
        return True
    
def create_permission_check(request, model_permission):
    permission = None
        
    if hasattr(request, 'permission'):
        permission = request.permission    
            
    if not CheckPermissionsHelper.verify_permissions(model_permission, 'Create', permission):
        print(F"[ERROR]: {model_permission}")
        return False, Response("You do not have permission to perform this action", status=status.HTTP_403_FORBIDDEN)    
    return True, ""

def read_permission_check(request, model_permission):
    permission = None
    
    if hasattr(request, 'permission'):
        permission = request.permission    
    if not CheckPermissionsHelper.verify_permissions(model_permission, 'Read',  permission):
        print(F"[ERROR]: {model_permission}")
        return False, Response("You do not have permission to perform this action", status=status.HTTP_403_FORBIDDEN)
    return True, ""

def update_permission_check(request, model_permission):
    permission = None
        
    if hasattr(request, 'permission'):
        permission = request.permission    
    if not CheckPermissionsHelper.verify_permissions(model_permission, 'Update', permission):
        print(F"[ERROR]: {model_permission}")
        return False, Response("You do not have permission to perform this action", status=status.HTTP_403_FORBIDDEN)    
    return True, ""

def delete_permission_check(request, model_permission):
    permission = None
   
    if hasattr(request, 'permission'):
        permission = request.permission
    if not CheckPermissionsHelper.verify_permissions(model_permission, 'Delete', permission):
        print(F"[ERROR]: {model_permission}")
        return False, Response("You do not have permission to perform this action", status=status.HTTP_403_FORBIDDEN)    
    return True, ""