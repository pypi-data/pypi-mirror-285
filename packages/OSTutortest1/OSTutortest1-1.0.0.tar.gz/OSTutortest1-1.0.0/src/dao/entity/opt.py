from dataclasses import dataclass

@dataclass
class Opt:
    id:      int = None
    instId:  int = None
    name:    str = None
    content: str = None

    def to_dict(self):
        return {
            'id':      self.id,
            'name':    self.name,
            'instId':  self.instId,
            'content': self.content
        }