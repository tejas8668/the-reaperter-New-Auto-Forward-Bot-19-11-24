from os import getenv

class Config(object):
    API_HASH = getenv("API_HASH")
    API_ID = int(getenv("API_ID", 0))
    AS_COPY = True if getenv("AS_COPY", "True") == "True" else False
    BOT_TOKEN = getenv("BOT_TOKEN", "")
    CHANNELS = {
        "group_A": {
            "sources": ["-1002488212445"],
            "destinations": ["-1001837851141", "-1002015902532", "-1001871384871", "-1001904241310", "-1002222697547", "-1001896982356", "-1001816810727", "-1002080777619", "-1001968609608", "-1002012196844", "-1001984356416", "-1001906082393", "-1002024156024", "-1001772462255", "-1002314519941"]
        },
        "group_B": {
            "sources": ["-1002349374753"],
            "destinations": ["-1002117648544"]
        },
        "group_C": {
            "sources": ["-1002377412867"],
            "destinations": ["-1002208109923", "-1002461641026", "-1002332046404"]
        },
        "group_D": {
            "sources": ["-1002402818813"],
            "destinations": ["-1002426553583"]
        }
    }  # Ensure this closing brace matches the opening brace for CHANNELS
