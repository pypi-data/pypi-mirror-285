#===================开始=======================
# # 导入Pandas库
import pandas as pd
# 读取数据集
data = pd.read_csv('111.csv')
# 导入CountVectorizer
from sklearn.feature_extraction.text import CountVectorizer
# 实例化CountVectorizer
vectorizer = CountVectorizer()
# 将文本数据转换成特征向量
X = vectorizer.fit_transform(data['description'].values.astype('U'))
# # 导入逻辑回归模型
from sklearn.linear_model import LogisticRegression
# # 实例化逻辑回归模型 设置最大迭代次数为1000
model = LogisticRegression(max_iter=1000)
# 拟合模型
model.fit(X, data['fraudulent'])

# 将要预测的csv文件内数据读出
ngData = pd.read_csv('r.csv')
# 将列转换为数组
inputs = ngData['description'].to_numpy()
# 将数据转换成特征向量
X_test = vectorizer.transform(inputs)
# 预测新闻的真假
predictions = model.predict(X_test)
# 注明列名，添加新列
ngData['f1'] = predictions
# 把数据写入数据集，index=False表示不加索引
ngData.to_csv('results-fit.csv', index=False)
#===================结束=======================


# 读取训练数据
# import pandas as pd
# with open('aa.csv',encoding='utf-8', errors='ignore') as f:
# 	df = pd.read_csv(f, on_bad_lines="skip", engine='python')
#
# print(df.head())



# import pp as pd
# # 假设 r.csv 是待预测的职位描述，不含标签
# df = pd.read_csv('bb.csv')
# # 检查数据
# # print(df_test.head())
# # df_test.insert(df_test.shape[1], 'd', 0) # 添加一列d, 默认值为0
# inputs = df.iloc[:, [1, 3]]  # 取所有行,第0 2列的数据
# print(inputs)



# import pandas as pd
# # 读取Excel文件，默认读取第一个工作表
# df = pd.read_excel('qqqqq.xlsx')
# # # 读取指定工作表
# # df = pd.read_excel('fake_job_postings(1).csv', sheet_name='fake_job_postings')
# # # 读取多个工作表，返回一个字典，键为工作表名，值为DataFrame
# # dfs = pd.read_excel('fake_job_postings(1).csv', sheet_name=None)
# # 查看数据
# print(df)
# a = df.iloc()
# print(f"参数为：{a[0].title}")
# print(f"参数为：{a}")


# r = range(1, 10, 1)
# print(f" {r} ")
# for i in r:
#     print(f" i {i} ", end="\t")
#     print("凤姐一共买了 %.2f 元的裤子" % i)


# # 选择两列数据
# columns = ['required_experience', 'employment_type']  # 假设你想要处理的列名分别是column1和column2
# df[columns[0]] = df[columns[0]].fillna('Experience not available')  # 用'value'替换空值
# df[columns[1]] = df[columns[1]].fillna('Employment not available')  # 用'value'替换空值
#
# # 保存结果到新的CSV文件
# df.to_csv("result.csv", index=False)


