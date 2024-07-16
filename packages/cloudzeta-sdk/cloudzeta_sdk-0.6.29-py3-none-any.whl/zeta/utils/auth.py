from __future__ import annotations
from cryptography.fernet import Fernet
from firebase_admin import auth
from flask import request, jsonify
from functools import wraps
import firebase_admin


# Use the default credentials, which will pull credentials from
# GOOGLE_APPLICATION_CREDENTIALS automatically.
# https://cloud.google.com/docs/authentication/application-default-credentials
cred = firebase_admin.credentials.ApplicationDefault()
firebase_admin.initialize_app(cred)


def verify_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if auth_header:
            token = auth_header.split(" ")[1]
        else:
            return jsonify({"error": "Missing token"}), 403

        try:
            decoded_token = auth.verify_id_token(token)
            request.user = decoded_token
        except Exception as e:
            return jsonify({"error": str(e)}), 403

        return f(*args, **kwargs)

    return decorated_function


def encrypt_token(token: str) -> tuple[str, str]:
    encryption_key = Fernet.generate_key()
    print(encryption_key)

    fernet = Fernet(encryption_key)
    return fernet.encrypt(token.encode()).decode(), encryption_key.decode()
