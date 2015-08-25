from peewee import (SqliteDatabase,
                    Model,
                    CharField,
                    DateTimeField,
                    BooleanField,
                    ForeignKeyField)
import os
import datetime

DBPATH = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                      'database.sqlite')
db = SqliteDatabase(DBPATH)


class User(Model):
    username = CharField()
    displayname = CharField()
    password = CharField()
    relationship = CharField()

    def sha1hash(self, salt, string):
        """ Generate sha1 hash from salt+string
        """
        import hashlib
        return hashlib.sha1(
            '{}{}'.format(salt, string).encode('utf-8')
        ).hexdigest()

    def set_password(self, raw_password):
        """ Encrypt password in django-style and store
            set password to 'algorithm$salt$hash'
        """
        import random
        algo = 'sha1'
        salt = self.sha1hash(str(random.random()), str(random.random()))[:5]
        hsh = self.sha1hash(salt, raw_password)
        self.password = '%s$%s$%s' % (algo, salt, hsh)

    def check_password(self, raw_password):
        """
        Returns a boolean of whether the raw_password was correct. Handles
        encryption formats behind the scenes.
        """
        algo, salt, hsh = self.password.split('$')
        return hsh == self.sha1hash(salt, raw_password)


class Post(Model):
    author = ForeignKeyField(User)
    text = CharField()
    created = DateTimeField(default=datetime.datetime.now)
    filename = CharField()
    image = CharField()
    deleted = BooleanField(default=False)

    def page(self):
        """ Try to clone the paginate format:
            [["2014-08-22T14:21:00Z", null],
            "676b4679cdcd56b936a8735022015bbd"]
        """
        from flask import json
        dump = json.dumps([[self.created.isoformat() + "Z", None], self.id])
        return dump

    def get_file(self):
        return 'img/upload/' + self.filename

    class Meta:
        database = db


class Likes(Model):
    user = ForeignKeyField(User)
    post = ForeignKeyField(Post)

    class Meta:
        database = db
