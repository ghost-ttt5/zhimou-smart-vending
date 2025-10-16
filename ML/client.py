import os
import base64
import cv2
import requests
from pathlib import Path
from requests.auth import HTTPBasicAuth
from collections import Counter
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import random

# 设置输入图片文件夹和输出文件夹
input_folder = r"C:\Users\KEKE\Desktop\dachuang\input"
output_folder = r"C:\Users\KEKE\Desktop\dachuang\output"
url = "http://127.0.0.1:5000/predict"  # 你的服务器ip和端口
# url = "http://10.250.115.187:5000"  # 你的服务器ip和端口

# 确保输出文件夹存在
os.makedirs(output_folder, exist_ok=True)

# 类别颜色映射
class_colors = {
}

name_to_id = {"上好佳荷兰豆55g": 0, "菜园小饼80g": 1, "上好佳鲜虾片40g": 2, "上好佳蟹味逸族40g": 3,
              "妙脆角魔力炭烧味65g": 4, "盼盼烧烤牛排味块105g": 5, "上好佳鲜虾条40g": 6, "上好佳洋葱圈40g": 7,
              "上好佳日式鱼果海苔味50g": 8, "奇多日式牛排味90g": 9, "奇多美式火鸡味90g": 10,
              "上好佳粟米条草莓味40g": 11, "甘源蟹黄味瓜子仁75g": 12, "惠宜开心果140g": 13, "惠宜咸味花生350g": 14,
              "惠宜腰果160g": 15, "惠宜枸杞100g": 16, "惠宜地瓜干228g": 17, "惠宜泰国芒果干80g": 18,
              "惠宜黄桃果干75g": 19, "惠宜柠檬片65g": 20, "新疆和田滩枣454g": 21, "惠宜香菇100g": 22,
              "惠宜桂圆干500g": 23, "惠宜茶树菇200g": 24, "豪雄单片黑木耳150g": 25, "惠宜煮花生454g": 26,
              "惠宜黄花菜100g": 27, "洽洽凉茶瓜子150g": 28, "洽洽奶香味瓜子150g": 29, "车仔茶包绿茶50g": 30,
              "车仔茶包红茶50g": 31, "优乐美香芋味80g": 32, "优乐美红豆奶茶65g": 33, "欢泥冲调土豆粥25g": 34,
              "江中猴姑早餐米稀40g": 35, "永和豆浆甜豆浆粉210g": 36, "立顿柠檬风味茶180g": 37,
              "桂格多种莓果麦片40g": 38, "荣怡谷麦加黑米味30g": 39, "荣怡谷麦加红豆味30g": 40, "今野香辣牛肉面112g": 41,
              "今野老坛酸菜牛肉面118g": 42, "今野红烧牛肉面114g": 43, "合味道海鲜风味84g": 44,
              "康师傅白胡椒肉骨面76g": 45, "康师傅香辣牛肉面105g": 46, "康师傅香辣蒜味排骨面108g": 47,
              "康师傅藤椒牛肉面82g": 48, "华丰鸡肉三鲜伊面87g": 49, "康师傅黑胡椒牛排面104g": 50,
              "五谷道场红烧牛肉面100g": 51, "康师傅老坛酸菜牛肉面114g": 52, "Aji泡芙饼干芒果菠萝味60g": 53,
              "庆联蓝莓味夹心饼63g": 54, "庆联凤梨味夹心饼63g": 55, "庆联草莓味夹心饼63g": 56,
              "嘉顿威化饼干草莓味50g": 57, "嘉顿威化饼干柠檬味50g": 58, "爱时乐香草牛奶味50g": 59,
              "爱时乐巧克力味50g": 60, "百力滋海苔味60g": 61, "百力滋草莓牛奶味45g": 62, "雀巢脆脆鲨80g": 63,
              "纳宝帝巧克力味威化58g": 64, "桂力地中海风味面包条50g": 65, "康师傅妙芙巧克力味48g": 66,
              "爱乡亲唱片面包90g": 67, "达利园派草莓味单个装*": 68, "mini奥利奥55g": 69, "农夫山泉矿泉水550ml": 70,
              "怡宝矿泉水555ml": 71, "可口可乐零度500ml": 72, "可口可乐500ml": 73, "百事可乐600ml": 74,
              "芬达苹果味500ml": 75, "芬达橙味500ml": 76, "雪碧500ml": 77, "喜力啤酒500ml": 78, "百威啤酒600ml": 79,
              "百事可乐330ml": 80, "可口可乐330ml": 81, "王老吉310ml": 82, "茶派柚子绿茶500ml": 83,
              "茶派玫瑰荔枝红茶500ml": 84, "康师傅冰红茶250ml": 85, "加多宝250ml": 86, "RIO果酒水蜜桃味275ml": 87,
              "RIO果酒蓝玫瑰威士忌味275ml": 88, "牛栏山二锅头100ml": 89, "哈尔滨啤酒330ml": 90, "青岛啤酒330ml": 91,
              "雪花啤酒330ml": 92, "哈尔滨啤酒500ml": 93, "KELER啤酒500ml": 94, "百威啤酒500ml": 95,
              "QQ星全聪奶125ml": 96, "QQ星均膳奶125ml": 97, "娃哈哈AD钙奶220g": 98, "活力宝动力源105ml": 99,
              "旺仔牛奶复原乳250ml": 100, "伊利纯牛奶250ml": 101, "维他低糖原味豆奶250ml": 102,
              "百怡花生牛奶250ml": 103, "惠宜原味豆奶250ml": 104, "伊利优酸乳250ml": 105, "伊利早餐奶250ml": 106,
              "达利园桂圆莲子360g": 107, "银鹭冰糖百合银耳280g": 108, "喜多多什锦椰果567g": 109, "都乐菠萝块567g": 110,
              "都乐菠萝块234g": 111, "银鹭薏仁红豆粥280g": 112, "银鹭莲子玉米粥280g": 113, "银鹭紫薯紫米粥280g": 114,
              "银鹭椰奶燕麦粥280g": 115, "银鹭黑糖桂圆280g": 116, "梅林午餐肉340g": 117, "珠江桥牌豆豉鱼150g": 118,
              "古龙原味黄花鱼120g": 119, "雄鸡标椰浆140ml": 120, "德芙芒果酸奶巧克力42g": 121,
              "德芙摩卡巴旦木巧克力43g": 122, "德芙百香果白巧克力42g": 123, "MM花生牛奶巧克力豆40g": 124,
              "MM牛奶巧克力豆40g": 125, "好时牛奶巧克力40g": 126, "好时曲奇奶香白巧克力40g": 127,
              "脆香米海苔白巧克力24g": 128, "脆香米奶香白巧克力24g": 129, "士力架花生夹心巧克力51g": 130,
              "士力架燕麦花生夹心巧克力40g": 131, "士力架辣花生夹心巧克力40g": 132, "炫迈果味浪薄荷味37g": 133,
              "炫迈果味浪柠檬味37g": 134, "炫迈薄荷味21g": 135, "炫迈葡萄味21g": 136, "炫迈西瓜味21g": 137,
              "炫迈葡萄味50g": 138, "绿箭无糖薄荷糖茉莉花茶味34g": 139, "绿箭5片装15g": 140,
              "比巴卜棉花泡泡糖可乐味11g": 141, "比巴卜棉花泡泡堂葡萄味11g": 142, "星爆缤纷原果味25g": 143,
              "阿尔卑斯焦香牛奶味硬糖45g": 144, "阿尔卑斯牛奶软糖黄桃酸奶味47g": 145,
              "阿尔卑斯牛奶软糖蓝莓酸奶味47g": 146, "王老吉润喉糖28g": 147, "伊利牛奶片蓝莓味32g": 148,
              "熊博士口嚼糖草莓牛奶味52g": 149, "彩虹糖原果味45g": 150, "宝鼎天鱼陈酿米醋245ml": 151,
              "恒顺香醋340ml": 152, "太太乐鸡精200g": 153, "家乐香菇鸡茸汤料41g": 154, "惠宜辣椒粉15g": 155,
              "惠宜生姜粉15g": 156, "味好美椒盐20g": 157, "海星加碘精制盐400g": 158, "恒顺料酒500ml": 159,
              "东古味极鲜酱油150ml": 160, "东古一品鲜酱油150ml": 161, "欣和六月鲜酱油160ml": 162,
              "李施德林零度漱口水80ml": 163, "舒肤佳纯白清香沐浴露100ml": 164, "美涛定型啫喱水60ml": 165,
              "清扬男士洗发露活力运动薄荷型50ml": 166, "蓝月亮风清白兰洗衣液80g": 167, "高露洁亮白小苏打180g": 168,
              "高露洁冰爽180g": 169, "舒亮皓齿白80g": 170, "云南白药牙膏45g": 171, "舒克宝贝儿童牙刷": 172,
              "清风原木纯品金装100x3": 173, "洁柔face150x3": 174, "斑布100x3": 175, "维达婴儿150x3": 176,
              "相印小黄人150x3": 177, "清风原木纯品黑耀150x3": 178, "洁云绒触感130x3": 179, "舒洁萌印花120x2": 180,
              "相印红悦130x3": 181, "得宝苹果木味90x4": 182, "清风新韧纯品130x3": 183, "金鱼竹浆绿135x3": 184,
              "清风原木纯品150x2": 185, "洁柔face130x3": 186, "维达立体美110x3": 187, "洁柔CS单包*": 188,
              "相印小黄人单包*": 189, "清风原色单包*": 190, "相印茶语单包*": 191, "清风质感纯品单包*": 192,
              "米奇1928笔记本": 193, "广博固体胶15g": 194, "票据文件袋": 195, "晨光蜗牛改正带": 196,
              "鸿泰液体胶50g": 197, "马培德自粘性标签": 198, "东亚记号笔": 199}

