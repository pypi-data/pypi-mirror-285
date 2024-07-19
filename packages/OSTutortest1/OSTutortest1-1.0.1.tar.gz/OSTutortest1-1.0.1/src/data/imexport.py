import json
from dataclasses import dataclass
from src.dao import OptDao, InstDao, InstExtraDao, BaseDao
from src.dao.entity import InstExtra, Inst, Opt
from tqdm import tqdm

@dataclass
class ExportData:
    id:          int = None
    name:        str = None
    description: str = None
    brief:       str = None
    synopsis:    str = None
    rpm:         str = None
    score:       str = None
    example:     str = None
    type:        str = None
    opt:         list = None
    extra:       list = None

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
            'type':        self.type,
            'opt':         self.opt,
            'extra':       self.extra
        }


    
@dataclass
class Export:
    path: str = 'inst.json'
    def exportDatabase(self):
        instDao = InstDao()
        instExtraDao = InstExtraDao()
        optDao = OptDao()

        insts = instDao.SelectAll()
        with open(self.path, 'w') as f:
            f.write('[')
            
            for index, inst in enumerate(tqdm(insts, desc="Exporting Info")):
                if index > 0:
                    # 如果不是第一个元素，前面需要加逗号
                    f.write(',\n')

                extra = instExtraDao.SelectById(inst.id)
                extra = [i.to_dict() for i in extra]
                opt   = optDao.SelectById(inst.id)
                opt   = [i.to_dict() for i in opt]
                exportData = ExportData(
                    inst.id, inst.name, inst.description, 
                    inst.brief, inst.synopsis, inst.rpm, 
                    inst.score, inst.example,  inst.type, 
                    opt, extra
                )
                jsonString = json.dumps(exportData.to_dict(), indent=4)
                f.write(jsonString)
                
            f.write(']')


@dataclass
class Import:
    path: str = 'inst.json'
    def importDatabase(self):
        optdao       = OptDao()
        instExtraDao = InstExtraDao()
        baseDao      = BaseDao()

        with open(self.path, 'r') as f:
            data = json.load(f)

            with baseDao.connect() as (conn, cur):
                for i in tqdm(data, desc="Importing Info"):
                    inst = Inst(
                                i['id'], i['name'], i['description'], 
                                i['brief'], i['synopsis'], i['rpm'], 
                                i['score'], i['example'],0, i['type']
                            )
                    instExtras = [
                        InstExtra(
                            i['id'], i['instId'], i['title'], i['text']
                        ) for i in i['extra']]
                    
                    opts = [Opt(
                        i['id'], i['instId'],i['name'], i['content']
                    ) for i in i['opt']]

                    cur.execute(f'SELECT * FROM inst WHERE id = ?', (inst.id,))
                    res = cur.fetchone()
                    if res != None:
                        cur.execute('DELETE FROM inst WHERE id = ?', (inst.id,))
                        cur.execute('DELETE FROM opt WHERE inst_id = ?', (inst.id, ))
                        cur.execute('DELETE FROM inst_extra WHERE inst_id = ?', (inst.id, ))

                    insert = """
                        INSERT INTO inst(id, name, description, brief, synopsis, rpm, score, example, exist, type) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """ 

                    cur.execute(insert, (
                        inst.id, inst.name, inst.description, 
                        inst.brief, inst.synopsis, inst.rpm, 
                        inst.score, inst.example, 0, inst.type
                    ))

                    for opt in opts:
                        cur.execute(optdao.insert, (
                            opt.instId,opt.name, opt.content
                        ))
                    for extra in instExtras: 
                        cur.execute(instExtraDao.insert, (
                            extra.instId, extra.title, extra.text
                        ))

                baseDao.commit()
            