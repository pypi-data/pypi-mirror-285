import os
from s3local.util import Util


class TestUtil(object):
    def setup_method(self, method):
        pass

    def teardown_method(self, method):
        pass

    def test_relative_files_from_dir(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        pair = Util.relative_files_from_dir(f"{dir_path}/data")
        assert pair[f"{dir_path}/data/a.txt"] == "data/a.txt"
