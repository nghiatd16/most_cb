import json
import msgpack
class JobDescription:
    '''
        JobDescription acts as a middleman, standardizing communication between services.
        You can free to set any attribute to an JobDescription instance, but keep your attributes are simple,
        that can be converted to MessagePack format (More Detail: https://msgpack.org/)
    '''
    def __init__(self, **kwargs):
        self.attribute_names = set()
        for key in kwargs:
            setattr(self, key, kwargs[key])
            self.attribute_names.add(key)

    def add_attribute(self, name, value):
        setattr(self, name, value)
        self.attribute_names.add(name)
    
    def to_msgpack(self):
        return msgpack.packb(self.to_dict())
    
    def to_dict(self):
        data_pack = dict()
        for attr_name in self.attribute_names:
            data_pack[attr_name] = getattr(self, attr_name)
        return data_pack
    
    @classmethod
    def from_msgpack(cls, msg_packed):
        data_pack = msgpack.unpackb(msg_packed, raw=False)
        return JobDescription(**data_pack)
    
    @classmethod
    def from_dict(cls, data_pack):
        return JobDescription(**data_pack)