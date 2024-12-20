import os
from ultralytics import YOLO
import cv2
from demo.utils import dbconnection

# 判断是否通过
def ngJudge(path, imgPath, best, userId):
    model=YOLO(best)
    results = model.predict(source=path, save=True, imgsz=640, line_width=1, show_conf=False)
    Item=[]
    resultPath=[]
    total_count = 0  # 初始化总数计数器
    for result in results:
        # 初始化计数器
        count = 0

        # 获取类别索引
        classes = result.boxes.cls

        # 获取照片名字
        ori_img_path = result.path.replace('\\', '/')
        file_name = os.path.basename(ori_img_path)

        model.predict(line_width=1)

        # 创建存放结果的文件夹
        path = "."
        save_path = path + '/' + 'result'
        os.makedirs(save_path, exist_ok=True)

        # 获取预测后的图片路径
        basename,_ = os.path.splitext(file_name)
        new_filename = basename+'.jpg'
        img_path = imgPath + new_filename


        # 读取图片
        img = cv2.imread(img_path)
        new_img = img.copy()

        # 如果有类别名称，可以通过类别索引获取
        class_names = [result.names[int(cls)] for cls in classes]
        # 统计检测结果
        for class_name in class_names:
            type=class_name
            count += 1
            print(f"Detected: {class_name}")  # 打印检测到的类别名称
        total_count += count  # 累加总数

        x = int(new_img.shape[1] * 0.8)
        y = int(new_img.shape[0] * 0.4)

        # 判断是否通过

        if count > 0:
            cv2.putText(new_img, "NG", (x, y), cv2.FONT_HERSHEY_DUPLEX, 8.0, (14, 49, 244), 15)
            machine_check = "NG"
            print("NG")
        else:
            cv2.putText(new_img, "OK", (x, y), cv2.FONT_HERSHEY_DUPLEX, 8.0, (46, 200, 28), 15)
            machine_check = "OK"
            print("OK")

        print(machine_check)
        saveItems={
            'error_count': 1,
            'machine_check_result': machine_check,
            'absolute_path': result.path,
            'detected_part_type': type,
            'result_path': './result/'+file_name
        }
        resultPath.append('./result/'+file_name)
        Item.append(saveItems)

        cv2.imwrite(save_path + "/" + file_name, new_img)

        cv2.waitKey(0)
        cv2.destroyAllWindows()
    db=dbconnection.znzz_SQLiteConnection()
    db.znzz_saveCheckList(Item,userId)
    print(f"Total number of tags detected: {total_count}")
    return resultPath


# # 加载预训练好的YOLOv8模型
# model = YOLO("best.pt")
#
# # 照片路径
# path = "./83_0_15.jpg"
#
# path = path.replace("\\", "/")
# # 进行目标检测
# detection = model.predict(path, save=True, imgsz=640, line_width=1, show_conf=False)
#
# ngJudge(detection)
