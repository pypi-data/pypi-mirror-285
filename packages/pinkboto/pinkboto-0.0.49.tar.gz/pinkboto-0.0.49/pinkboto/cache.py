class Cache(object):
    def __init__(self, lifetime=120, folder="~/.cache/pinkboto"):
        import os

        self.lifetime = lifetime
        self.folder = os.path.expanduser(folder)

        if not os.path.exists(self.folder) and lifetime:
            os.makedirs(self.folder)

    @staticmethod
    def hashkey(*args):

        import json

        from bson import json_util

        dump = json.dumps(args, default=json_util.default, sort_keys=True)

        # import json
        # dump = json.dumps(args, sort_keys=True)

        import hashlib

        hash = hashlib.sha256(dump.encode()).hexdigest()

        return hash

    def is_old(self, *args):
        hs = self.hashkey(*args)
        filename = "%s/%s" % (self.folder, hs)

        import os.path as path
        import time

        return time.time() - path.getmtime(filename) > self.lifetime

    def exists(self, *args):
        hs = self.hashkey(*args)
        filename = "%s/%s" % (self.folder, hs)

        import os.path

        if os.path.exists(filename):
            return True
        else:
            return False

    def load(self, args):
        from pathlib import Path

        hs = self.hashkey(*args)
        file_hs = Path(self.folder, hs)
        if file_hs.exists():
            from json import JSONDecodeError, load as json_load

            with file_hs.open(mode="r") as fp:
                try:
                    content = json_load(fp)
                    return content
                except JSONDecodeError as e:
                    from pinkboto import logger

                    logger.exception(
                        "Pinkboto cache file content error: %s", extra={"error": e}
                    )
        return {}

    def save(self, value, *args):
        def json_datetime(o):
            import datetime

            if isinstance(o, datetime.datetime):
                return o.__str__()

        hs = self.hashkey(*args)
        filename = "%s/%s" % (self.folder, hs)

        import json

        with open(filename, "w") as f:
            f.write(json.dumps(value, default=json_datetime))

    def clean_cache(self):
        import os
        import shutil

        if os.path.exists(self.folder):
            shutil.rmtree(self.folder)
        os.makedirs(self.folder)

    def caching(self, fn, *args):
        if not self.lifetime:
            return fn(*args)

        if self.exists(*args) and not self.is_old(*args):
            results = self.load(args)
        else:
            results = fn(*args)
            self.save(results, *args)

        return results
