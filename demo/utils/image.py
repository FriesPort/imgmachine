import base64
import io

import numpy as np
import PIL.ExifTags
import PIL.Image
import PIL.ImageOps


# 将图像数据转换为PIL图像对象
def img_data_to_pil(img_data):
    f = io.BytesIO()
    f.write(img_data)
    img_pil = PIL.Image.open(f)
    return img_pil


# 将图像数据转换为NumPy数组
def img_data_to_arr(img_data):
    img_pil = img_data_to_pil(img_data)  # 先转换为PIL图像对象
    img_arr = np.array(img_pil)  # 再转换为NumPy数组
    return img_arr


# 将Base64编码的图像数据转换为NumPy数组
def img_b64_to_arr(img_b64):
    img_data = base64.b64decode(img_b64)  # Base64解码
    img_arr = img_data_to_arr(img_data)  # 转换为NumPy数组
    return img_arr


# 将PIL图像对象转换为图像数据
def img_pil_to_data(img_pil):
    f = io.BytesIO()
    img_pil.save(f, format="PNG")  # 保存为PNG格式
    img_data = f.getvalue()  # 获取图像数据
    return img_data


# 将NumPy数组转换为Base64编码的字符串
def img_arr_to_b64(img_arr):
    img_data = img_arr_to_data(img_arr)  # 先转换为图像数据
    img_b64 = base64.b64encode(img_data).decode("utf-8")  # Base64编码
    return img_b64


# 将NumPy数组转换为图像数据
def img_arr_to_data(img_arr):
    img_pil = PIL.Image.fromarray(img_arr)  # 从NumPy数组创建PIL图像对象
    img_data = img_pil_to_data(img_pil)  # 转换为图像数据
    return img_data


# 将图像数据转换为PNG格式的图像数据
def img_data_to_png_data(img_data):
    with io.BytesIO() as f:
        f.write(img_data)
        img = PIL.Image.open(f)  # 打开图像

        with io.BytesIO() as f:  # 再次使用BytesIO保存PNG格式
            img.save(f, "PNG")
            f.seek(0)
            return f.read()  # 返回PNG格式的图像数据


# 将Qt图像转换为NumPy数组
def img_qt_to_arr(img_qt):
    w, h, d = img_qt.size().width(), img_qt.size().height(), img_qt.depth()  # 获取图像尺寸和深度
    bytes_ = img_qt.bits().asstring(w * h * d // 8)  # 获取图像字节数据
    img_arr = np.frombuffer(bytes_, dtype=np.uint8).reshape((h, w, d // 8))  # 转换为NumPy数组
    return img_arr


# 应用图像的EXIF方向信息进行旋转和翻转
def apply_exif_orientation(image):
    try:
        exif = image._getexif()  # 尝试获取EXIF信息
    except AttributeError:
        exif = None

    if exif is None:
        return image  # 如果没有EXIF信息，直接返回图像

    exif = {PIL.ExifTags.TAGS[k]: v for k, v in exif.items() if k in PIL.ExifTags.TAGS}  # 格式化EXIF信息

    orientation = exif.get("Orientation", None)  # 获取方向信息

    # 根据方向信息进行相应的旋转和翻转操作
    if orientation == 1:
        # 不进行任何操作
        return image
    elif orientation == 2:
        # 从左到右镜像
        return PIL.ImageOps.mirror(image)
    elif orientation == 3:
        # 旋转180度
        return image.transpose(PIL.Image.ROTATE_180)
    elif orientation == 4:
        # 从上到下镜像
        return PIL.ImageOps.flip(image)
    elif orientation == 5:
        # 从上到左镜像
        return PIL.ImageOps.mirror(image.transpose(PIL.Image.ROTATE_270))
    elif orientation == 6:
        # 旋转270度
        return image.transpose(PIL.Image.ROTATE_270)
    elif orientation == 7:
        # 从上到右镜像
        return PIL.ImageOps.mirror(image.transpose(PIL.Image.ROTATE_90))
    elif orientation == 8:
        # 旋转90度
        return image.transpose(PIL.Image.ROTATE_90)
    else:
        return image