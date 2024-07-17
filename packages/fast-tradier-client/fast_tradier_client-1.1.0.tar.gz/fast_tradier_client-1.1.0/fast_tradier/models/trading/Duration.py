from enum import Enum

class Duration(str, Enum):
    Day = "day"
    Gtc = "gtc"
    Pre = "pre"
    Post = "post"