from datetime import datetime
from typing import List
import logging

from google.cloud import firestore
from google.oauth2 import credentials
from pxr import Sdf, Tf, Usd

from zeta.sdk.uid import generate_uid
from zeta.usd.sync import SyncData, SyncOp, SyncOpList, SyncOpType

import json
import requests

CLOUD_ZETA_PROJECT_ID = "gozeta-prod"
CLOUD_ZETA_URL_PREFIX = "https://cloudzeta.com"
GOOGLE_SIGN_UP_URL = "https://identitytoolkit.googleapis.com/v1/accounts:signUp"
GOOGLE_AUTH_URL = "https://securetoken.googleapis.com/v1/token"
COLAB_USER_DATA_KEY_EPHEM_TOKEN = "ZETA_EPHEM_TOKEN"

class EphemeralSession(object):

    def __init__(self, api_key):
        logging.basicConfig(level=logging.INFO)

        self._api_key = api_key
        self._edit_layer = Sdf.Layer.CreateAnonymous("editLayer.zeta")
        self._stage = Usd.Stage.Open(self._edit_layer)
        self._stage.SetEditTarget(self._edit_layer)
        self._stageListener = Tf.Notice.Register(
            Usd.Notice.StageContentsChanged,
            self._sync_edit_layer_update,
            self._stage)

        self._auth_token = None
        self._refresh_token = None
        self._user_uid = None
        self._session_ref = None
        self._edit_layer_ref = None
        self._session_uid = None

    @property
    def stage(self):
        return self._stage

    @property
    def uid(self):
        return self._session_uid

    def preview(self) -> str:
        if self._session_uid is None:
            self._connect()

        assert self._session_uid is not None, "Session not connected to remote."
        return f"{CLOUD_ZETA_URL_PREFIX}/player/{self._session_uid}"

    def session_url(self) -> str:
        assert self._session_uid is not None, "Session not connected to remote."
        return f"{CLOUD_ZETA_URL_PREFIX}/zeta/ephemerals/session/{self._session_uid}"

    @staticmethod
    def _get_now_string():
        return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

    def _connect(self):
        assert self._session_uid is None, "Session already connected to remote."

        signed_in: bool = self._try_signin()
        if not signed_in:
            self._signup_anonymously()

        self._session_uid = self._create_session()

        # Trigger session contents changed event to sync data.
        self._sync_edit_layer_update()

    def _try_signin(self) -> bool:
        if self._refresh_token is None:
            try:
                from google.colab import userdata
                try:
                    self._refresh_token = userdata.get(COLAB_USER_DATA_KEY_EPHEM_TOKEN)
                except userdata.NotebookAccessError:
                    return False
                except userdata.SecretNotFoundError:
                    return False
            except Exception:
                # Can't access colab userdata, skip signin.
                return False

        assert self._refresh_token is not None, "Refresh token is invalid"

        request_url = f"{GOOGLE_AUTH_URL}?key={self._api_key}"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {
            "grant_type": "refresh_token",
            "refresh_token": self._refresh_token,
        }
        response = requests.post(request_url, headers=headers, data=data)
        if response.ok:
            res = response.json()
            self._auth_token = res["id_token"]
            self._refresh_token = res["refresh_token"]
            self._user_uid = res["user_id"]
            return True
        else:
            return False

    def _set_refresh_token_for_test(self, refresh_token) -> bool:
        if refresh_token is None:
            logging.warning("Refresh token is None.")
            return False
        if self._refresh_token is not None:
            logging.warning("Refresh token already set.")
            return False

        self._refresh_token = refresh_token
        return True

    def _signup_anonymously(self):
        request_url = f"{GOOGLE_SIGN_UP_URL}?key={self._api_key}"
        headers = {
            "Content-Type": "application/json",
            "Referer": "http://localhost:8848"
        }
        data = json.dumps({"returnSecureToken": True})
        response = requests.post(request_url, headers=headers, data=data)
        assert response.ok, "Failed to login anonymously."

        res = response.json()

        # TODO(CZ-186) prompt user to create a CloudZeta account.
        self._auth_token = res["idToken"]
        self._refresh_token = res["refreshToken"]
        self._user_uid = res["localId"]

    def _create_session(self):
        assert self._auth_token is not None, "Auth token is invalid."
        assert self._refresh_token is not None, "Refresh token is invalid."

        cred = credentials.Credentials(
            self._auth_token, self._refresh_token, client_id="", client_secret="",
            token_uri=f"{GOOGLE_AUTH_URL}?key={self._api_key}")

        session_db = firestore.Client(CLOUD_ZETA_PROJECT_ID, cred)
        session_uid = generate_uid()
        edit_layer_uid = generate_uid()
        annotation_layer_uid = generate_uid()

        self._session_ref = session_db.collection("sessions").document(session_uid)

        created_at = self._get_now_string()
        self._session_ref.set({
            "uid": session_uid,
            "name": f"Ephemeral Session [{datetime.now().strftime('%A, %B %d, %Y %I:%M:%S %p')}]",
            "createdAt": created_at,
            "updatedAt": created_at,
            "deletedAt": None,

            "projectUid": "ltm7y0mw9h7xwe5t",
            "rootAssetPath": "/ephemeral_root.usdc",
            "externalAssetPath": None,
            "assetPrefix": ["/", "/ephemeral_root.usdc"],
            "isPublic": False,
            "isEphemeral": True,
            "isPublished": True,
            "roles": {
                "FygPbdvG6GfNpCPbPNhURDMiLsu2": "owner",
                self._user_uid: "editor",
            },
            "state": "ready",

            "annotationLayerUid": annotation_layer_uid,
            "editLayerUid": edit_layer_uid,

            "error": None,
            "thumbnailAsset": None,
        })

        layer_collection = session_db.collection("sessions", session_uid, "layers")
        self._edit_layer_ref = layer_collection.document(edit_layer_uid)
        self._edit_layer_ref.set({
            "uid": edit_layer_uid,
            "name": "edit",
            "createdAt": created_at,
            "updatedAt": created_at,
            "deletedAt": None,
            "data": {},
        })

        layer_collection.document(annotation_layer_uid).set({
            "uid": annotation_layer_uid,
            "name": "annotation",
            "createdAt": created_at,
            "updatedAt": created_at,
            "deletedAt": None,
            "data": {},
        })

        return session_uid

    def _sync_edit_layer_update(self, *args):
        if self._session_uid is None:
            logging.info("Remote Session not connected, skipping sync")
            return

        ops: SyncOpList = SyncData.GetLayerUpdates(self._edit_layer)
        layer_data_update = self._get_layer_update_data(ops)

        if len(layer_data_update) == 0:
            # Explicitly return here to avoid updating the layer data with an empty update.
            return

        layer_update = {
            "data": layer_data_update,
            "updatedAt": self._get_now_string(),
        }

        self._edit_layer_ref.set(layer_update, merge=True)

    def _get_layer_update_data(self, ops: List[SyncOp]):
        layer_update = {}
        for sync_op in ops:
            if sync_op.opType == SyncOpType.CreateNode:
                node_path: str = sync_op.nodePath
                node_type: int = sync_op.nodeType
                if (node_path in layer_update):
                    logging.warning(f"Found duplicate node path: {node_path}")
                else:
                    layer_update[node_path] = {
                        "nodeType": node_type,
                        "fields": {},
                    }

            elif sync_op.opType == SyncOpType.SetField:
                node_path: str = sync_op.nodePath
                field_name: str = sync_op.fieldName
                field_value: bytearray = sync_op.GetFieldValue()
                if node_path not in layer_update:
                    layer_update[node_path] = {
                        "fields": {}
                    }
                layer_update[node_path]["fields"][field_name] = bytes(field_value)

            elif sync_op.opType == SyncOpType.MoveNode:
                raise NotImplementedError("MoveNode not implemented")

            elif sync_op.opType == SyncOpType.EraseNode:
                node_path: str = sync_op.nodePath
                layer_update[node_path] = firestore.DELETE_FIELD

            elif sync_op.opType == SyncOpType.EraseField:
                node_path: str = sync_op.nodePath
                field_name: str = sync_op.fieldName

                if node_path not in layer_update:
                    layer_update[node_path] = {
                        "fields": {}
                    }

                layer_update[node_path]["fields"][field_name] = firestore.DELETE_FIELD

        return layer_update
