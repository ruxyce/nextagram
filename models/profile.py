from models.base_model import BaseModel
from models.user import User
import peewee as pw

class User_Profile(BaseModel):
    user = pw.ForeignKeyField(User, backref="profile")
    is_protected = pw.BooleanField(default=False)
    full_name = pw.CharField()
    description = pw.TextField()


# class User_Setting(BaseModel, UserMixin):
