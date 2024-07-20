import os
import time
import copy

from .dummylogger import DummyLogger
from .database import Database

class Storify:
    def __init__(self, root="data", save_interval=60, log=DummyLogger(), models=[]):
        self.root = root
        self.save_interval = save_interval
        self.log = log
        self.models = models

        self.databases = []

        if not os.path.exists(self.root):
            os.mkdir(self.root)

        if not os.path.exists(os.path.join(self.root, ".backups")):
            os.mkdir(os.path.join(self.root, ".backups"))

    def get_db(self,
               name,
               root={}):

        _root = copy.deepcopy(root)

        db = Database(name, self.root, self.log, rootdata=_root, models=self.models)
        self.databases.append(db)

        return db

    def db_exists(self, name):
        return os.path.exists(
            os.path.join(self.root, name + ".mpack")
        )

    def rename_db(self, old_name, new_name):
        """ WARNING: Dangerous to use if a DB is open! """
        # TODO: Make this safer

        old_path = os.path.join(self.root, old_name + ".mpack")
        new_path = os.path.join(self.root, new_name + ".mpack")

        os.rename(old_path, new_path)

    def remove_db(self, name):
        """ WARNING: Likely ineffective if a DB is open! """
        # TODO: Make this safer
        # TODO: Remove backups
        path = os.path.join(self.root, name + ".mpack")

        os.remove(path)

    def tick(self, force=False):
        a = len(self.databases)
        i = 0

        # Safely iterate through databases without any RuntimeErrors
        while i < a:
            db = self.databases[i]

            if db.defunct:
                i += 1

                continue

            if force:
                db.flush()
            else:
                 # Saves on a regular interval based off of self.save_interval
                if time.time() - db.last_flush > self.save_interval:
                    db.flush()

            i += 1

    def flush(self):
        self.tick(force=True)
