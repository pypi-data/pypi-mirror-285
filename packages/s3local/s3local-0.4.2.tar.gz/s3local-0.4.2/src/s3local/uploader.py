import os
import shutil

from .util import Util
from .core import Core


class Uploader(Core):
    def upload(
        self, source_path: str, skip_exist: bool = True, extra_args: dict = None
    ):
        basename = os.path.basename(source_path)

        if os.path.isfile(source_path):
            if self.prefix.endswith("/"):
                key = f"{self.prefix}{basename}"
            else:
                # change basename
                key = self.prefix

            # Check if the key exists
            objects = self.bucket.objects.filter(
                Prefix=key,
            )
            if skip_exist and self.should_skip(
                objects, key=key, source_path=source_path
            ):
                pass
            else:
                self.upload_file(source_path, key, extra_args)
        elif os.path.isdir(source_path):
            if self.recursive:
                objects = self.bucket.objects.filter(
                    Prefix=self.prefix,
                )
                pair = Util.relative_files_from_dir(directory=source_path)
                for abspath, relative_path in pair.items():
                    upload_key = f"{self.prefix}{relative_path}"

                    if skip_exist and self.should_skip(
                        objects, key=upload_key, source_path=abspath
                    ):
                        pass
                    else:
                        self.upload_file(abspath, upload_key, extra_args)
            else:
                raise "not implement"

    def upload_file(self, local_path: str, key: str, extra_args: dict = None):
        # copy local
        dst_path = os.path.join(self.root, key)
        self.logger.debug(f"Copying to local: {local_path} => {dst_path}")
        dst_dir_path = os.path.dirname(dst_path)
        os.makedirs(dst_dir_path, exist_ok=True)
        shutil.copyfile(local_path, dst_path)

        # copy s3
        self.logger.info(
            f"Copying to s3: {local_path} => s3://{self.bucket_name}/{key}"
        )
        self.bucket.upload_file(local_path, key, ExtraArgs=extra_args)

    def should_skip(self, objects_collection, key: str, source_path: str) -> bool:
        objects = [o for o in objects_collection if o.key == key]
        if len(objects) > 0:
            size = objects[0].size
            if os.path.getsize(source_path) == size:
                self.logger.info(
                    f"skip copy. match filesize ({size} byte) {source_path} > s3://{self.bucket_name}/{key}"
                )
                return True
        return False
