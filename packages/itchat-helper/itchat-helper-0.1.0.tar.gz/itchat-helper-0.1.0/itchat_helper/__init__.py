import itchat
from .user import Chatroom
from .userlist import UserList
from threading import Thread
import time

class ICHelper:
    
    def check_login(self, timer=5):
        def work():
            while True:
                print(itchat.check_login())
                time.sleep(timer)
        Thread(target=work).start()
    
    def login(self, hot_reload=False, picDir='qrcode.png', new_thread=False,login_callback=None):
        def _login(hot_reload, picDir):
           itchat.auto_login(hotReload=hot_reload, picDir=picDir,loginCallback=login_callback)  
           
        if new_thread:
            t = Thread(target=_login, args=(hot_reload, picDir))
            t.start()
            return t
        else:
            _login(hot_reload, picDir)
    
    

    def get_chatrooms(self):
        # 获取所有群组
        chatrooms = itchat.get_chatrooms()
        return UserList([Chatroom.build_from_ITChatroom(x) for x in chatrooms])
    
    def send_chatroom_msg(self,msg:str, chatroom_nickname:str):
        chatrooms = self.get_chatrooms()
        room = chatrooms.get_user_by_nickname(chatroom_nickname)
        if room:
            itchat.send_msg(msg, toUserName=room.get_username())
            return True
        else:
            return False
    
    def logout(self):
        itchat.logout()
            
    
    
        
    