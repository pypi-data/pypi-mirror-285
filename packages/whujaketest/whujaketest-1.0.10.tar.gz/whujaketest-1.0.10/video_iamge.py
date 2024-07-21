import cv2
 
# 创建视频捕获对象，参数是视频文件的路径
cap = cv2.VideoCapture(r'C:\Users\zx\Videos\12月25日.mp4')
 
# 检查视频是否成功打开
if not cap.isOpened():
    print("Error: Could not open video.")
    exit()
 
# 通过循环读取视频的每一帧
while True:
    # 读取一帧
    ret, frame = cap.read()
    
    # 如果正确读取帧，ret为True
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break
 
    # 显示帧
    # cv2.imshow('frame', frame)
    gray_curr = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cv2.imwrite("3/vv1.png", gray_curr )
 
    # 按'q'退出循环
    if cv2.waitKey(1) == ord('q'):
        break
 
# 释放捕获的视频
cap.release()
# 销毁所有窗口
cv2.destroyAllWindows()



import cv2
import os

# 图片文件夹路径
image_folder = r'C:\Users\zx\Pictures\2'
# 输出视频文件路径
video_name = r'C:\Users\zx\Pictures\2video.mp4'

# 获取图片列表
images = [img for img in os.listdir(image_folder) if img.endswith(".png")]

# 获取第一张图片的宽度和高度
image_path = os.path.join(image_folder, images[0])
frame = cv2.imread(image_path)
height, width, layers = frame.shape

# 创建视频编码器
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
video = cv2.VideoWriter(video_name, fourcc, 30, (width, height))

# 遍历每张图片，将其添加到视频编码器中
for image in images:
    image_path = os.path.join(image_folder, image)
    frame = cv2.imread(image_path)
    video.write(frame)