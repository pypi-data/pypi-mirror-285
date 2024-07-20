import os
import json
import glob
from tqdm import tqdm


def convert_labelme_to_yolo(json_path, out_txt_path, name_class_path):

    json_list = glob.glob(json_path + '/*.json')

    for json_path in tqdm(json_list):
        with open(json_path, "r") as f_json:
            json_data = json.loads(f_json.read())
        infos = json_data['shapes']
        if len(infos) == 0:
            continue
        img_w = json_data['imageWidth']
        img_h = json_data['imageHeight']

        txt_name = os.path.basename(json_path).split('.')[0] + '.txt'
        txt_path = os.path.join(out_txt_path, txt_name)
        file = open(txt_path, 'w')

        segmentation = []
        corr_xy = []
        cls_names = []

        with open(name_class_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                val = line.split(' ')
                cls_names.append(val[0])

        for label in infos:
            points = label['points']
            names = label['label']
            cls_id = [i for i, name in enumerate(cls_names) if name == names]

            for p in points:
                segmentation.append(int(p[0]))
                segmentation.append(int(p[1]))

            for i, cor in enumerate(segmentation):
                if i % 2 == 0:
                    cor_y = cor / img_h / 1.0
                    corr_xy.append(cor_y)
                else:
                    cor_x = cor / img_w / 1.0
                    corr_xy.append(cor_x)

            final_info = str(cls_id[0]) + ' ' + ' '.join([str(i) for i in corr_xy]) + '\n'
            file.write(final_info)
        file.close()


if __name__ == "__main__":
    json_path = './data_test'  # labelme出来的标签路径
    out_txt_path = './data_test/labels'  # 转换完后Yolo格式输出的路径
    name_class_path = './data_test/names.txt'  # 数据集字典
    # 示例
    # bus 0

    convert_labelme_to_yolo(json_path, out_txt_path, name_class_path)
