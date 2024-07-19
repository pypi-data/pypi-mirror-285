from .baseDao import BaseDao
from dataclasses import dataclass
from .entity import Inst
from typing import List

@dataclass
class InstDao(BaseDao):
    insert: str = """
        INSERT INTO inst(name, description, brief, synopsis, rpm, score, example, exist, type) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """ 
    update: str = """
        UPDATE inst SET name = ?, description = ?, brief = ?, synopsis = ?, rpm = ?, score = ?, example = ?, exist = ?, type = ?
        WHERE id = ?
    """
    delete: str = """
        DELETE FROM inst WHERE id = ?
    """
    selectAll: str = """
        SELECT id, name, description, brief, synopsis, rpm, score, example, exist, type FROM inst
    """
    selectById: str = """
        SELECT * FROM inst WHERE id = ?
    """
    selectByNameAndType: str = """
        SELECT * FROM inst WHERE name = ? and type = ?
    """
    selectAllExist: str = """
        SELECT * FROM inst WHERE exist = 1
    """
    selectAllExistByType: str = """
        SELECT * FROM inst WHERE exist = 1 and type = ?
    """
    selectExistByName: str = """
        SELECT * FROM inst WHERE exist = 1 and name = ?
    """
    def Insert(self, data: Inst) -> int:
        """
        插入一条数据
        """
        with self.connect() as (conn, cur):
            cur.execute(self.insert, (
                data.name,   
                data.description,
                data.brief,
                data.synopsis,
                data.rpm,
                data.score,
                data.example,
                data.exist,
                data.type,
            ))
        
            id = cur.lastrowid
            
            self.commit()
        return id
    
    def Update(self, data: Inst):
        """
        更新一条数据
        """
        with self.connect() as (conn, cur):
            cur.execute(self.update, (
                data.name,
                data.description,
                data.brief,
                data.synopsis,
                data.rpm,
                data.score,
                data.example,
                data.exist,
                data.type,
                data.id
            ))
            
            self.commit()
        return
    
    def SelectAll(self) -> List[Inst]:
        """
        查询所有数据
        """
        with self.connect() as (conn, cur):
            res = cur.execute(self.selectAll)
        
            insts = []
            for item in res:
                info = Inst(*item)
                insts.append(info)

        return insts
    
    def SelectAllExist(self) -> List[Inst]:
        """
        查询所有存在于本地的指令数据
        """
        with self.connect() as (conn, cur):
            res = cur.execute(self.selectAllExist)
        
            insts = []
            for item in res:
                info = Inst(*item)
                insts.append(info)

        return insts
    
    def SelectAllExistByType(self, type) -> List[Inst]:
        """
        查询所有存在于本地的指令数据
        """
        with self.connect() as (conn, cur):
            res = cur.execute(self.selectAllExistByType, (type,))
        
            insts = []
            for item in res:
                info = Inst(*item)
                insts.append(info)

        return insts
    
    def SelectExistByName(self, name) -> Inst:
        """
        根据名称查询存在于本地的指令数据
        """
        with self.connect() as (conn, cur):
            res = cur.execute(self.selectExistByName, (name,))
        
            t = res.fetchone()
            
        if t == None:
            return None
            
        inst = Inst(*t)      
        return inst
    
    def SelectById(self, id: int) -> Inst:
        """
        根据id查询一条数据
        """
        with self.connect() as (conn, cur):
            res = cur.execute(self.selectById, (id,))  
            t = res.fetchone()
            
        if t == None:
            return None
            
        inst = Inst(*t)      
        return inst
    
    def SelectBriefInfoByIds(self, ids: list) -> List[Inst]:
        """
        根据id列表查询简要数据
        """
        with self.connect() as (conn, cur):
            placeholders = ', '.join('?' * len(ids))
            query = f"SELECT id, name, brief, type FROM inst WHERE id IN ({placeholders})"
            res = cur.execute(query, ids)
            
            briefInfo = []
            for item in res:
                briefInfo.append(item)   

        return briefInfo
    
    def SelectByNameAndType(self, name: str, type: str) -> Inst:
        """
        根据name与类型查询一条数据
        """
        with self.connect() as (conn, cur):
            res = cur.execute(self.selectByNameAndType, (name,type, ))
            t = res.fetchone()

        if t == None:
            return None
            
        inst = Inst(*t)      
        return inst