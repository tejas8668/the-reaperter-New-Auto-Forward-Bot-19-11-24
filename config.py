from os import getenv

class Config(object):
    API_HASH = getenv("API_HASH")
    API_ID = int(getenv("API_ID", 0))
    AS_COPY = True if getenv("AS_COPY", "True") == "True" else False
    BOT_TOKEN = getenv("BOT_TOKEN", "")
    CHANNELS = {
        "group_A": {
            "sources": ["-1001111111111", "-1002222222222"],
            "destinations": ["-1003333333333", "-1004444444444"]
        },
        "group_B": {
            "sources": ["-1005555555555", "-1006666666666"],
            "destinations": ["-1007777777777", "-1008888888888"]
        },
        "group_C": {
            "sources": ["-1009999999999", "-1001010101010"],
            "destinations": ["-1001111111112", "-1001212121212"]
        },
        "group_D": {
            "sources": ["-1001313131313", "-1001414141414"],
            "destinations": ["-1001515151515", "-1001616161616"]
        },
    }
}
