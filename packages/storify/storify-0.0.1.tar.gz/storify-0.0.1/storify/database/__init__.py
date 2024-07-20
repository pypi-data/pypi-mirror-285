import msgpack
import os
import time
import traceback
import shutil

from ..exceptions import *
from .backups import Backups
from ..model import Model

class Database:
    def __init__(self, name, root, log, rootdata={}, models=[]):
        self.name = name
        self.root = root
        self.last_flush = time.time()
        self.data = rootdata
        self.backups = None
        self.log = log
        self.models = models

        self.destroyed = False
        self.defunct = False

        self.backups = Backups(self)

        self.load()

    def load(self, path=None):
        if not path:
            path = os.path.join(self.root, "%s.mpack" % self.name)

        if os.path.exists(path):

            try:
                self.data = self.unpack(path)
            except:
                self.log.traceback("Database '%s' corrupted, reading from backup" % self.name)

                # Read from backups
                for backup_id in self.backups.list:
                    backup_path = self.backups.get_path_of_backup(backup_id)

                    try:
                        self.log.warning("Reading from backup '%s'" % backup_id)
                        self.data = self.unpack(backup_path)

                        self.log.warning("Successfully loaded backup '%s'" % backup_id)
                        return
                    except:
                        self.log.error("Failed to read backup")
                        continue

                self.log.error("Failed to load database, throwing DatabaseLoadError")
                raise DatabaseLoadError("Could not load db:%s" % self.name)
          
    def encode_type(self, data):
        if isinstance(data, dict):
            return {walk(key): walk(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [walk(item) for item in data]
        elif isinstance(data, (str, int, float, bool, type(None))):
            return data
        elif isinstance(data, Model):
            return data._to_dict()  # Serialize Model instances
        elif isinstance(data, type) and issubclass(data, Model):
            return data._to_dict()  # Serialize subclassed Model instances
        
        return data
    
    def decode_type(self, data):
        if isinstance(data, dict) and '__model_type__' in data:

            model_type = data.pop('__model_type__')
            model_class = next((cls for cls in self.models if cls.__name__ == model_type), None)

            if model_class is None:
                raise ValueError(f"Model type '{model_type}' not found.")

            if model_class:
                try:
                    return model_class()._from_dict(data)
                except:
                    print(traceback.format_exc())
                    print("Failed to decode model", data)
                    return data

        return data

    def unpack(self, path, raw=False):
        try:
            with open(path, "rb") as f:
                blob = msgpack.unpackb(
                    f.read(),
                    object_hook=self.decode_type,
                    raw=raw
                )
        except UnicodeDecodeError:
            self.log.error("Failed to read database due to a UnicodeDecodeError. Attempting to read the database again with raw=True. Please ensure the database file is not corrupted or in an unsupported format.")
            return self.unpack(path, raw=True)

        # Walk the blob, fix bytes > str
        def walk(b):
            if isinstance(b, dict):
                new_dict = {}

                for key in b:
                    value = walk(b[key])

                    if isinstance(key, bytes):
                        key = key.decode("utf8")

                    if key in new_dict:
                        if isinstance(value, (str, bytes, list, dict)):
                            if len(value) < 1:
                                print("Skipping conflicting key %s because it's empty" % key)
                                continue

                    new_dict[key] = value

                return new_dict

            elif isinstance(b, list):
                return [walk(item) for item in b]

            elif isinstance(b, bytes):
                try:
                    return b.decode("utf8")
                except:
                    return b

            else:
                return b

        return walk(blob)
    
    def flush(self):
        if self.destroyed or self.defunct:
            return

        # Save code here
        final_path = os.path.join(self.root, "%s.mpack" % self.name)
        tmp_path = os.path.join(self.root, "%s.mpack.tmp" % self.name)

        # Backup before flushing
        if os.path.exists(final_path):
            self.log.debug("Backing up db...")
            self.backups.backup()

        try:
            with open(tmp_path, "wb") as f:
                self.log.warning("Syncing data to disk")

                blob = msgpack.packb(
                    self.data,
                    default=self.encode_type
                )

                f.write(blob)

            shutil.copy(tmp_path, final_path)
            os.remove(tmp_path)

            self.last_flush = time.time()
        except IOError:
            self.log.error(
                "An error occurred while attempting to write data to disk. "
                "This may be due to insufficient storage space. Please ensure "
                "there is adequate space available before retrying the operation."
            )

            # Try to clean up
            try:
                os.remove(tmp_path)
            except:
                pass

    def close(self):
        self.flush()

        self.data = None
        self.defunct = True

    def destroy(self):
        self.data = None

        path = os.path.join(self.root, "%s.mpack" % self.name)

        if os.path.exists(path):
            os.remove(
                path
            )

    def append(self, *args, **kwargs):
        self.data.append(*args, **kwargs)

    def remove(self, **kwargs):
        self.data.remove(**kwargs)

    def pop(self, i):
        return

    def __getitem__(self, index):
        if not (type(index) in (str, bytes)):
            raise Exception("Expected str or bytes, got %s" % type(index))
        
        val = self.data[index]

        # TODO: Recursively fix any unneccessarily bytes types

        return val

    def __setitem__(self, index, value):
        if not (type(index) in (str, bytes)):
            raise Exception("Expected str or bytes, got %s" % type(index))

        self.data[index] = value
        return self.data[index]

    def __delitem__(self, index):
        if not (type(index) in (str, bytes)):
            raise Exception("Expected str or bytes, got %s" % type(index))

        del self.data[index]

    def __iter__(self):
        for i in self.data:
            yield i

    def __len__(self):
        return len(self.data)
