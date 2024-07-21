import json
import numpy as np
import cv2
from PIL import Image
import base64
import os


# **************************************************转换为包含信息的png文件
# 读取 JSON 文件
with open('task3/测试转换格式/bremen_000000_000019_leftImg8bit.json', encoding='utf-8') as f:
    data = json.load(f)

# 创建空白图片
height = data['imageHeight']
width = data['imageWidth']
label_img = np.zeros((height, width), dtype=np.uint8)

# 获取多边形点并绘制在图片上
for shape in data['shapes']:
    points = np.array(shape['points'], dtype=np.int32)
    cv2.fillPoly(label_img, [points], color=1)  # 用1来表示标注的区域

# 保存 labelids.png 文件
label_img = Image.fromarray(label_img)
label_img.save('task3/测试转换格式/labelids.png')




import cv2
import numpy as np
from PIL import Image
import json


# **************************************************将png文件转换回json文件
# 读取 labelids.png 文件
label_img = Image.open('task3/测试转换格式/labelids.png')
label_img = np.array(label_img)

# 查找所有标注的多边形
contours, _ = cv2.findContours(label_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)


# 创建新的 JSON 数据结构
new_data = {
    "version": "5.5.0",
    "flags": {},
    "shapes": [],
    "imagePath": "人工智能训练师\\task3\\dataset\\leftImg8bit_trainvaltest\\leftImg8bit\\train\\bremen_000000_000019_leftImg8bit.png",
    "imageData": None,  # 可以重新添加 base64 编码的图像数据
    "imageHeight": height,
    "imageWidth": width
}

# 设置多边形近似的精度参数
epsilon = 5  # 可以调整此值以减少或增加点数

# 添加多边形信息到 JSON 数据结构
for contour in contours:
    # 使用cv2.approxPolyDP来简化多边形
    approx = cv2.approxPolyDP(contour, epsilon, True)
    approx = approx.squeeze().tolist()
    shape = {
        "label": "car",
        "points": approx,
        "group_id": None,
        "description": "",
        "shape_type": "polygon",
        "flags": {},
        "mask": None
    }
    new_data['shapes'].append(shape)
# 保存新的 JSON 文件
with open('task3/测试转换格式/converted_bremen_000000_000019_leftImg8bit.json', 'w') as f:
    json.dump(new_data, f, ensure_ascii=False, indent=4)





# # **************************************************json文件数据转换成原始图像
# 读取 JSON 文件，指定编码为 UTF-8
json_path = 'task3/测试转换格式/bremen_000000_000019_leftImg8bit.json'
output_image_path = 'task3/测试转换格式/converted_image.png'

if not os.path.exists(json_path):
    raise FileNotFoundError(f"JSON file not found: {json_path}")

with open(json_path, encoding='utf-8') as f:
    data = json.load(f)

# 提取并解码 imageData
image_data_base64 = data.get('imageData', None)
if image_data_base64 is None:
    raise ValueError("No imageData found in the JSON file.")

# 解码 base64 数据
image_data_decoded = base64.b64decode(image_data_base64)

# 将解码后的数据保存为 PNG 文件
with open(output_image_path, 'wb') as image_file:
    image_file.write(image_data_decoded)