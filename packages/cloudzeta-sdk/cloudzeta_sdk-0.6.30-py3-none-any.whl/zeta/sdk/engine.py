from __future__ import annotations
from cryptography.fernet import Fernet
from google.cloud import firestore
from google.oauth2 import credentials
import requests

from zeta.utils.logging import zetaLogger
from zeta.sdk.asset import ZetaAsset


CLOUD_ZETA_PROJECT_ID = "gozeta-prod"
CLOUD_ZETA_API_KEY = "AIzaSyBBDfxgpOAnH7GJ6RNu0Q_v79OGbVr1V2Q"
CLOUD_ZETA_URL_PREFIX = "https://cloudzeta.com"
GOOGLE_AUTH_URL = "https://securetoken.googleapis.com/v1/token"


class ZetaEngine(object):
    def __init__(self, api_key=CLOUD_ZETA_API_KEY, zeta_url_prefix=CLOUD_ZETA_URL_PREFIX):
        self._api_key = api_key
        self._zeta_url_prefix = zeta_url_prefix

        self._auth_token = None
        self._refresh_token = None
        self._user_uid = None

        self._db: firestore.Client = None

    def login(self, token_uid: str, encryption_key: str) -> bool:
        """
        Login with the given token_uid and encryption_key.

        @param token_uid: The token_uid to login with.
        @param encryption_key: The encryption_key to decrypt the token with.
        """
        zeta_auth_token_url = f"{self._zeta_url_prefix}/api/auth/token/get"
        response = requests.get(zeta_auth_token_url, params={"authToken": token_uid})
        if not response.ok:
            zetaLogger.error(f"Failed to get auth token")
            return False

        res = response.json()
        encrypted_token = res.get("encryptedToken")

        try:
            fernet = Fernet(encryption_key.encode())
            self._refresh_token = fernet.decrypt(encrypted_token.encode()).decode()
        except Exception as e:
            zetaLogger.error("Failed to decrypt token.")
            return False

        google_login_url = f"{GOOGLE_AUTH_URL}?key={self._api_key}"
        response = requests.post(
            google_login_url,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
            }, data={
                "grant_type": "refresh_token",
                "refresh_token": self._refresh_token,
            }
        )

        if not response.ok:
            zetaLogger.error(f"Failed to login with auth token")
            return False

        res = response.json()
        self._auth_token = res["id_token"]
        self._refresh_token = res["refresh_token"]
        self._user_uid = res["user_id"]

        assert self._auth_token is not None
        assert self._refresh_token is not None
        assert self._user_uid is not None

        cred = credentials.Credentials(
            self._auth_token, self._refresh_token, client_id="", client_secret="",
            token_uri=f"{GOOGLE_AUTH_URL}?key={self._api_key}")

        self._db = firestore.Client(CLOUD_ZETA_PROJECT_ID, cred)
        assert self._db is not None

        return True

    def api_get(self, url: str, params: dict) -> requests.Response:
        if not self._auth_token:
            raise ValueError("Must login() before get()")
        if not url.startswith("/"):
            raise ValueError("URL must start with /")

        full_url: str = f"{self._zeta_url_prefix}{url}"
        return requests.get(
            full_url,
            headers={
                "Authorization": f"Bearer {self._auth_token}",
            },
            params=params
        )

    def api_post(self, url: str, json: dict) -> requests.Response:
        if not self._auth_token:
            raise ValueError("Must login() before get()")
        if not url.startswith("/"):
            raise ValueError("URL must start with /")

        full_url: str = f"{self._zeta_url_prefix}{url}"
        return requests.post(
            full_url,
            headers={
                "Authorization": f"Bearer {self._auth_token}",
                "Content-Type": "application/json",
            },
            json=json
        )

    def asset(self, owner_name: str, project_name: str, asset_path: str) -> ZetaAsset:
        return ZetaAsset(self, owner_name, project_name, asset_path)