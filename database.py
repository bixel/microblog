#! /usr/bin/env python2
from peewee import(SqliteDatabase,
                   TextField,
                   CharField,
                   ForeignKeyField,
                   BooleanField,
                   DateTimeField,
                   Model)
from playhouse.shortcuts import model_to_dict
import config
import datetime


db = SqliteDatabase(config.DATABASE_PATH)


class BaseModel(Model):
    def to_dict(self):
        return model_to_dict(self)

    class Meta:
        database = db


class Relationship(BaseModel):
    title = CharField()

    class Meta:
        database = db


class User(BaseModel):
    username = CharField(unique=True)
    displayname = CharField()
    password = CharField()
    relationship = ForeignKeyField(Relationship, null=True)

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

    def to_dict(self):
        return {
            'id': self.id,
            'displayname': self.displayname
        }

    class Meta:
        database = db


class Content(BaseModel):
    text = TextField()
    author = ForeignKeyField(User)
    created = DateTimeField(default=datetime.datetime.now)
    visible = BooleanField(default=True)

    def to_dict(self):
        return {
            'id': self.id,
            'text': self.text,
            'created': str(self.created),
            'author': self.author.to_dict()
        }

    class Meta:
        database = db


class Post(Content):
    image = CharField(null=True)

    def to_dict(self):
        obj = super(Post, self).to_dict()
        obj.update({'image': self.image})
        return obj


class Comment(Content):
    anchor = ForeignKeyField(Post)


class Like(BaseModel):
    user = ForeignKeyField(User)
    post = ForeignKeyField(Post)

    def to_dict(self):
        return {
            'post_id': self.post.id,
            'user_id': self.user.id
        }

    class Meta:
        database = db
        indexes = (
            (('user', 'post'), True),
        )


db.connect()
