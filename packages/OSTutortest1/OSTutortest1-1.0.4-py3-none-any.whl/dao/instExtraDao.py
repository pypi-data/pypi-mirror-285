from dataclasses import dataclass
from .baseDao import BaseDao
from .entity import InstExtra
from typing import List

@dataclass
class InstExtraDao(BaseDao):
    insert: str = """
        insert into inst_extra(Inst_id, title, text) values(?, ?, ?)
    """
    update: str = """
        update inst_extra set title = ?, text = ? where id = ?
    """
    delete: str = """
        delete from inst_extra where id = ?
    """
    selectAll: str = """
        select * from inst_extra
    """
    selectById: str = """
        select * from inst_extra where inst_id = ?
    """

    def Insert(self, data: InstExtra) -> int:
        """
        插入数据
        """
        with self.connect() as (conn, cur):
            cur.execute(self.insert, (
                data.instId, 
                data.title,
                data.text
            ))
            id = cur.lastrowid
            
            self.commit()
        return id
    
    def Update(self, data: InstExtra):
        """
        更新数据
        """
        with self.connect() as (conn, cur):
            cur.execute(self.update, (
                data.title,
                data.text,
                data.id,
            ))
            self.commit()
        return
    
    def Delete(self, id: int):
        """
        删除数据
        """
        with self.connect() as (conn, cur):
            cur.execute(self.delete, (
                id,
            ))
            self.commit()
        return
    
    def SelectAll(self) -> List[InstExtra]:
        """
        查询所有数据
        """
        with self.connect() as (conn, cur):
            res = cur.execute(self.selectAll)
        
            instexs = []
            for item in res:
                info = InstExtra(*item)
                instexs.append(info)

        return instexs
    
    
    def SelectById(self, id: int) -> List[InstExtra]:
        """
        根据指令id查询
        """
        with self.connect() as (conn, cur):
            res = cur.execute(self.selectById, (id,))
            
            instexs = []
            for item in res:
                info = InstExtra(*item)
                instexs.append(info)

        return instexs