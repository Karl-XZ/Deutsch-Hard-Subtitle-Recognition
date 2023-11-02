from  PIL import  Image
import pytesseract
import  cv2 as cv
import base64
import os
import cv2
import requests
from fuzzywuzzy import fuzz 
import re
import string
import time


# 记录开始时间
start_time = time.time()


def is_whitespace(s):
    # 使用字符串的内置方法isspace()来检查字符串是否只包含空白字符
    return s.isspace()

def remove_punctuation_lines(text):
    # 将文本按行分割
    lines = text.split('\n')
    
    # 初始化一个空列表，用于存储非标点符号行
    non_punctuation_lines = []

    for line in lines:
        # 去除行两端的空白字符
        line = line.strip()
        
        # 检查行是否只包含标点符号
        if all(char in string.punctuation or char.isspace() for char in line):
            continue  # 如果是只有标点符号的行，跳过
        else:
            non_punctuation_lines.append(line)

    # 将非标点符号行重新组合为一个字符串
    result = '\n'.join(non_punctuation_lines)
    
    return result

def remove_digit_only_lines(text):
    # 将文本拆分为行
    lines = text.split('\n')
    
    # 用于存储结果的列表
    result = []
    
    # 遍历每一行
    for line in lines:
        # 如果该行不仅由数字组成，则将其添加到结果列表中
        if not line.strip().isdigit():
            result.append(line)
    
    # 重新组合非数字行并返回
    cleaned_text = '\n'.join(result)
    return cleaned_text

def remove_symbol_lines(text_lines):
    cleaned_lines = []
    for line in text_lines:
        # 使用正则表达式检查行中是否只包含符号字符
        if not re.match(r'^[!@#$%^&*()_+=\[\]{};:\'",.<>/?\\|`~-]+$', line):
            cleaned_lines.append(line)
    return cleaned_lines

def remove_lines_with_only_uppercase(text):
    lines = text.split('\n')  # 将文本拆分成行
    new_lines = []  # 存储不包含只有大写字母的行

    for line in lines:
        # 如果该行不只包含大写字母，将其添加到新行列表中
        if not line.isupper():
            new_lines.append(line)

    # 重新构建文本
    new_text = '\n'.join(new_lines)

    return new_text

def remove_short_lines(input_str):
    # 将输入字符串拆分成行

    lines = input_str.split('\n')
    
    # 使用列表推导来筛选出长度大于三的行
    filtered_lines = [line for line in lines if len(line) > 3]
    
    # 将筛选后的行重新组合成字符串
    result_str = '\n'.join(filtered_lines)
    
    return result_str

def filter_text(text):
    # 将文本拆分为行
    lines = text.split('\n')

    # 初始化一个新的文本结果
    filtered_text = []

    for line in lines:
        # 拆分每行为单词
        words = line.split()

        # 检查每个单词
        should_include_line = True
        for word in words:
            if (word.isupper() or len(word) < 3):
                should_include_line = False
                break

            if (word.isupper() and len(word) < 3):
                should_include_line = False
                break
        # 如果该行应该包含，请将其添加到结果中
        if should_include_line:
            filtered_text.append(line)

    # 将结果合并为一个字符串
    result = '\n'.join(filtered_text)

    return result



def frames_to_time(frames, frame_rate ):
    # 计算总秒数
    total_seconds = frames / frame_rate
    
    # 计算小时、分钟和秒
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)
    
    # 计算毫秒
    milliseconds = int((total_seconds % 1) * 1000)
    
    # 格式化为 "00:00:00,000" 格式
    time_str = "{:02d}:{:02d}:{:02d},{:03d}".format(hours, minutes, seconds, milliseconds)
    
    return time_str
 
##img_path='C:/Users/Administrator/Pictures/1306240.jpg'
 
# img_path='orgin.jpg'
 
# img_path='F:/fb/hpop.jpg'
 
