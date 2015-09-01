#! /usr/bin/env python3
from peewee import(SqliteDatabase,
                   TextField,
                   CharField,
                   ForeignKeyField,
                   BooleanField,
                   DateTimeField,
                   Model)
import config
import datetime


db = SqliteDatabase(config.DATABASE_PATH)


class Relationship(Model):
    title = CharField()

    class Meta:
        database = db


class User(Model):
    username = CharField(unique=True)
    displayname = CharField()
    password = CharField()
    relationship = ForeignKeyField(Relationship)

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

    class Meta:
        database = db


class Post(Model):
    text = TextField()
    author = ForeignKeyField(User)
    created = DateTimeField(datetime.datetime.now)
    image = CharField()
    visible = BooleanField(default=True)

    class Meta:
        database = db


class Likes(Model):
    user = ForeignKeyField(User)
    post = ForeignKeyField(Post)

    class Meta:
        database = db


db.connect()
