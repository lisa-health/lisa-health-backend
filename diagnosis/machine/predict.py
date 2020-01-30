import pandas as pd
import jieba
from keras.models import load_model
from os.path import dirname, abspath
from gensim.models import Word2Vec


# 给出至少两个症状,输出10个最有可能出现的病.
# 按照概率从大到小排序
class Predictor:
    def __init__(self):
        abs_path = dirname(abspath(__file__))
        self.train_df = pd.read_csv(abs_path + '/data/data_result.csv')
        self.label_df = pd.read_csv(abs_path + '/data/label.csv')['诊断']
        self.train_df.drop(['Unnamed: 0', '诊断'], inplace=True, axis=1)
        self.label_df = pd.get_dummies(self.label_df)
        jieba.load_userdict(abs_path + '/data/symptom_dict.txt')
        self.train_list = []
        with open(abs_path + '/data/symptom_dict.txt', encoding='utf-8') as f:
            for line in f.readlines():
                self.train_list.append(line.strip('\n'))

        # 加载疾病预测模型
        self.model = load_model(abs_path + '/data/train_mae.h5')
        # 加载疾病相关症状模型
        self.relate_model = Word2Vec.load(abs_path + '/data/disease_relate_symptom.model')

    def get_train_dict_and_value_num(self, train):
        value_num = 0
        train_dict = {}
        for value in train:
            if value in self.train_list:
                train_dict[value] = 1
                value_num += 1
        return value_num, train_dict

    def convert_train(self, train_dict):
        train = pd.DataFrame(train_dict, index=[1])
        train = pd.concat([self.train_df, train], axis=0)[1:][:].fillna(0)
        return train

    # 根据输入的symptom字符串，返回可能的疾病和概率
    # 返回结果是一个list，每个元素是{'name':**,'probability':**}
    def predict(self, symptom):
        # 提取结果
        label_df = self.label_df
        # 加载模型
        model = self.model
        # 新数据分词
        train = jieba.cut(str(symptom), cut_all=False)
        # 统计分词结果,记数
        value_num, train_dict = self.get_train_dict_and_value_num(train)
        # 转换新数据
        train = self.convert_train(train_dict)
        # 预测结果统计
        predict_result = model.predict(train.values)[0]
        predict_dict = {key: predict_result[key] for key in range(len(predict_result))}

        # 提取前十概率结果
        # result_dict key为疾病的索引编号，value为概率
        result_dict = dict(sorted(predict_dict.items(), key=lambda x: x[1], reverse=True)[:10])
        train_columns = label_df.columns.values  # 疾病名称list
        # 返回的结果为一个list
        # 每一个元素是一个dict  {'name':**,'probability':**}
        result = [{
            'name': train_columns[key],
            'probability': round(value * 100, 2)
        } for key, value in result_dict.items()]
        result.sort(key=lambda x: x['probability'], reverse=True)
        return result

    # 根据输入的疾病名称，返回和该疾病最相关的几个症状
    # 返回结果是一个list，每个元素是一个tuple   （症状，相关性）
    def relate(self, disease: str):
        try:
            return self.relate_model.wv.most_similar(disease.replace('，', ',').split(','))
        except KeyError as e:
            return []


predictor = Predictor()
symptom = '四肢无力'
try:
    predictor.predict(symptom)
except Exception as e:
    print(e)
# '头痛,四肢无力,血尿,尿痛,大便出血'