for name in name_to_id.keys():
    # 生成一个随机的 RGB 颜色。
    # 为了避免颜色太深看不清，我们将随机范围设置在 50-255 之间。
    r = random.randint(50, 255)
    g = random.randint(50, 255)
    b = random.randint(50, 255)
    class_colors[name] = (r, g, b)


# 将图片转换为base64格式
def image_to_base64(image_path):
    with open(image_path, 'rb') as f:
        img_byte = f.read()
    img_b64 = base64.b64encode(img_byte)
    return img_b64.decode()


# 从接口返回的结果画框和置信度
# def draw_predictions(image, marks):
#     for mark in marks:
#         cls = mark["cls"]  # 获取类别
#         x1, y1, x2, y2 = map(int, mark["axis"])  # 获取坐标
#         score = mark["score"]  # 获取置信度
#         label = f'{cls}: {score:.2f}'  # 标注类别和置信度
#
#         # 获取类别颜色，如果没有指定颜色则使用默认颜色（白色）
#         color = class_colors.get(cls, (255, 255, 255))
#
#         # 画框
#         cv2.rectangle(image, (x1, y1), (x2, y2), color, 5)
#
#         font_scale = 0.8
#
#         # 计算标签的大小
#         label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, 2)[0]
#         label_x, label_y = x1, y1 - 10
#
#         # 检查标签是否会超出图像或框的顶部
#         if label_y - label_size[1] - 5 < 0:
#             label_y = y1 + 10  # 将标签位置调整到框的下方
#
#         # 绘制背景色以便突出显示类别标签
#         cv2.rectangle(image, (label_x, label_y - label_size[1] - 5),
#                       (label_x + label_size[0], label_y), color, -1)
#
#         # 在框上方标注类别和置信度
#         cv2.putText(image, label, (label_x, label_y - 5), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 0), 2,
#                     cv2.LINE_AA)
#
#     return image

