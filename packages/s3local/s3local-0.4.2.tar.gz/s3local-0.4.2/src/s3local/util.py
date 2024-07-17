from pathlib import Path
import os
from glob import glob
from urllib.parse import urlparse


class Util:
    @staticmethod
    def relative_files_from_dir(directory: str) -> dict:
        abspath = os.path.abspath(directory)
        parent = Path(abspath).parent
        glob_string = f"{abspath}/**/*"
        paths = glob(glob_string, recursive=True)

        results = {}
        for path in paths:
            if os.path.isfile(path):
                relative_path = Util._remove_prefix(path, str(parent) + "/")
                results[path] = relative_path
        return results

    @staticmethod
    def get_bucket_and_prefix_from_url(url: str):
        o = urlparse(url)
        return o.scheme, o.netloc, o.path.lstrip("/")

    def _remove_prefix(text: str, prefix: str) -> str:
        if text.startswith(prefix):
            return text[len(prefix) :]
        return text
