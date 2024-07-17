from ultralytics import YOLO

# model = YOLO('yolov8.yaml')
model = YOLO('best.pt')  # load a pretrained model (recommended for training)

# Train the model
if __name__== '__main__':

    # 1 模型训练
    #  result = model.train(data="NEU_train2.yaml", epochs=1, batch=10, imgsz=224, workers=0,optimizer='SGD')
    #  result = model.train(data="NEU_train2.yaml", epochs=10, imgsz=224, device=0, verbose=True, workers=1)

    # 2 模型预测
    model.predict(source="./test_data/4.jpg", save_txt=True, save=True)


