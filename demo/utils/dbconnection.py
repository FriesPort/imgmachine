import sqlite3
import datetime
import os

class znzz_SQLiteConnection:
    def __init__(self):
        self.connection = None

    def znzz_check(self,current_image_path,status):
        with znzz_SQLiteConnection.connect(self) as db:
            cursor = db.cursor()
            # 将人工检测结果标记为合格
            cursor.execute("UPDATE checklist SET manual_check_result=? WHERE absolute_path=?", (status,current_image_path,))
            db.commit()

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
                    description TEXT 
                );
                """
                cursor.execute(znzz_create_table_sql)
                db.commit()
            cursor.execute("SELECT * FROM user where username=? and password=?", (znzz_username,znzz_password))
            if cursor.fetchone():
                cursor.close()
                return True
            else:
                cursor.close()
                return False

    def connect(self):
        try:
            self.znzz_connection = sqlite3.connect('../znzz.db')
            return self.znzz_connection
        except sqlite3.Error as e:
            print(f"Error: {e}")
            return None

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

    def searchUser(self):
        with znzz_SQLiteConnection.connect(self) as db:
            cursor = db.cursor()
            query ="select * from user where login_status=1"
            cursor.execute(query)
            results = cursor.fetchone()
        print(results)
        return results

    def znzz_saveCheckList(self,result):
        user=self.searchUser()
        with znzz_SQLiteConnection.connect(self) as db:
            cursor = db.cursor()
            if True:
                for item in result:
                    error_count = item.get('error_count')
                    machine_check_result = item.get('machine_check_result')
                    absolute_path = item.get('absolute_path')
                    detected_part_type = item.get('detected_part_type')
                    result_path = item.get('absolute_path')

                    #查看是否已经存在该路径的记录
                    cursor.execute("SELECT * FROM checklist WHERE absolute_path=?", (absolute_path,))
                    existing_record=cursor.fetchone()
                    if existing_record:
                        #如果存在则更新记录
                        updated_by = user[1]
                        updated_time = datetime.datetime.now()
                        cursor.execute("UPDATE checklist SET error_count=?, machine_check_result=?, detected_part_type=?, updated_by=?, updated_time=? WHERE absolute_path=?",
                                       (error_count, machine_check_result, detected_part_type, updated_by, updated_time, absolute_path))
                    else:
                        #如果不存在
                        created_by = user[1]
                        created_time = datetime.datetime.now()
                        cursor.execute("""INSERT INTO checklist (error_count, machine_check_result, absolute_path, detected_part_type,
                                          created_by, created_time, result_path) VALUES (?,?,?,?,?,?,?)""",
                                       (error_count, machine_check_result, absolute_path, detected_part_type,
                                        created_by, created_time, result_path))
                db.commit()




