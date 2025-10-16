from collections import Counter
import json

# 初始化商品计数
product_count = Counter()

# 遍历 YOLO 识别的对象
for result in results:
    for box in result.boxes:
        class_id = int(box.cls)  # 目标类别编号
        product_count[class_id] += 1  # 计数

# 转换成 {商品编号: 数量} 格式
product_data = dict(product_count)
print(product_data)  


json_data = json.dumps(product_data, ensure_ascii=False)
print(json_data)  # 输出 {"1": 3, "2": 5}，表示 1 号商品 3 个，2 号商品 5 个
