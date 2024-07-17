from boto3.session import Session
import os
import shutil

from .logger import get_logger
from .util import Util
from . import constants


class Core:
    def __init__(
        self,
        url: str,
        root: str = (os.environ.get("S3LOCAL_ROOT") or constants.DEFAULT_S3LOCAL_ROOT),
        aws_profile: str = None,
        logger=get_logger(),
    ):
        scheme, bucket_name, prefix = Util.get_bucket_and_prefix_from_url(url)
        self.bucket_name = bucket_name
        self.prefix = prefix
        self.recursive = True if prefix.endswith("/") else False

        self.root = os.path.join(root, scheme, bucket_name)
        os.makedirs(self.root, exist_ok=True)
        self.local_path = os.path.join(self.root, prefix)
        self.bucket = (
            (Session() if aws_profile is None else Session(profile_name=aws_profile))
            .resource("s3")
            .Bucket(bucket_name)
        )
        self.logger = logger
        self.download_paths = []

    def get_local_root(self) -> str:
        return self.root

    def delete(self):
        self.logger.info(f"delete => s3://{self.bucket_name}/{self.prefix}")
        self.logger.debug(f"delete => {self.local_path}")
        if self.recursive:
            shutil.rmtree(self.local_path)
            self.bucket.objects.filter(
                Prefix=self.prefix,
            ).delete()
        else:
            os.remove(self.local_path)
            self.bucket.delete_object(
                Key=self.prefix,
            )
