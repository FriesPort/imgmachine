import sqlite3
import datetime
import os

class znzz_SQLiteConnection:
    def __init__(self):
        self.connection = None

    """
     获取日志所需信息：
     id  图片绝对路径  机器检测结果  检测时间(created_time or updated_time)
    """
    def znzz_logList(self,path):
        item=[]
        query = 'select * from checklist where result_path=?'
        with znzz_SQLiteConnection.connect(self) as db:
            cursor=db.cursor()
            if isinstance(path,str):
                cursor.execute(query,(path,))
                result = cursor.fetchall()
                if result[7] is not None:
                    it={result[0],result[2],result[4],result[7]}
                if result[7] is None and result[9] is not None:
                    it={result[0],result[2],result[4],result[9]}
                else:
                    it={result[0],result[2],result[4]}
                item.append(it)
            for pa in path:
                cursor.execute(query, (pa,))
                result = cursor.fetchone()
                if result[7] is not None and result[9] is None:
                    it={result[0],result[2],result[4],result[7]}
                elif result[7] is None and result[9] is not None:
                    it={result[0],result[2],result[4],result[9]}
                elif result[7] is not None and result[9] is not None:
                    it={result[0],result[2],result[4],result[9]}
                else:
                    it={result[0],result[2],result[4]}
                item.append(it)
            return item

    #用户检测数量
    def znzz_searchCountByUser(self,userId):
        query = 'select count(*) from checklist where created_by=? or updated_by=?'
        if userId is not None:
            with znzz_SQLiteConnection.connect(self) as db:
                cursor=db.cursor()
                cursor.execute(query, (userId,userId,))
                result = cursor.fetchone()
                return result
        else:
            return 0



    #获取测试结果路径
    def znzz_List(self):
        with znzz_SQLiteConnection.connect(self) as db:
            cursor = db.cursor()
            cursor.execute("select result_path from checklist")
            result = cursor.fetchall()
            return result

    #人工标注
    def znzz_check(self,current_image_path,status):
        with znzz_SQLiteConnection.connect(self) as db:
            cursor = db.cursor()
            # 将人工检测结果标记为合格
            cursor.execute("UPDATE checklist SET manual_check_result=? WHERE absolute_path=?", (status,current_image_path,))
            db.commit()

    #登录
    def znzz_dblogin(self,znzz_username,znzz_password):
        with znzz_SQLiteConnection.connect(self) as db:
            cursor = db.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE TYPE='table'AND name='user'")
            table_exist=cursor.fetchone()
            if not table_exist:
                znzz_create_table_sql = """
                CREATE TABLE user (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    password TEXT NOT NULL,
                    description TEXT,
                    login_status TINYINT NULL 
                );
                """
                cursor.execute(znzz_create_table_sql)
                db.commit()
            cursor.execute("SELECT id FROM user where username=? and password=?", (znzz_username,znzz_password))
            user=cursor.fetchone()
            if cursor.fetchone():
                cursor.close()
                return user[0]
            else:
                cursor.close()
                return False

    #数据库连接
    def connect(self):
        try:
            self.znzz_connection = sqlite3.connect('../znzz.db')
            return self.znzz_connection
        except sqlite3.Error as e:
            print(f"Error: {e}")
            return None

    #建表
    def znzz_createTable(self):
        with znzz_SQLiteConnection.connect(self) as db:
            cursor = db.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE TYPE='table'AND name='checklist'")
            table_exist=cursor.fetchone()
            if not table_exist:
                znzz_create_table_sql = """
                        CREATE TABLE checklist (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        error_count INTEGER,
                        machine_check_result TEXT,
                        manual_check_result TEXT,
                        absolute_path TEXT,
                        detected_part_type TEXT,
                        created_by TEXT,
                        created_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_by TEXT,
                        updated_time DATETIME DEFAULT CURRENT_TIMESTAMP
                     );
                """
                cursor.execute(znzz_create_table_sql)
                db.commit()
                cursor.close()

    #获取当前登录用户信息
    def searchUser(self):
        with znzz_SQLiteConnection.connect(self) as db:
            cursor = db.cursor()
            query ="select * from user where login_status=1"
            cursor.execute(query)
            results = cursor.fetchone()
        print(results)
        return results

    #机器检测结果存储
    def znzz_saveCheckList(self,result,userId):
        with znzz_SQLiteConnection.connect(self) as db:
            cursor = db.cursor()
            if True:
                for item in result:
                    error_count = item.get('error_count')
                    machine_check_result = item.get('machine_check_result')
                    absolute_path = item.get('absolute_path')
                    detected_part_type = item.get('detected_part_type')
                    result_path = item.get('result_path')

                    #查看是否已经存在该路径的记录
                    cursor.execute("SELECT * FROM checklist WHERE absolute_path=?", (absolute_path,))
                    existing_record=cursor.fetchone()
                    if existing_record:
                        #如果存在则更新记录
                        updated_by = userId
                        updated_time = datetime.datetime.now()
                        cursor.execute("UPDATE checklist SET error_count=?, machine_check_result=?, detected_part_type=?, updated_by=?, updated_time=?, result_path=? WHERE absolute_path=?",
                                       (error_count, machine_check_result, detected_part_type, updated_by, updated_time, result_path,absolute_path))
                    else:
                        #如果不存在
                        created_by = userId
                        created_time = datetime.datetime.now()
                        cursor.execute("""INSERT INTO checklist (error_count, machine_check_result, absolute_path, detected_part_type,
                                          created_by, created_time, result_path) VALUES (?,?,?,?,?,?,?)""",
                                       (error_count, machine_check_result, absolute_path, detected_part_type,
                                        created_by, created_time, result_path))
                db.commit()




