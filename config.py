from os import getenv

class Config(object):
    API_HASH = getenv("API_HASH")
    API_ID = int(getenv("API_ID", 0))
    AS_COPY = True if getenv("AS_COPY", "True") == "True" else False
    BOT_TOKEN = getenv("BOT_TOKEN", "")
    CHANNELS = {
        "group_A": {
            "sources": ["-1002488212445"],
            "destinations": ["-1002328051849", "-1002387272968"]
        },
        "group_B": {
            "sources": ["-1002349374753"],
            "destinations": ["-1002280290177", "-1002387272968"]
        },
        "group_C": {
            "sources": ["-1002377412867"],
            "destinations": ["-1002416263186", "-1002387272968"]
        },
        "group_D": {
            "sources": ["-1002402818813"],
            "destinations": ["-1002387272968", "-1002387272968"]
        }
    }  # Ensure this closing brace matches the opening brace for CHANNELS
