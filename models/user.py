from models.base_model import BaseModel

import peewee as pw
from flask_login import UserMixin

from playhouse.hybrid import hybrid_property

from config import Config

class User(BaseModel, UserMixin):
    email = pw.CharField(null=False, unique=True)
    username = pw.CharField(null=False, unique=True)
    password = pw.CharField(null=False)
    avatar = pw.CharField(default='xk54cw37vcl7yjd')
    about = pw.TextField(null=True)

    def following(self):
        # query other users through the "relationship" table
        return (User
                .select()
                .join(Relationship, on=Relationship.to_user)
                .where(Relationship.from_user == self)
                .order_by(User.username))

    def followers(self):
        return (User
                .select()
                .join(Relationship, on=Relationship.from_user)
                .where(Relationship.to_user == self)
                .order_by(User.username))

    def follow(self, user_to_follow):
        relationship = Relationship.get_or_none(Relationship.from_user == self, Relationship.to_user == user_to_follow)
        if not relationship:
            Relationship.create(from_user = self, to_user = user_to_follow)

    def unfollow(self, user_to_unfollow):
        relationship = Relationship.get_or_none(Relationship.from_user == self, Relationship.to_user == user_to_unfollow)
        relationship.delete_instance()

    @hybrid_property
    def avatar_url(self):
        return Config.S3_LOCATION + 'avatars/' + self.avatar

class Relationship(BaseModel):
    from_user = pw.ForeignKeyField(User, backref='relationships', on_delete='cascade')
    to_user = pw.ForeignKeyField(User, backref='related_to', on_delete='cascade')

    class Meta:
        # `indexes` is a tuple of 2-tuples, where the 2-tuples are
        # a tuple of column names to index and a boolean indicating
        # whether the index is unique or not.
        indexes = (
            # Specify a unique multi-column index on from/to-user.
            (('from_user', 'to_user'), True),
        )

# ''.join(random.choices(string.ascii_lowercase + string.digits, k=15))