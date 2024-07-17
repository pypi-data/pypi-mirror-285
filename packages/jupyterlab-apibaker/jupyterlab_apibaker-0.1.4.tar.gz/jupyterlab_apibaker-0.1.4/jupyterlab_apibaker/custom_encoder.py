import datetime
import json


class JSONWithDateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        try:
            if isinstance(o, datetime.datetime):
                return str(o)
        except TypeError:
            pass
        return json.JSONEncoder.default(self, o)
