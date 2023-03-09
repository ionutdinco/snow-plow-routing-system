import os.path
import secrets
import string
import json
from django.contrib.staticfiles import finders

class Token:

    def admin_token(self):
        alphabet = string.ascii_letters + string.digits
        token = ''.join(secrets.choice(alphabet) for i in range(15))
        return token

    def employee_token(self):
        alphabet = string.ascii_letters + string.digits
        token = ''.join(secrets.choice(alphabet) for i in range(10))
        return token
