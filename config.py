from os import getenv

class Config(object):
    API_HASH = getenv("API_HASH")
    API_ID = int(getenv("API_ID", 0))
    AS_COPY = True if getenv("AS_COPY", "True") == "True" else False
    BOT_TOKEN = getenv("BOT_TOKEN", "")
    CHANNELS = {
        "group_A": {
            "sources": ["-1002487065354"],
            "destinations": ["-1002464896968"]
        },
        "group_B": {
            "sources": ["-1002398034096"],
            "destinations": ["-1002176533426"]
        },
        "group_C": {
            "sources": ["-1002398034096"],
            "destinations": ["-1002464896968"]
        },
        "group_D": {
            "sources": ["-1002487065354"],
            "destinations": ["-1002176533426"]
        }
    }  # Ensure this closing brace matches the opening brace for CHANNELS
