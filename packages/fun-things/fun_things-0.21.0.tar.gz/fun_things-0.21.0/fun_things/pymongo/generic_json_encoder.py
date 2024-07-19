from datetime import datetime
from json import JSONEncoder

from bson import ObjectId


class GenericJSONEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)

        if isinstance(o, datetime):
            return o.isoformat()

        return JSONEncoder.default(self, o)
