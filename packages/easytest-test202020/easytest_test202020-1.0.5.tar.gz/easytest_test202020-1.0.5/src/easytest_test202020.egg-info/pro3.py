# 切换清华源
# 1、临时使用
# pip install -i https://pypi.tuna.tsinghua.edu.cn/simple some-package
# 2、永久更改pip源
# 升级 pip 到最新的版本 (>=10.0.0) 后进行配置：
# pip install pip -U
# python -m pip install --upgrade pip
# pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
# 如果您到 pip 默认源的网络连接较差，临时使用镜像站来升级 pip：
# pip install -i https://pypi.tuna.tsinghua.edu.cn/simple pip -U
# 3、查看当前源列表
# pip config list
#
#
# 4 安装ultralytics
# pip3 freeze > requirements.txt
#
# 方式一：
#  pip install ultralytics -i  https://pypi.tuna.tsinghua.edu.cn/simple/
# 方式二：
# pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn ultralytics
#
# pandas


import matplotlib
from ultralytics import YOLO
# Load a model
model = YOLO('yolov8.yaml')  # load a pretrained model (recommended for training)
# model = YOLO('yolov8s.pt')  # load a pretrained model (recommended for training)
if __name__ == '__main__':
    # model.train(data="NEU_train.yaml", epochs=10, imgsz=104, device=0, verbose=True, batch=2,optimizer='SGD')
    # result = model.train(data="train2017.yaml", epochs=5,  imgsz=224, device=0, workers=0, optimizer='SGD')
    # result = model.train(data="train2017.yaml", epochs=5, batch=10, imgsz=640, workers=0, optimizer='SGD')
    # result = model.train(data="../src/train2017.yaml", epochs=10, imgsz=224, device=0, verbose=True, workers=1)
    result = model.train(data="train2017.yaml", epochs=10, imgsz=224,  verbose=True, workers=1, optimizer='SGD')
    model.val()

    # 测试模型
    matplotlib.use( "TkAgg")
    #加载训练好的模型
    model = YOLO('models/best.pt')
    # 对验证集进行评估
    metrics = model.val(data = 'datasets/SteelData/data.yaml')

    # 测试模型结果
    print(metrics.box.map)    # map50-95
    # 0.4295214306631942
    print(metrics.box.map50)  # map50
    # 0.7603770368473041
    print(metrics.box.map75)  # map75
    # .42599055499198585
    print(metrics.box.maps)



import pandas as pd

# with open("aa.csv",encoding="UTF-8") as f:
#     df = pd.read_csv(f, on_bad_lines="skip",sep=";")
#     print(df.head())
#     print(df.info())
#     print(df)

df = pd.read_csv("aa222.csv");
print(f"head: {df.head()}")
print(f"info: {df.info()}")

# 选择两列数据
columns = ['required_experience', 'employment_type']  # 假设你想要处理的列名分别是column1和column2
df[columns[0]] = df[columns[0]].fillna('Experience not available')  # 用'value'替换空值
df[columns[1]] = df[columns[1]].fillna('Employment not available')  # 用'value'替换空值

# 保存结果到新的CSV文件
# df.to_csv("result.csv", index=False)

# 获取所有信息
a = df.iloc()
#打印第一行，title数据的值
print(f"参数为：{a[0].title}")
print(f"参数为：{a}")


# 接下来，我们需要将文本数据转换成特征向量。
# 我们可以使用词袋模型（Bag of Words）或
# TF-IDF（Term Frequency-Inverse Document Frequency）来提取特征。
# 导入CountVectorizer
from sklearn.feature_extraction.text import CountVectorizer

# 实例化CountVectorizer
vectorizer = CountVectorizer()

# 将文本数据转换成特征向量
X = vectorizer.fit_transform(df['required_experience']).values.astype('U'))

# 查看特征向量的形状
X.shape

# 现在，我们可以选择一个机器学习模型来训练，比如逻辑回归模型。
# 导入逻辑回归模型
from sklearn.linear_model import LogisticRegression

# 实例化逻辑回归模型
model = LogisticRegression()

# 拟合模型
model.fit(X, df['title'])

# 最后，我们使用训练好的模型来对新闻进行真假预测。
# 准备测试数据
test_data = ['这是一条真实新闻', '这是一条假新闻']

# 将测试数据转换成特征向量
X_test = vectorizer.transform(test_data)

# 预测新闻的真假
predictions = model.predict(X_test)

# 打印预测结果
for news, pred in zip(test_data, predictions):
    print(f'新闻：{news}，预测结果：{"真实" if pred == 1 else "假新闻"}')