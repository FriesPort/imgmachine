import datetime
from faker import Faker
import sqlite3
from demo.utils import dbconnection
from ultralytics import YOLO
from check import judge


faker=Faker()

class test:
    def __init__(self):
        self.test=None

    def AppController(self):
        znzz_checkResult=None
        with dbconnection.znzz_SQLiteConnection.connect() as db:
            cursor = db.cursor()
            if True:
                for item in range(10):
                    error_count = faker.random_int(min=0, max=10)
                    machine_check_result = faker.sentence()
                    manual_check_result = faker.sentence()
                    absolute_path = faker.file_path()
                    detected_part_type = faker.word()
                    created_by = faker.name()
                    created_time = faker.date_time_this_year()
                    result_path = faker.file_path()

                    # insert_query = """
                    # INSERT INTO "checklist" (
                    #     error_count, machine_check_result, manual_check_result, absolute_path, detected_part_type,
                    #     created_by, created_time, updated_by, updated_time, result_path
                    # ) VALUES (?,?,?,?,?,?,?,?,?,?);
                    # """
                    # cursor.execute(insert_query, (
                    #     error_count, machine_check_result, manual_check_result, absolute_path, detected_part_type,
                    #     created_by, created_time, updated_by, updated_time, result_path
                    # ))

                    #查看是否已经存在该路径的记录
                    cursor.execute("SELECT * FROM checklist WHERE absolute_path=?", (absolute_path,))
                    existing_record=cursor.fetchone()
                    if existing_record:
                        #如果存在则更新记录
                        updated_by = created_by
                        updated_time = datetime.datetime.now()
                        cursor.execute("UPDATE checklist SET error_count=?, machine_check_result=?, manual_check_result=?, detected_part_type=?, updated_by=?, updated_time=? WHERE absolute_path=?",
                                       (error_count, machine_check_result, manual_check_result, detected_part_type, updated_by, updated_time, absolute_path))
                    else:
                        #如果不存在
                        created_time = datetime.datetime.now()
                        cursor.execute("""INSERT INTO checklist (error_count, machine_check_result, manual_check_result, absolute_path, detected_part_type,
                                          created_by, created_time, result_path) VALUES (?,?,?,?,?,?,?,?)""",
                                       (error_count, machine_check_result, manual_check_result, absolute_path, detected_part_type,
                                        created_by, created_time, result_path))
                db.commit()

    def search(self):
        znzz_connection = sqlite3.connect('../znzz.db')
        with znzz_connection as db:
            cursor = db.cursor()
            query ="select * from user where login_status=1"
            cursor.execute(query)
            results = cursor.fetchone()
        print(results)
        return results




# test_oo=test()
# test_oo.AppController()

result = [
    {'error_count': 1, 'machine_check_result': 'fail', 'manual_check_result': None, 'absolute_path': '/path1/image1.jpg', 'detected_part_type': 'type1'},
    {'error_count': 0, 'machine_check_result': 'pass', 'manual_check_result': 'approved', 'absolute_path': '/path2/image2.jpg', 'detected_part_type': 'type2'}
]

db=dbconnection.znzz_SQLiteConnection()
db.searchUser()
#db.znzz_check("/building/measure.txt","OK")
result[0].update({'error_count': 0})
print(result)

# 加载预训练好的YOLOv8模型
model = YOLO("../check/best.pt")

# 照片路径
path = "C:/Users/11988/Documents/picture/1/新建文件夹"
img_path="./runs/detect/predict/"
best="../check/best.pt"
# path = path.replace("\\", "/")
# 进行目标检测
detection = model.predict(path, img_path, save=True, imgsz=640, line_width=1, show_conf=False)
i=1
print(detection)
judge.ngJudge(path,img_path,best)