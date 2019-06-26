from models.base_model import BaseModel

import peewee as pw
from flask_login import UserMixin

from playhouse.hybrid import hybrid_property

from config import Config

class User(BaseModel, UserMixin):
    email = pw.CharField(null=False, unique=True)
    username = pw.CharField(null=False, unique=True)
    password = pw.CharField(null=False)
    avatar = pw.CharField(default='x8aeubacxt9jjds')
    about = pw.TextField(null=True)
    is_private = pw.BooleanField(default=False)

    @hybrid_property
    def follower_requests(self):
        return (User
                .select()
                .join(Relationship, on=Relationship.from_user)
                .where((Relationship.to_user == self) & (Relationship.approved == False))
                .order_by(User.username))

    @hybrid_property
    def following_requests(self):
        return (User
                .select()
                .join(Relationship, on=Relationship.to_user)
                .where((Relationship.from_user == self) & (Relationship.approved == False))
                .order_by(User.username))

    @hybrid_property
    def following(self):
        # query other users through the "relationship" table
        return (User
                .select()
                .join(Relationship, on=Relationship.to_user)
                .where((Relationship.from_user == self) & (Relationship.approved == True))
                .order_by(User.username))

    @hybrid_property
    def followers(self):
        return (User
                .select()
                .join(Relationship, on=Relationship.from_user)
                .where((Relationship.to_user == self) & (Relationship.approved == True))
                .order_by(User.username))

    def follow(self, user_to_follow):
        relationship = Relationship.get_or_none(Relationship.from_user == self, Relationship.to_user == user_to_follow)
        target = User.get_by_id(user_to_follow)
        if not relationship:
            if target.is_private == True:
                Relationship.create(from_user=self, to_user=user_to_follow, approved=False)
            else:
                Relationship.create(from_user=self, to_user=user_to_follow, approved=True)

    def unfollow(self, user_to_unfollow):
        relationship = Relationship.get_or_none(Relationship.from_user == self, Relationship.to_user == user_to_unfollow)
        if relationship:
            relationship.delete_instance()

    def set_public(self):
        if self.is_private == False:
            return
        self.is_private = False
        self.save()
        self.approve_all()

    def set_private(self):
        self.is_private = True
        self.save()

    def reject(self, user_id):
        self.remove_follower(user_id)

    def remove_follower(self, user_id):
        relationship = Relationship.get_or_none(Relationship.from_user == user_id, Relationship.to_user == self)
        if relationship:
            relationship.delete_instance()

    def approve(self, user_id):
        relationship = Relationship.get_or_none(Relationship.from_user == user_id, Relationship.to_user == self)
        if relationship:
            relationship.approved = True
            relationship.save()

    def approve_all(self):
        query = Relationship.update(approved=True).where(Relationship.to_user == self)    
        query.execute()

    @hybrid_property
    def avatar_url(self):
        return Config.S3_LOCATION + 'avatars/' + self.avatar

    def validate(self):
        pass

class Relationship(BaseModel):
    from_user = pw.ForeignKeyField(User, backref='relationships', on_delete='cascade')
    to_user = pw.ForeignKeyField(User, backref='related_to', on_delete='cascade')
    approved = pw.BooleanField(default=False)

    class Meta:
        # `indexes` is a tuple of 2-tuples, where the 2-tuples are
        # a tuple of column names to index and a boolean indicating
        # whether the index is unique or not.
        indexes = (
            # Specify a unique multi-column index on from/to-user.
            (('from_user', 'to_user'), True),
        )

# ''.join(random.choices(string.ascii_lowercase + string.digits, k=15))