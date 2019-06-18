from models.base_model import BaseModel
from models.user import User
import peewee as pw
from config import Config
from playhouse.hybrid import hybrid_property

from ago import human

class Post(BaseModel):
    user = pw.ForeignKeyField(User, backref="posts", on_delete='cascade')
    image = pw.CharField(null=False)
    caption = pw.TextField()

    @hybrid_property
    def image_url(self):
        return Config.S3_LOCATION + 'images/' + self.image

    @hybrid_property
    def when(self):
        return human(self.created_at, 1)

    def is_liked(self, user):
        return user.id in [like.user_id for like in self.likes]

class Like(BaseModel):
    post = pw.ForeignKeyField(Post, backref="likes", on_delete='cascade')
    user = pw.ForeignKeyField(User, backref="likes", on_delete='cascade')


class AvatarKey(BaseModel):
    filename = pw.CharField(unique=True)

class ImageKey(BaseModel):
    filename = pw.CharField(unique=True)

class Comment(BaseModel):
    post = pw.ForeignKeyField(Post, backref="comments", on_delete='cascade')
    user = pw.ForeignKeyField(User, backref="comments", on_delete='cascade')
    comment = pw.TextField()

