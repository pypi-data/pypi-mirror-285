# s3local

[![PyPI version](https://badge.fury.io/py/s3local.svg)](https://badge.fury.io/py/s3local)
[![tests](https://github.com/toyama0919/s3local/actions/workflows/tests.yml/badge.svg)](https://github.com/toyama0919/s3local/actions/workflows/tests.yml)

Cache the object in s3 to localhost.

Create a cache corresponding to s3 and automatically create a path for localhost and return it.

Once downloaded files remain in localhost as cache, the second migration download will be skipped

works on python3.6 or higher

## Settings

aws auth support following.

* environment variables
* profile(use --aws-profile option.)
* instance profile

## Examples

#### download object and list object

```bash
$ s3local download -u s3://mybucket/artifacts/ --debug
2021-05-14 11:27:13,367 DEBUG - Copying: s3://mybucket/artifacts/main.log > /Users/hiroshi.toyama/.s3local/s3/mybucket/artifacts/main.log
2021-05-14 11:27:13,367 DEBUG - Copying: s3://mybucket/artifacts/main2.log > /Users/hiroshi.toyama/.s3local/s3/mybucket/artifacts/main2.log
2021-05-14 11:27:13,367 DEBUG - Copying: s3://mybucket/artifacts/main3.log > /Users/hiroshi.toyama/.s3local/s3/mybucket/artifacts/main3.log

# next download is skip
$ s3local download -u s3://mybucket/artifacts/ --debug
2021-05-14 14:08:02,970 DEBUG - skip already exists in local: s3://mybucket/artifacts/main.log
2021-05-14 14:08:02,970 DEBUG - skip already exists in local: s3://mybucket/artifacts/main2.log
2021-05-14 14:08:02,970 DEBUG - skip already exists in local: s3://mybucket/artifacts/main3.log

# overwrite download. (not skip)
$ s3local download -u s3://mybucket/artifacts/ --debug --no-skip-exist
2021-05-14 11:27:13,367 DEBUG - Copying: s3://mybucket/artifacts/main.log > /Users/hiroshi.toyama/.s3local/s3/mybucket/artifacts/main.log
2021-05-14 11:27:13,367 DEBUG - Copying: s3://mybucket/artifacts/main2.log > /Users/hiroshi.toyama/.s3local/s3/mybucket/artifacts/main2.log
2021-05-14 11:27:13,367 DEBUG - Copying: s3://mybucket/artifacts/main3.log > /Users/hiroshi.toyama/.s3local/s3/mybucket/artifacts/main3.log
```

By default `$HOME/.s3local` is the root directory.

The format of path in local is as follows:

```
$HOME/.s3local/s3/${bucket}/${key}
```

You can change root by setting an environment variable S3LOCAL_ROOT.

```bash
$ s3local list-local -u s3://mybucket/artifacts/
/Users/hiroshi.toyama/.s3local/s3/mybucket/artifacts/main.log
/Users/hiroshi.toyama/.s3local/s3/mybucket/artifacts/main2.log
/Users/hiroshi.toyama/.s3local/s3/mybucket/artifacts/main3.log
```

#### upload object

```bash
$ s3local upload -s tox.ini -u s3://mybucket/test/
2023-05-31 10:44:08,474 INFO - Copying to s3: tox.ini => s3://mybucket/test/tox.ini
```

## Python API

### download

```python
from s3local import Downloader

s3local = Downloader("s3://mybucket/artifacts/")
list = s3local.list_local_path(download=True)
print(list)
#=> [
#     "/Users/hiroshi.toyama/.s3local/s3/mybucket/artifacts/main.log",
#     "/Users/hiroshi.toyama/.s3local/s3/mybucket/artifacts/main2.log",
#     "/Users/hiroshi.toyama/.s3local/s3/mybucket/artifacts/main3.log",
# ]

```

### upload

```python
from s3local import Uploader

s3local = Uploader("s3://mybucket/artifacts/")

uploader.upload("output/hoge.txt")
#=> s3://mybucket/artifacts/hoge.txt

uploader.upload("output")
#=> s3://mybucket/artifacts/output/hoge.txt

```

## Installation

```sh
pip install s3local
```

## CI

### install test package

```
$ ./scripts/ci.sh install
```

### test

```
$ ./scripts/ci.sh run-test
```

flake8 and black and pytest.

### release pypi

```
$ ./scripts/ci.sh release
```

git tag and pypi release.
