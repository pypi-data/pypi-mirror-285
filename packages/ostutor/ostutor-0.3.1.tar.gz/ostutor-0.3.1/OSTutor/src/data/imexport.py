import json
from dataclasses import dataclass
from ..dao import OptDao, InstDao, InstExtraDao, BaseDao
from ..dao.entity import InstExtra, Inst, Opt
from tqdm import tqdm

@dataclass
class ExportData:
    insts:        list = None
    opts:         list = None
    extras:       list = None

    def to_dict(self):
        return {
            'insts':        self.insts,
            'opts':         self.opts,
            'extras':       self.extras
        }


    
@dataclass
class Export:
    path: str = 'inst.json'
    def exportDatabase(self):
        # 获取全部数据
        insts = InstDao().SelectAll()
        opts = OptDao().SelectAll()
        extras = InstExtraDao().SelectAll()

        with open(self.path, 'w') as f:

            insts  = [i.to_dict() for i in tqdm(insts , desc="Exporting Inst Info")]
            extras = [i.to_dict() for i in tqdm(extras , desc="Exporting Opt Info")]
            opts   = [i.to_dict() for i in tqdm(opts , desc="Exporting Extra Info")]
            exportData = ExportData(
                insts=insts,
                opts=opts,
                extras=extras
            )
            jsonString = json.dumps(exportData.to_dict(), indent=4)
            f.write(jsonString)
                


@dataclass
class Import:
    path: str = 'inst.json'
    def importDatabase(self):
        instDao      = InstDao()
        optdao       = OptDao()
        instExtraDao = InstExtraDao()
        baseDao      = BaseDao()

        # 删除所有数据，完全替代
        instDao.DeleteAll()
        optdao.DeleteAll()
        instExtraDao.DeleteAll()

        with open(self.path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        with baseDao.connect() as (conn, cur):
            # 插入指令数据
            for i in tqdm(data['insts'], desc="Importing Inst Info"):
                insert = """
                    INSERT INTO inst(id, name, description, brief, synopsis, rpm, score, example, type, uploader) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """ 
                cur.execute(insert, (
                    i['id'],    i['name'],     i['description'], 
                    i['brief'], i['synopsis'], i['rpm'], 
                    i['score'], i['example'],  i['type'],  i['uploader']
                ))
            # 插入指令选项数据
            for i in tqdm(data['opts'], desc="Importing Opt Info"):
                cur.execute(optdao.insert, (
                     i['instId'], i['name'], i['content']
                ))

            # 插入指令额外数据
            for i in tqdm(data['extras'], desc="Importing Extra Info"):
                cur.execute(instExtraDao.insert, (
                    i['instId'], i['title'], i['text']
                ))

            baseDao.commit()
            