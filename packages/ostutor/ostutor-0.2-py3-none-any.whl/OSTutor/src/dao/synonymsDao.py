from dataclasses import dataclass
from .baseDao import BaseDao
from .entity import Synonym
from typing import List
import re
import csv
import os

class SynonymsDao(BaseDao):
    path = os.path.dirname(os.path.abspath(__file__))
    backup_csv:  str = os.path.join(path,'../assets/csv/synonyms_data.csv')
    input_backup_csv:  str = os.path.join(path,'../assets/csv/input/synonyms_data.csv')
    backup_sql:  str = os.path.join(path,'../assets/sql/synonyms_data.sql')
    input_backup_sql:  str = os.path.join(path,'../assets/sql/input/synonyms_data.sql')

    insert: str = """
        insert into synonyms(synonym) values(?)
    """
    update: str = """
        update synonyms set synonym = ? where id = ?
    """
    delete: str = """
        delete from synonyms where id = ?
    """
    selectAll: str = """
        select * from synonyms
    """
    selectByString: str = """
        select id from synonyms where synonym like ?
        OR synonym LIKE ?
        OR synonym LIKE ?
        OR synonym = ?
    """
    selectById: str = """
        select synonym FROM synonyms WHERE id = ?
    """

    def validate_synonym(self, synonym: str) -> str:
        """
        验证输入的内容只能是英语和空格，并将其转换为小写
        """
        if not re.match("^[a-zA-Z ]*$", synonym):
            raise ValueError("Synonym can only contain English letters and spaces.")
        return synonym.lower()

    def Insert(self, synonym: str) -> int:
        """
        增加一行内容，返回增加主键
        """
        validated_synonym = self.validate_synonym(synonym)
        with self.connect() as (conn, cur):
            cur.execute(self.insert, (validated_synonym,))
            # if cur.rowcount == 0:
            #     raise ValueError(f"Error: Insert failed for id {cur.lastrowid}")
            self.commit()
            return cur.lastrowid

    def Update(self, id: int, synonym: str):
        """
        根据主键和输入的内容更改单元格内容
        如果主键不存在，则返回错误
        """
        validated_synonym = self.validate_synonym(synonym)
        with self.connect() as (conn, cur):
            # 检查主键是否存在
            cur.execute("SELECT COUNT(*) FROM synonyms WHERE id = ?", (id,))
            if cur.fetchone()[0] == 0:
                print(f"Error: No record found with id {id}")
            else:
                # 更新
                cur.execute(self.update, (validated_synonym, id))
                if cur.rowcount == 0:
                    raise ValueError(f"Error: Update failed for id {id}")
                self.commit()

    def Delete(self, id: int):
        """
        根据主键删除一行内容
        """
        with self.connect() as (conn, cur):
            cur.execute(self.delete, (id,))
            self.commit()

    def SelectAll(self) -> List[Synonym]:
        """
        查找所有内容
        """
        with self.connect() as (conn, cur):
            cur.execute(self.selectAll)
            rows = cur.fetchall()
            return [Synonym(id=row[0], synonym=row[1]) for row in rows]

    def SelectByString(self, search_str: str) -> List[int]:
        """
        根据输入的字符串，查找synonym列中包含该字符串的主键
        """
        params = (
            f"% {search_str} %",
            f"{search_str} %",
            f"% {search_str}",
            search_str
        )
        with self.connect() as (conn, cur):
            cur.execute(self.selectByString, params)
            rows = cur.fetchall()
            return [row[0] for row in rows]
        
    def SelectById(self, id: int) -> str:
        """
        根据主键id查询synonyms表中的synonym信息
        返回对应的synonym字符串
        如果找不到对应的记录，则返回空字符串
        """
        with self.connect() as (conn, cur):
            cur.execute(self.selectById, (id,))
            row = cur.fetchone()
            return row[0] if row else ""
        
    def DeleteAll(self):
        """
        删除synonyms表中的所有数据
        """
        deleteAll: str = """
            DELETE FROM synonyms
        """
        # 询问用户是否要清除现有数据
        clear_existing = input("Do you want to clear all existing data before importing? (y/n): ").lower().strip()
        
        if clear_existing == 'y':
            with self.connect() as (conn, cur):
                cur.execute(deleteAll)
                self.commit()
                print(f"All records in synonyms table have been deleted.")
            print("All existing data has been cleared.")
        elif clear_existing != 'n':
            print("Invalid input. Proceeding without clearing existing data.")

    def ExportToCSV(self):
        """
        将synonyms表中的所有数据导出到CSV文件
        """
        with self.connect() as (conn, cur):
            cur.execute(self.selectAll)
            rows = cur.fetchall()

        with open(self.backup_csv, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['id', 'synonym'])  # 写入表头
            writer.writerows(rows)
        
        print(f"Data exported to {self.backup_csv}")

    def ImportFromCSV(self):
        """
        从CSV文件导入数据到synonyms表
        """
        if not os.path.exists(self.input_backup_csv):
            print(f"Error: File {self.input_backup_csv} does not exist.")
            return

        self.DeleteAll()

        with open(self.input_backup_csv, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # 跳过表头

            insertMany: str = """
                INSERT INTO synonyms (id, synonym) VALUES (?, ?)
            """

            with self.connect() as (conn, cur):
                try:
                    cur.executemany(insertMany, reader)
                    self.commit()
                    print(f"Data imported from {self.input_backup_csv}")
                except Exception as e:
                    print(f"Error during import: {e}")
                    conn.rollback()

    def BackupTable(self):
        """
        备份synonyms表到指定路径的SQL文件
        """
        with self.connect() as (conn, cur):
            # 获取表结构
            cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='synonyms'")
            table_schema = cur.fetchone()[0]

            # 获取表数据
            cur.execute("SELECT * FROM synonyms")
            table_data = cur.fetchall()

            with open(self.backup_sql, 'w', encoding='utf-8') as f:
                # 表结构
                # f.write(f"{table_schema};\n\n")
                # 表数据
                for row in table_data:
                    # 只选择 synonym 列的值
                    synonym_value = row[1]
                    f.write(f"""INSERT INTO synonyms (synonym) VALUES ('{synonym_value.replace("'", "''")}');\n""")
        
        print(f"Synonyms表已备份到 {self.backup_sql}")

    def RestoreTable(self):
        """
        从SQL文件恢复synonyms表
        """
        if not os.path.exists(self.input_backup_sql):
            print(f"Error: Backup file {self.input_backup_sql} does not exist.")
            return
        self.DeleteAll()
        # 从备份文件读取并执行SQL语句
        with self.connect() as (conn, cur):
            with open(self.input_backup_sql, 'r') as f:
                sql_script = f.read()
                cur.executescript(sql_script)
            self.commit()
        
        print(f"Synonyms table restored from {self.input_backup_sql}")