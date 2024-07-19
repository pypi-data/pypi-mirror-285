from dataclasses import dataclass

@dataclass
class Inst:
    id:          int = None
    name:        str = None
    description: str = None
    brief:       str = None
    synopsis:    str = None
    rpm:         str = None
    score:       str = None
    example:     str = None
    exist:       int = None
    type:        str = None

    def to_dict(self):
        return {
            'id':          self.id,
            'name':        self.name,
            'description': self.description,
            'brief':       self.brief,
            'synopsis':    self.synopsis,
            'rpm':         self.rpm,
            'score':       self.score,
            'example':     self.example,
            'exist':       self.exist,
            'type':        self.type
        }