from itchat.storage.templates import Chatroom as ITChatroom
from .interface import BaseModel

class User(BaseModel):
    def __init__(self,nickname:str, username:str) -> None:
        self.nickname = nickname
        self.username = username
    
    def get_username(self):
        return self.username 
    
    def get_nickname(self):
        return self.nickname
    def __str__(self) -> str:
        return str(self.to_dict())
    
    def __repr__(self) -> str:
        return self.__str__()
    

class Chatroom(User):
    @classmethod
    def build_from_ITChatroom(cls, object:ITChatroom):
        return Chatroom(object['NickName'], object['UserName'])