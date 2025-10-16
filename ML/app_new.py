import json
import numpy as np
from flask import Flask, request, jsonify
from loguru import logger
import base64
import cv2
from ultralytics import YOLO
 
app = Flask(__name__)
 
# 只处理 base64 编码图像
def read_img_cv(base64_str):
    try:
        img_data = base64.b64decode(base64_str)
        img = np.frombuffer(img_data, np.uint8)
        return cv2.imdecode(img, cv2.IMREAD_COLOR)
    except Exception:
        return None
 
def invasion(xyxy, points):
    # 检查目标框中心是否在给定区域内
    center_x, center_y = (xyxy[0] + xyxy[2]) / 2, (xyxy[1] + xyxy[3]) / 2
    return any(point[0] < center_x < point[2] and point[1] < center_y < point[3] for point in points)
 
# 设置日志记录
logger.add("./logs/{0}".format("log.log"), rotation="10 MB")
 
# 自定义标签列表
custom_labels = {
    0: '芬达',
    1: '营养快线',
    2: '加多宝',
    3: '脉动',
    4: '统一阿萨姆煎茶奶绿',
    5: '百岁山',
    6: '统一阿萨姆原味奶茶',
    7: '维他命水',
    8: '冰红茶',
    9: '果粒橙'
}
 
# 参数设置
def set_parameters():
    return {'device': 'cuda', 'port': 5000}
 
args = set_parameters()
logger.info("start load Model!")
model = YOLO('/root/autodl-fs/best_new.pt')
 
@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        try:
            data = request.get_json()
            img_object = data.get('image')
            minScore = float(data.get('minScore', 0.45))
            maxScore = float(data.get('maxScore', 1.0))
            customerID = data.get('customerID')
            imageID = data.get('imageID')
            axisall = data.get('axis', [])
 
            # 校验置信度范围
            if not (0 <= minScore <= 1 and 0 <= maxScore <= 1 and minScore <= maxScore):
                return jsonify({'customerID': customerID, 'imageID': imageID, 'code': 1, 'msg': '置信度错误', "marks": None, "result": None})
 
            # 解码图像
            img0 = read_img_cv(img_object)
            if img0 is None:
                return jsonify({'customerID': customerID, 'imageID': imageID, 'code': 1, 'msg': '图片解码出错', "marks": None, "result": None})
 
            w, h = img0.shape[:2]
            if axisall:
                axisall = [[max(0, a[0]), max(0, a[1]), min(w, a[2]), min(h, a[3])] for a in axisall]
 
            det_list = []
            try:
                # 使用YOLO模型进行预测
                annos = model(img0, conf=minScore)
                annos = annos[0].boxes.data.clone().cpu().detach().tolist()
 
                if annos:
                    for cls, *xyxy, conf in zip(np.array(annos)[:, -1], np.array(annos)[:, :-2], np.array(annos)[:, -2]):
                        category = str(int(cls))
                        # 映射到自定义标签
                        custom_category = custom_labels.get(int(cls), "未知")
                        x0, y0, x1, y1 = map(int, xyxy[0])
                        info = {"cls": custom_category, "axis": [x0, y0, x1, y1], "score": round(conf, 2)}
                        if axisall and not invasion(xyxy[0], axisall):
                            continue
                        det_list.append(info)
 
            except Exception:
                return jsonify({'customerID': customerID, 'imageID': imageID, 'code': 1, 'msg': '内部错误', "marks": None, "result": None})
 
            out = {'customerID': customerID, 'imageID': imageID, 'code': 0, 'msg': 'OK', "marks": det_list, "result": bool(det_list)}
            logger.info(f'outputs: {out}')
            return jsonify(out)
 
        except Exception:
            return jsonify({'customerID': None, 'imageID': None, 'code': 1, 'msg': '未知错误', "marks": None, "result": None})
 
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=args['port'], debug=True)