def draw_predictions(image, marks):
    # 将 OpenCV 图像 (BGR) 转换为 PIL 图像 (RGB)
    cv_rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(cv_rgb_image)

    # 创建一个可以在图像上绘图的对象
    draw = ImageDraw.Draw(pil_image)

    # 加载支持中文的字体文件，请确保路径正确！
    # 字体大小可以根据你的图片分辨率调整
    try:
        font_path = "C:/Windows/Fonts/simsun.ttc"  # 这是一个示例路径，请修改为你自己的字体路径
        font = ImageFont.truetype(font_path, 20)
    except IOError:
        print(f"无法加载字体文件：{font_path}。请检查路径。将使用默认字体。")
        font = ImageFont.load_default()

    for mark in marks:
        cls = mark["cls"]  # 获取类别
        x1, y1, x2, y2 = map(int, mark["axis"])  # 获取坐标
        score = mark["score"]  # 获取置信度
        label = f'{cls}: {score:.2f}'  # 标注类别和置信度

        # 获取类别颜色，如果没有指定颜色则使用默认颜色（红色）
        color = class_colors.get(cls, (255, 0, 0))

        # 画框
        draw.rectangle([x1, y1, x2, y2], outline=color, width=5)

        # 计算文本框的大小
        text_bbox = draw.textbbox((0, 0), label, font=font)
        text_w = text_bbox[2] - text_bbox[0]
        text_h = text_bbox[3] - text_bbox[1]

        # 设置文本框的位置
        text_x = x1
        text_y = y1 - text_h - 5

        # 如果文本框超出图像顶部，则将其移动到检测框内部
        if text_y < 0:
            text_y = y1 + 5

        # 绘制文本背景
        draw.rectangle([text_x, text_y, text_x + text_w, text_y + text_h], fill=color)

        # 在框上方标注类别和置信度
        draw.text((text_x, text_y), label, font=font, fill=(255, 255, 255))

    # 将 PIL 图像转换回 OpenCV 图像 (BGR)
    final_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

    return final_image


