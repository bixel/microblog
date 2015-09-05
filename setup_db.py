#! /usr/bin/env python2
import os
import sys
import config

if os.path.isfile(config.DATABASE_PATH):
    choice = input('Databse-file `{}` already exists. Delete? [y/n]: '
                   .format(config.DATABASE_PATH)).lower()
    if choice == 'y':
        os.remove(config.DATABASE_PATH)
    else:
        print('Aborting.')
        sys.exit(0)


from database import Post, User, Comment, Like, Relationship, Content, db
db.connect()
db.create_tables([
    Relationship,
    User,
    Content,
    Post,
    Comment,
    Like
])

r = Relationship.create(title='Looking for an adventure...')

u = User(username='kevin', displayname='kevin', relationship=r)
u.set_password('123')
u.save()

p = Post.create(text='Juhu ein erster, sehr sinnvoller Post!',
                author=u)

c = Comment.create(text='Was ein Quatsch.', author=u, anchor=p)

l = Like.create(user=u, post=p)

db.close()
