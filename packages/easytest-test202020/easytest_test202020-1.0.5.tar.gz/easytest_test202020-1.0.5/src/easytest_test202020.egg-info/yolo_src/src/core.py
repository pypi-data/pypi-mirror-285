import json
import os.path
import time
from ultralytics import YOLO
import os
import cv2


def inference(model_path, path_file):
    # file_name=os.path.basename(img_path)
    # json_result = {"name": file_name, "class": 1, }
    # return json_result

    model = YOLO(model_path)

    model.predict(source="./test_data/", task="detect", line_thickness=1, save_txt=True, save=True)
    # path_file = './runs/detect/train_model3/labels/'
    label_path = os.listdir(path_file)
    res = []
    for img_name in label_path:
        img = img_name.split('.')
        txt_path = './runs/detect/train_model/labels/' + img[0] + '.txt'
        with open(txt_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                val = line.split(' ')
                # print(val[0])
                res.append(int(val[0]))

    res_json = {'results': res}
    # print(res_json)
    # json_data = json.dumps(res_json)
    return res_json
    # print(json_data)
    # file = open('result.json', 'w', encoding='utf-8')
    # file = open(os.environ['RES_PATH'], 'w', encoding='utf-8')
    # file.write(json_data)
    # file.close()
    # print("json文件写入完毕")


# def inference_gpu(img_path):
#     file_name=os.path.basename(img_path)
#     img=cv2.imread(img_path)
#     print(img.shape)
#
#     """
#
#     该模块放模型推理输出 0，1，2，3
#     """
#     # time.sleep(600000)
#     a=torch.randn(size=(2,2))
#     a.cuda()
#     # time.sleep(600)



    return 1