# # # 准备测试数据
# test_data = ['THE COMPANY: ESRI 鈥?Environmental Systems Research InstituteOur passion for improving quality of life through geography is at the heart of everything we do.聽 Esri鈥檚 geographic information system (GIS) technology inspires and enables governments, universities and businesses worldwide to save money, lives and our environment through a deeper understanding of the changing world around them.Carefully managed growth and zero debt give Esri stability that is uncommon in todays volatile business world.聽 Privately held, we offer exceptional benefits, competitive salaries, 401(k) and profit-sharing programs, opportunities for personal and professional growth, and much more.THE OPPORTUNITY: Account ExecutiveAs a member of the Sales Division, you will work collaboratively with an account team in order to sell and promote adoption of Esri鈥檚 ArcGIS platform within an organization. As part of an account team, you will be responsible for facilitating the development and execution of a set of strategies for a defined portfolio of accounts. When executing these strategies you will utilize your experience in enterprise sales to help customers leverage geospatial information and technology to achieve their business goals.聽Specifically鈥rospect and develop opportunities to partner with key stakeholders to envision, develop, and implement a location strategy for their organizationClearly articulate the strength and value proposition of the ArcGIS platformDevelop and maintain a healthy pipeline of opportunities for business growthDemonstrate a thoughtful understanding of insightful industry knowledge and how GIS applies to initiatives, trends, and triggersUnderstand the key business drivers within an organization and identify key business stakeholdersUnderstand your customers鈥?budgeting and acquisition processesSuccessfully execute the account management process including account prioritization, account resourcing, and account planningSuccessfully execute the sales process for all opportunitiesLeverage and lead an account team consisting of sales and other cross-divisional resources to define and execute an account strategyEffectively utilize and leverage the CRM to manage opportunities and drive the buying processPursue professional and personal development to ensure competitive knowledge of the real estate industryLeverage social media to successfully prospect and build a professional networkParticipate in trade shows, workshops, and seminars (as required)Support visual story telling through effective whiteboard sessionsBe resourceful and takes initiative to resolve issues',
#              'QualificationsKnowledge, Skills &amp; Abilities:聽A high school diploma or GED is required. Must have a valid driver鈥檚 license. Ability to read, write, and communicate effectively in English.聽聽Good math skills.聽Four years of experience as an I&amp;C Technician and/or Electrician in a power plant environment, preferably with a strong electrical background, up to and including, voltages to 15 KV to provide the following:Demonstrated knowledge of electrical equipment, electronics, schematics, basics of chemistry and physics and controls and instrumentation.Demonstrated knowledge of safe work practices associated with a power plant environment.Demonstrated ability to calibrate I&amp;C systems and equipment, including analytic equipment.Demonstrated ability to configure and operate various test instruments and equipment, as necessary, to troubleshoot and repair plant equipment including, but not limited to, distributed control systems, programmable logic controllers, motor control centers, transformers, generators, and continuous emissions monitor (CEM) systems.Demonstrated ability to work with others in a team environment.聽',
#              'Organised - Focused - Vibrant - Awesome!Do you have a passion for customer service? Slick typing skills? Maybe Account Management? ...And think administration is cooler than a polar bear on a jetski? Then we need to hear you!聽We are the Cloud Video Production Service and opperating on a glodal level. Yeah, it is pretty cool. Serious about聽delivering a world class product and excellent customer service.Our rapidly expanding business is looking for a talented Project Manager to manage the successful delivery of video projects, manage client communications and drive the production process. Work with some of the coolest brands on the planet and learn from a global team that are representing NZ is a huge way!We are entering the next growth stage of our business and growing quickly internationally. 聽Therefore, the position is bursting with opportunity for the right person entering the business at the right time.聽90 Seconds, the worlds Cloud Video Production Service -聽http://90#URL_fbe6559afac620a3cd2c22281f7b8d0eef56a73e3d9a311e2f1ca13d081dd630#90 Seconds is the worlds Cloud Video Production Service enabling brands and agencies to get high quality online video content shot and produced anywhere in the world. Fast, affordable, and all managed seamlessly in the cloud from purchase to publish.聽90 Seconds removes the hassle, cost, risk and speed issues of working with regular video production companies by managing every aspect of video projects in a beautiful online experience. 聽With a growing network of over 2,000 rated video professionals in over 50 countries and dedicated production success teams in 5 countries guaranteeing video project success 100%. It is as easy as commissioning a quick google adwords campaign.90 Seconds has produced almost 4,000 videos in over 30 Countries for over 500 Global brands including some of the worlds largest including Paypal, Loreal, Sony and Barclays and has offices in Auckland, London, Sydney, Tokyo &amp; Singapore.Our Auckland',
#              'ADMINISTRATIVE &amp; OFFICE ASSISTANTJOB DESCRIPTIONAn exciting growth opportunity for an assistant, who will assist in the daily operations (customer service, office assistant, administrative tasks).QUALIFICATIONSMust have experience in fast pace and dynamic office environments.Extremely detailed oriented, Highly organized and Results oriented.Excellent communication skills/telephone etiquette.Ability to multi-task, prioritize and work on a very dynamic and changing environment.Excellent communication skills, written and oral.Attitude to Solve problems, work INDEPENDENTLY and minimum supervision.'
#              ]
# print(test_data)
# # 将测试数据转换成特征向量
# X_test = vectorizer.transform(test_data)
# # 预测新闻的真假
# predictions = model.predict(X_test)
# print(X_test)
# print(predictions)
# # 打印预测结果
# for news, pred in zip(test_data, predictions):
#     print(f'新闻：{pred}  ，预测结果：{"假新闻" if pred == 1 else "真新闻"} 新闻内容：{news}')
