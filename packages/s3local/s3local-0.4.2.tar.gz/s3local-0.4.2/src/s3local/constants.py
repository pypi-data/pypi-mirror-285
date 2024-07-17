import pkg_resources
import os

VERSION = pkg_resources.get_distribution("s3local").version

DEFAULT_S3LOCAL_ROOT = f"{os.environ.get('HOME')}/.s3local"
