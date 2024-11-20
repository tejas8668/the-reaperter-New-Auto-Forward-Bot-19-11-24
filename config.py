from os import getenv

class Config(object):
    API_HASH = getenv("API_HASH")
    API_ID = int(getenv("API_ID", 0))
    AS_COPY = True if getenv("AS_COPY", "True") == "True" else False
    BOT_TOKEN = getenv("BOT_TOKEN", "")
    CHANNELS = {
        "group_A": {
            "sources": ["-1002301291753", "-1002294100731"],
            "destinations": ["-1002328051849", "-1002387272968"]
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