def convert_to_id_count(name_to_id, data):
    """
    将商品名称->编号的映射应用到数据，转换格式为 {商品编号: 数量}

    :param name_to_id: {商品名称: 商品编号} 的映射字典
    :param data: {商品名称: 数量} 的统计结果
    :return: {商品编号: 数量} 的转换结果
    """
    id_count = {}

    for name, count in data.items():
        if name in name_to_id:  # 确保名称在映射表中
            product_id = name_to_id[name]
            id_count[product_id] = count  # 直接赋值数量

    return id_count


# 处理每一张图片
for image_name in os.listdir(input_folder):
    image_path = os.path.join(input_folder, image_name)

    # 跳过非图片文件
    if not image_name.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
        print(f"跳过非图片文件: {image_name}")
        continue

    print(f'正在处理图片: {image_name}')
    try:
        # 读取图片并转换为base64
        image_base64 = image_to_base64(image_path)

        # 构建POST请求的JSON数据
        payload = {
            "imageID": 'test.jpg',
            "minScore": 0.01,
            "maxScore": 0.99,
            "timeStamp": "1234455",
            "flexibleParams": "",
            "image": image_base64
        }

        response = requests.post(url, json=payload, timeout=10)

        print("Response status code:", response.status_code)
        # print("Response content:", response.text)

        if response.status_code == 200:
            try:
                response_data = response.json()  # 尝试解析 JSON 数据
                print("Response JSON:", response_data)
                # 初始化商品计数
                product_count = Counter()

                # 遍历 response_data 里的 `marks`
                for mark in response_data.get("marks", []):
                    product_name = mark["cls"]  # 直接获取商品名称
                    product_count[product_name] += 1  # 计数

                product_data = dict(product_count)
                # print(product_data)

                # 转换成 {商品名称: 数量} 格式
                output = convert_to_id_count(name_to_id, product_data)
                print(output)

                # 转换为 JSON 格式
                json_data = json.dumps(product_data, ensure_ascii=False, indent=4)
                print(json_data)

                # 读取原始图片
                image = cv2.imread(image_path)

                # 获取并画出预测结果
                if response_data.get("marks"):
                    image = draw_predictions(image, response_data["marks"])

                # 保存处理后的图片
                output_path = os.path.join(output_folder, image_name)
                cv2.imwrite(output_path, image)
                print(f"Processed and saved: {output_path}")
            except requests.exceptions.JSONDecodeError:
                print(f"JSON 解码失败，服务器返回内容: {response.text}")
        else:
            print(f"服务器返回错误状态码: {response.status_code}, 内容: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
    except Exception as e:
        print(f"处理图片时发生错误: {e}")