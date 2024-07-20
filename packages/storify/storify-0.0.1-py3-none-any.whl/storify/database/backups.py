import os
import shutil

class Backups:
    def __init__(self, db):
        self.db = db
        self.root = db.root
        self.name = db.name

        self.max_backups = 5

    def backup(self):
        backup_id = self.latest + 1

        shutil.copy(
            self.db_path,
            os.path.join(self.backup_path, str(backup_id))
        )

        backups = self.list
        backups.reverse()

        while len(backups) > self.max_backups:

            os.remove(
                os.path.join(
                    self.root,
                    ".backups",
                    self.name,
                    str(backups[0])
                    )
                )

            del backups[0]

    # def restore(self, backup_id):
    #     path = self.get_path_of_backup(backup_id)

    @property
    def db_path(self):
        return os.path.join(self.root, "%s.mpack" % self.name)

    @property
    def backup_path(self):
        return os.path.join(self.root, ".backups", self.name)

    @property
    def list(self):
        if not os.path.exists(self.backup_path):
            os.makedirs(self.backup_path)
            return []

        backups = os.listdir(self.backup_path)
        backups = [int(i) for i in backups]
        backups.sort()
        backups.reverse()

        return backups

    @property
    def latest(self):
        backups = self.list

        if len(backups) > 0:
            return int(backups[0])
        else:
            return 0

    @property
    def last(self):
        backups = self.list

        return backups[0]

    def get_path_of_backup(self, backup_id):
        return os.path.join(self.backup_path, str(backup_id))
