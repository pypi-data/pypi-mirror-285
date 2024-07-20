import os
from src import core
import time
import shutil


# os.environ["CUDA_VISIBLE_DEVICES"]="-1"

# 以下2行代码，本地测试时候不需要注释，上传代码需要注释
# os.environ.setdefault('TEST_DATA_PATH', "test_data")
# os.environ.setdefault('RES_PATH', "./")

if __name__ == '__main__':
    import json
    #需要保留以下目录接口
    os.environ['TEST_DATA_PATH'] = './test_data/predict.txt'
    os.environ['RES_PATH'] = './results.json'
    # print(os.environ['TEST_DATA_PATH'])
    Model_path = './model.pt'
    txt_path_file = './runs/detect/train_model/labels/'
    res = core.inference(Model_path, txt_path_file)
    # print(res)
    json_data = json.dumps(res)

    # print(json_data)
    # file = open('result.json', 'w', encoding='utf-8')
    file = open(os.environ['RES_PATH'], 'w', encoding='utf-8')
    file.write(json_data)
    file.close()
    print("json文件写入完毕")
    shutil.rmtree('./runs')
