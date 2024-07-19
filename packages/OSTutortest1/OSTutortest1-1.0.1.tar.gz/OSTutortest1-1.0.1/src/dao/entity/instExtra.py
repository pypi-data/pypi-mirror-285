from dataclasses import dataclass

@dataclass
class InstExtra:
    id:     int = None
    instId: int = None
    title:  str = None
    text:   str = None

    def to_dict(self):
        return {
            'id':     self.id,
            'instId': self.instId,
            'title':  self.title,
            'text':   self.text
        }