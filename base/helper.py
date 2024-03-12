from mongodb import db


class Collection:
    User_Collection = db["User"]
    Room_Collection = db["RoomModel"]
    Account_Collection = db["Account"]
    Quiz_Collection = db["Quizzes"]
    def __init__(self):
        pass
