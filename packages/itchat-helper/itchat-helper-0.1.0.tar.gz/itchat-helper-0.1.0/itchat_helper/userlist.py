from .user import User


class UserList:
    def __init__(self, users: list[User]) -> None:
        self.__list__ = users

    def get_user_by_nickname(self, nickname: str):
        for u in self.__list__:
            if u.nickname == nickname:
                return u
        return None
    
    def __str__(self) -> str:
        return str(self.__list__)
    
    def __repr__(self) -> str:
        return str(self.__list__)
    
    # subscriptable and slice-able
    def __getitem__(self, idx):
        return self.__list__[idx]
    
     # return an iterator that can be used in for loop etc.
    def __iter__(self):
        return self.__list__.__iter__()

    def __len__(self):
        return len(self.__list__)
