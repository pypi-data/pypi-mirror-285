import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score,f1_score


train=pd.read_csv("fake_job_postings_train.csv")

train.head()
train.info()
train.describe()


#train['location'] = train['location'].replace('GB, LND, ', '')
#train.where(~train['location'].isna() ).replace('', '22', )
bin_features = ['telecommuting', 'has_company_logo', 'has_questions']

cat_features = ['department', 'employment_type', 'required_experience',
                'required_education', 'industry', 'function']

text_features = ['title', 'company_profile', 'description', 'requirements', 'benefits']

complex_features = ['location', 'salary_range']


train['location'].fillna(',,,', inplace=True)
train['employment_type'].fillna('Employment_not_available', inplace=True)
train['required_experience'].fillna('Employment_not_available', inplace=True)
train['required_education'].fillna('unknown', inplace=True)
train['location'].fillna(',,,', inplace=True)
train['salary_range'].fillna('0-0',inplace=True)
train['department'].fillna('unknown',inplace=True)
train['industry'].fillna('unknown',inplace=True)
train['function'].fillna('unknown',inplace=True)
for i in text_features:
    train[i].fillna('',inplace=True)


new = pd.concat([train[bin_features],train['fraudulent']],axis=1)
plt.figure(figsize=(10,10))
sns.heatmap(new.corr(),annot=True)
plt.savefig('corr.jpg')
plt.show()

train['required_education'].value_counts()
for i in cat_features:
    print(i,len(train[i].unique()))

plt.figure(figsize=(10, 6))
sns.countplot(x='employment_type', hue='fraudulent', data=train)
plt.xlabel('employment_type')
plt.ylabel('fraudulent')
plt.legend(title='Label')
plt.savefig('plt_demo.jpg')
plt.show()

#特殊处理
train['requirements_count_of_words'] = train['requirements'].astype(str).str.split(' ').apply(len)
train['company_profile_count_of_words'] = train['company_profile'].astype(str).str.split(' ').apply(len)



min_max_salary_list = [i.split('-') for i in train['salary_range'].values]
for i in min_max_salary_list:
    try:
        i[0] = int(i[0])
        i[1] = int(i[1])
    except:
        i[0] = 0
        i[1] = 0


df_min_max_salary_list = pd.DataFrame(min_max_salary_list,columns=['min_salary','max_salary']).astype(int)

train = pd.concat([train,df_min_max_salary_list],axis=1)
t,t1 = train_test_split(train,test_size=0.2,shuffle=True)


import lightgbm as lgb
lgb_model = lgb.LGBMClassifier(objective='binary', metric='binary_logloss')

train,test = train_test_split(train,test_size=0.2,shuffle=True)
train = train.drop('job_id',axis=1)
train_x =  train.drop('fraudulent',axis=1)
train_y = train['fraudulent']

test_x =  test.drop('fraudulent',axis=1)
test_y = test['fraudulent']

num_transformer = Pipeline(steps=[('scaler', StandardScaler())])
cat_transformer = Pipeline(steps=[('onehot', OneHotEncoder(handle_unknown='ignore'))])
text_transformer = Pipeline(steps=[('tfidf', TfidfVectorizer(ngram_range=(1, 2)))])
num_features = ['requirements_count_of_words','company_profile_count_of_words']
preprocessor = ColumnTransformer(
    transformers=[
        ('num', num_transformer, num_features),
        ('cat', cat_transformer, cat_features),
        *[(feature_name, text_transformer, feature_name)
          for feature_name in text_features]
    ]
)

log_reg_pipe = Pipeline(steps=[('preprocessor', preprocessor),
                               ('classifier', lgb_model)])
model=log_reg_pipe.fit(train_x,train_y)


import joblib
joblib.dump(model, 'model.pkl')  # 保存模型到文件'model.pkl'

# 加载模型
loaded_model = joblib.load('model.pkl')
result = loaded_model.predict(test_x)
#result_pre = loaded_model.predict_proba(test)
accuracy = accuracy_score(test_y,result)
f1 = f1_score(test_y,result )
print("Accuracy:", accuracy)
print("f1:", f1)

###save_result
pre_df = pd.DataFrame(result, columns=['pre'])

r = pd.concat([test['job_id'], pre_df], axis=1)
r.to_csv('r.csv', index=False)




