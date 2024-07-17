import os
import glob
from .core import Core


class Downloader(Core):
    def download_file(
        self,
        key: str,
        dryrun: bool = False,
        dst_path: str = None,
    ):
        # make dir
        dst_dir_path = os.path.dirname(dst_path)
        os.makedirs(dst_dir_path, exist_ok=True)

        s3_url = f"s3://{self.bucket_name}/{key}"
        self.logger.info(f"Copying: {s3_url} > {dst_path}")
        if not dryrun:
            self.bucket.download_file(key, dst_path)
        self.download_paths.append(dst_path)

    def download(
        self, dryrun: bool = False, skip_exist: bool = True, dst_path: str = None
    ):
        if self.recursive:
            objects = self.bucket.objects.filter(
                Prefix=self.prefix,
            )
            for o in objects:
                if o.key.endswith("/"):
                    continue
                local_dst_path = (
                    f"{dst_path}/{os.path.basename(o.key)}" if dst_path else None
                ) or f"{self.root}/{o.key}"
                if not (skip_exist and self.should_skip(o.key, local_dst_path)):
                    self.download_file(
                        o.key,
                        dryrun,
                        dst_path=local_dst_path,
                    )
        else:
            local_dst_path = dst_path or f"{self.root}/{self.prefix}"
            if not (skip_exist and self.should_skip(self.prefix, local_dst_path)):
                self.download_file(self.prefix, dryrun, dst_path=local_dst_path)

    def should_skip(self, key: str, source_path: str) -> bool:
        size = self.bucket.Object(key).content_length

        if os.path.exists(source_path) and os.path.isfile(source_path):
            if os.path.getsize(source_path) == size:
                self.logger.info(
                    f"skip download. match filesize ({size} byte) s3://{self.bucket_name}/{key} > {source_path}"
                )
                return True
        return False

    def list_download_path(self):
        self.download()
        return self.download_paths

    def list_local_path(self, download: bool = False):
        if download:
            self.download()

        # Search cache only without accessing s3
        if self.recursive:
            glob_string = f"{self.local_path}**/*"
            paths = glob.glob(glob_string, recursive=True)
            paths = [x for x in paths if os.path.isfile(x)]  # file only
        else:
            paths = [self.local_path]

        return paths

    def get_local_path(self, download=False):
        if download:
            self.download()
        return self.local_path
