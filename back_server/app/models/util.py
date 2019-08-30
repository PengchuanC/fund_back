import datetime


class ModelToDict(object):
    def to_dict(self):
        items = self.__dict__
        json = {}
        for k, v in items.items():
            if k != "_sa_instance_state":
                if isinstance(v, datetime.datetime):
                    json[k] = v.strftime("%Y-%m-%d %H:%m")
                else:
                    json[k] = v
        return json
