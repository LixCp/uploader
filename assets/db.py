# database.py
from datetime import datetime, timedelta
from peewee import *
import jdatetime
from playhouse.shortcuts import ReconnectMixin
import config
class DB(ReconnectMixin, MySQLDatabase):
    pass

db = DB('uoploader', user='root', password='a8H8HI', host='localhost', port=3306, charset='utf8mb4')
class Base(Model):
    class Meta:
        database = db

class Users(Base):
    user_id = BigIntegerField(primary_key=True)
    phone = TextField(null=True)
    coin = IntegerField(default=0)
    ban = BooleanField(default=False)
    timestamp = TimestampField(null=True)
    joinDate = CharField(default=jdatetime.datetime.now().strftime('%Y/%m/%d'))
    last_large_file_upload = TimestampField(null=True)

db.connect()
db.create_tables([Users])

def get_or_create_user(user_id):
    user, created = Users.get_or_create(user_id=user_id)
    return user

def set_download_status(user_id, status):
    user = Users.get(user_id=user_id)
    user.download_status = status
    user.save()

def get_download_status(user_id):
    try:
        user = Users.get(Users.user_id == user_id)
        return user.download_status
    except Users.DoesNotExist:
        return None

def remove_download_status(user_id):
    user = Users.get(user_id=user_id)
    user.download_status = False
    user.save()

def can_upload_large_file(user_id):
    user = get_or_create_user(user_id)
    if user.last_large_file_upload:
        elapsed_time = datetime.now() - user.last_large_file_upload
        if elapsed_time < timedelta(hours=12):
            return False
    return True

def update_large_file_upload_time(user_id):
    user = get_or_create_user(user_id)
    user.last_large_file_upload = datetime.now()
    user.save()

def get_total_users():
    return Users.select().count()