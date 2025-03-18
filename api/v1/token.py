import base64
import json
import time
import hmac
import hashlib

from rest_framework.response import Response
from rest_framework import status

SECRET_KEY = 'X3z32rH7CRW4pUn24ycJGp1Y5YtQ6MNW3W3T-Falcon-iOS-Application_Dev-ASEcode_AT-SILVERHOST'
API_KEY = 'X3z32rH7CRW4pUn2ANWARSADIKPYTHONDEVELOPER4ycJG' 


def generate_token(user_id): 
    payload = {
        'user_id': user_id,
        'exp': int(time.time()) + 9744161462987654321,
        'project': 'falcon',
        'type': 'iosapplication',
    }
    
    json_payload = json.dumps(payload).encode('utf-8')
    encoded_payload = base64.urlsafe_b64encode(json_payload).decode('utf-8').rstrip('=')

    # Create a signature
    signature = hmac.new(
        SECRET_KEY.encode('utf-8'),  (encoded_payload + API_KEY).encode('utf-8'), 
        hashlib.sha256
    ).hexdigest()

    # Combine payload and signature
    token = f'{encoded_payload}.{signature}'
    return token


def verify_token(token):
    try:
        # Split the token into payload and signature
        encoded_payload, signature = token.split('.')
        
        # Verify the signature
        expected_signature = hmac.new(
            SECRET_KEY.encode('utf-8'), 
            (encoded_payload + API_KEY).encode('utf-8'), 
            hashlib.sha256
        ).hexdigest()
        if signature != expected_signature:
            return 'Invalid signature'
        
        # Decode the payload
        json_payload = base64.urlsafe_b64decode(encoded_payload + '==').decode('utf-8')
        payload = json.loads(json_payload)
        
        if time.time() > payload['exp']:
            return 'Token expired'
        
        return payload
    except Exception as e:
        return str(e)
