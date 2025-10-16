from ultralytics import YOLO

def main():
    model = YOLO('yolov11n.pt') 

    results = model.train(
        data='data.yaml',
        epochs=100,
        imgsz=640,
        batch=16,                    
        device=0,                    

        patience=30,
        optimizer='Adam',
        lr0=0.01,
        workers=8
    )
    

    # 验证模型
    
    # 加载训练好的最佳模型
    # best_model = YOLO('runs/detect/my_first_train/weights/best.pt')
    
    # 在验证集上评估模型
    # metrics = best_model.val()
    # print("验证集mAP: ", metrics.box.map50) # 打印 mAP@50

    # 使用模型进行预测
    # results = best_model.predict(source='path/to/your/test_image.jpg', save=True)


if __name__ == '__main__':
    main()