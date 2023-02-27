from peewee import Model, CharField, IntegerField, DateTimeField, BooleanField, ForeignKeyField, FloatField, \
    PrimaryKeyField, BlobField, TextField
from config import DB, DEFAULT_TIMER

from datetime import datetime


class BaseModel(Model):

    class Meta:

        database = DB


class User(BaseModel):

    tg_id = IntegerField()
    username = CharField()
    created_at = DateTimeField(default=datetime.now)
    score = IntegerField(default=0)


class GameRoom(BaseModel):

    tg_id = IntegerField()
    owner = ForeignKeyField(User, backref='gamerooms')
    created_at = DateTimeField(default=datetime.now)
    timer = IntegerField(default=DEFAULT_TIMER)
    autostart = BooleanField(default=False)
    dictionary_name = CharField(default='DEFAULT_ENG_RU_DICTIONARY')


# class Game(BaseModel):

#     gameroom_id = ForeignKeyField(GameRoom, backref='games', unique=True)
#     dictionary_name = CharField(default='TEST_ENG_RU_DICTIONARY_5000')
#     current_riddle = CharField(default='')
#     current_answer = CharField(default='')
#     created_at = DateTimeField(default=datetime.now)


class UserRoomScore(BaseModel):

    user_id = ForeignKeyField(User, backref='userroomscores')
    gameroom_id = ForeignKeyField(GameRoom)
    score = IntegerField(default=0)


DB.create_tables([User, GameRoom, UserRoomScore])
