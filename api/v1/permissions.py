from rest_framework.permissions import BasePermission
from rest_framework.exceptions import AuthenticationFailed
from api.v1.token import *

class TokenBasedAuthentication(BasePermission):
    def has_permission(self, request, view):
        auth_header = request.headers.get('Authorization', '')
        token = auth_header.split(' ')[1] if ' ' in auth_header else None
        if token:
            try:
                payload = verify_token(token)
                if isinstance(payload, dict):
                    request.user_id = payload["user_id"]
                    return True
            except Exception as e:
                return Response(
                    {"status": "error", "message": "Invalid Token"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return False
