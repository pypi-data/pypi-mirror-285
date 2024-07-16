from google.cloud import storage
import os

from zeta.usd.resolve import AssetFetcher
from zeta.utils.logging import zetaLogger

class AssetDownloader(object):
    _bucket_name = "gozeta-prod.appspot.com"
    _storage_client = storage.Client()
    _bucket = _storage_client.get_bucket(_bucket_name)
    _fetcher = AssetFetcher.GetInstance()

    @classmethod
    def download_asset(cls, asset_blobname: str, temp_path: str):
        asset_blob = cls._bucket.blob(asset_blobname)
        if not asset_blob.exists():
            zetaLogger.warning(f"asset '{asset_blobname}' does not exist")
            return ""

        asset_filename: str = os.path.join(temp_path, asset_blobname)
        asset_dirname: str = os.path.dirname(asset_filename)
        if not os.path.exists(asset_dirname):
            os.makedirs(asset_dirname)
        asset_blob.download_to_filename(asset_filename)

        return asset_filename


# Register the asset downloader callback. Note that we have to let the AssetDownloader class down
# the PyObject (i.e. AssetFetcher), so that destructor can be called in a proper order.
AssetDownloader._fetcher.SetOnFetchCallback(AssetDownloader.download_asset)


class AssetUtils(object):
    @staticmethod
    def is_image_asset(asset_path: str) -> bool:
        _, ext = os.path.splitext(asset_path)
        return ext.lower() in [".png", ".jpg", ".jpeg"]

    @staticmethod
    def is_fbx_asset(asset_path: str) -> bool:
        _, ext = os.path.splitext(asset_path)
        return ext.lower() == ".fbx"

    @staticmethod
    def is_gltf_asset(asset_path: str) -> bool:
        _, ext = os.path.splitext(asset_path)
        return ext.lower() in [".glb", ".gltf"]

    @staticmethod
    def is_obj_asset(asset_path: str) -> bool:
        _, ext = os.path.splitext(asset_path)
        return ext.lower() == ".obj"

    @staticmethod
    def is_usd_asset(asset_path: str) -> bool:
        _, ext = os.path.splitext(asset_path)
        return ext.lower() in [".usd", ".usda", ".usdc", ".usdz", ".zeta"]

    @staticmethod
    def is_usdz_asset(asset_path: str) -> bool:
        _, ext = os.path.splitext(asset_path)
        return ext.lower() == ".usdz"

    @staticmethod
    def is_unpacked_usd_asset(asset_path: str) -> bool:
        _, ext = os.path.splitext(asset_path)
        return ext.lower() in [".usd", ".usda", ".usdc"]

    @staticmethod
    def is_editable_asset(asset_path: str) -> bool:
        return (AssetUtils.is_fbx_asset(asset_path) or
                AssetUtils.is_gltf_asset(asset_path) or
                AssetUtils.is_obj_asset(asset_path) or
                AssetUtils.is_usd_asset(asset_path))

    @staticmethod
    def is_external_asset(asset_path: str) -> bool:
        return (AssetUtils.is_fbx_asset(asset_path) or
                AssetUtils.is_gltf_asset(asset_path) or
                AssetUtils.is_obj_asset(asset_path))

    @staticmethod
    def get_all_parent_paths(asset_path: str) -> set[str]:
        current_path = asset_path
        asset_prefix = set()

        while current_path:
            asset_prefix.add(current_path)
            if current_path == "/":
                break
            else:
                current_path = os.path.dirname(current_path)

        return asset_prefix

    @staticmethod
    def is_asset_file_valid(asset_path) -> bool:
        if not asset_path:
            return False
        if not isinstance(asset_path, str):
            return False
        if not os.path.exists(asset_path):
            return False
        if not os.path.isfile(asset_path):
            return False
        if os.path.getsize(asset_path) == 0:
            return False

        return True