# 依赖opencv
##img=cv.imread(img_path)
##text=pytesseract.image_to_string(Image.fromarray(img))
 
 
# 不依赖opencv写法
# text=pytesseract.image_to_string(Image.open(img_path))
 
 
#print(text)


print('start')

def remove_empty_lines(input_string):
    lines = input_string.split('\n')
    # 使用列表推导式来过滤掉空白行
    non_empty_lines = [line for line in lines if line.strip() != ""]
    # 重新连接非空行
    result_string = '\n'.join(non_empty_lines)
    return result_string

def detect_and_recognize_subtitles(image_path):
    # 读取图像
    image = cv2.imread(image_path)

    # 将图像转换为灰度图像
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 对灰度图像应用中值滤波以降噪
    denoised_image = cv2.medianBlur(gray_image, 5)

    # 二值化图像，以便更容易识别文本
    _, binary_image = cv2.threshold(denoised_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # 查找轮廓
    contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 筛选出适合作为字幕的轮廓
    subtitle_contours = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        area = cv2.contourArea(contour)
        if h > 10 and w > 10 and area > 100:
            subtitle_contours.append(contour)

    # 在原始图像上绘制找到的字幕轮廓
    for contour in subtitle_contours:
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # 保存带有字幕框的图像
    cv2.imwrite( 'output_image.png' , image)

    # 从带有字幕框的图像中提取文本
    result=pytesseract.image_to_string(Image.fromarray(image))

    return result


# 要提取视频的文件名，隐藏后缀
print("请将视频文件与程序放在同一文件夹下 ")
sourceFileName = input("请输入视频文件名（mp4文件，不加后缀）: ")
y1 = 860
y2 = 1080
x1 = 000
x2 = 1920

# 在这里把后缀接上
workpath = os.getcwd()
video_path = os.path.join( workpath , sourceFileName + '.mp4')
cap = cv2.VideoCapture(video_path)
if not os.path.exists(video_path):
    print("未找到此文件，请检查文件名是否有误并重启本程序")
    exit()
if not cap.isOpened():
    print("无法打开视频文件")
else:
    # 获取视频的帧宽度和帧高度
    frame_width = int(cap.get(3))  # 获取帧宽度
    frame_height = int(cap.get(4))  # 获取帧高度
    frame_rate = int(cap.get(cv2.CAP_PROP_FPS))
    #print(frame_rate)
        
grose = input("是否修改字幕识别区域（默认为画面大小1920*1080的下五分之一区域，本视频为" + str(frame_width) + "*" + str(frame_height) + "，若要修改请输入y，否则直接回车即可）: ")
if grose == 'y':
    print("请修改字幕识别区域（像素单位从上到下，从左到右，（不要超过画面本身大小会报错！）） ")
    y1 = input("请输入上半像素高度:")
    y2 = input("请输入下半像素高度:")
    x1 = input("请输入左半像素宽度:")
    x2 = input("请输入右半像素宽度:")
times = 0
# 提取视频的频率，每10帧提取一个
#####  在！  这！  里！  #####
frameFrequency = 1
# 输出图片到当前目录video文件夹下
outPutDirName = workpath + '/video/' + sourceFileName + '/'
    
if not os.path.exists(outPutDirName):
    # 如果文件目录不存在则创建目录
    os.makedirs(outPutDirName)
camera = cv2.VideoCapture(video_path)
while True:
    times += 1
    res, image = camera.read()
    if not res:
        print('not res , not image')
            
        break
    if times % frameFrequency == 0:
        cv2.imwrite(outPutDirName + str(times) + '.jpg', image)  #文件目录下将输出的图片名字命名为10.jpg这种形式
        print(outPutDirName + str(times) + '.jpg')
        t = times
print( t )
print('图片提取结束')

times = 0
time_format = "00:00:00,000"
time_formatlast = "00:00:00,000"
# 提取视频的频率，每10帧提取一个
desktop_path = workpath + "/"  # 新创建的txt文件的存放路径

existing_files = os.listdir(desktop_path)
file_name = sourceFileName + ".txt"
counter = 0
while file_name in existing_files:
    counter += 1
    file_name = sourceFileName + '字幕输出' + str(counter) + ".txt"

full_path = desktop_path + file_name 
last = str('0')
i = 0
a = 1
while True:
    times += frameFrequency
    res, image = camera.read()
        
    #file = open(full_path, 'a+')

    if times == t:
        print('not res , not image')
        break
    img_path= outPutDirName + str(times) + '.jpg'
    print(img_path)


    img=cv.imread(img_path)
    cropped = img[int(y1):int(y2), int(x1):int(x2)]


    imgray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
    thresh = 200
    ret, binary = cv2.threshold(imgray, thresh, 255, cv2.THRESH_BINARY)  # 输入灰度图，输出二值图
    binary1 = cv2.bitwise_not(binary)  # 取反
    ##config = ('-l chi_sim --oem 1 --psm 3')
    ##text=pytesseract.image_to_string(Image.fromarray(binary1), config=config)

    text=pytesseract.image_to_string(Image.fromarray(binary1))
    text = remove_empty_lines(text)
    result_string = "".join(text)
    text = remove_punctuation_lines(result_string) 
    text = remove_short_lines(text)
    text = remove_digit_only_lines(text)
    text = remove_lines_with_only_uppercase(text)
    print(text)
    #text = filter_text(text)
    text1 = text
    text2 = last
    similarity_ratio = fuzz.ratio(text1, text2)
    if similarity_ratio > 70 or len(text) < 3 :
        #print(text)
        print('same')
    else:
        if is_whitespace(text) :
            time_format = frames_to_time(total_frames)
            time_formatlast = str(time_format)
            print('null')
         #with open(full_path, 'a+') as f:
            #f.write( text +'\n')
         #f.close()2
        else:
            print(text)
            total_frames = times
            #time_format = frames_to_time(total_frames)
            total_seconds = total_frames / frame_rate
            print(total_seconds)
            
    
            # 计算小时、分钟和秒
            hours = int(total_seconds // 3600)
            minutes = int((total_seconds % 3600) // 60)
            seconds = int(total_seconds % 60)
    
            # 计算毫秒
            milliseconds = int((total_seconds % 1) * 1000)
    
            # 格式化为 "00:00:00,000" 格式
            time_format = "{:02d}:{:02d}:{:02d},{:03d}".format(hours, minutes, seconds, milliseconds)
            file = open(full_path, 'a+',encoding='utf-8')
            file.write(str(i))
            file.write('\n')
            file.write( str(time_formatlast) + ' --> '+ str(time_format) )
            file.write('\n')
            file.write(last)
            file.write('\n')
            file.write('\n')
            print( str(time_formatlast) + ' --> '+ str(time_format) )
            print(str(times))
            print(outPutDirName + str(times) + '----srt')
            i += 1
            last = text
            time_formatlast = str(time_format)
        #file.write(
                   #"1"
                   #"00:00:00,599 --> 00:00:04,259"
                   #text
                   #""
                   #)
        #file.close()
           
        
        #print(text)
        #cv2.imwrite(outPutDirName + str(times) + '.jpg', image)  #文件目录下将输出的图片名字命名为10.jpg这种形式
        #print(outPutDirName + str(times) + '----srt')
with open( full_path , 'r',encoding='utf-8') as fileend:
    lines = fileend.readlines()

with open( full_path , 'w',encoding='utf-8') as fileend:
    fileend.writelines(lines[4:]) 

# 记录结束时间
end_time = time.time()

# 计算程序的运行时间
execution_time = end_time - start_time

# 打印运行时间
print(f"程序运行时间: {execution_time} 秒")
print("按下任意键退出...")
input()  # 等待用户按下任意键
