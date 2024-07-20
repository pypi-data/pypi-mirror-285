import os
import pickle
import pandas as pd 
from sklearn.metrics.pairwise import cosine_similarity 

def tfidf(user_input):
    # 获取当前脚本的绝对路径
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # 构建各个文件和文件夹的绝对路径
    tvp = os.path.join(current_dir, '..', 'assets', 'pickle', 'tfidf_vectorizer.pickle')
    tmp = os.path.join(current_dir, '..', 'assets', 'pickle', 'tfidf_matrix.pickle')
    backup_folder = os.path.join(current_dir, '..', 'assets', 'pickle', 'old')
    output_csv = os.path.join(current_dir, '..', 'assets', 'csv', 'inst_data.csv')

    # 读取CSV数据
    df = pd.read_csv(output_csv, delimiter=',')
  
    if os.path.isfile(tvp) and os.path.isfile(tmp):
        # 加载TF-IDF向量化器以及向量矩阵
        with open(tvp, 'rb') as handle:
            tfidf_vectorizer = pickle.load(handle)

        with open(tmp, 'rb') as handle:
            tfidf_matrix = pickle.load(handle)

        # 将用户输入转换为TF-IDF向量
        user_tfidf = tfidf_vectorizer.transform([user_input])

        # 计算用户输入与所有软件包指令的相似度
        cosine_similarities = cosine_similarity(user_tfidf, tfidf_matrix).flatten()
        indices = cosine_similarities.argsort()[::-1]  # [::-1]反转数组使索引按降序排列

        # 获取相关度排序列表
        similar = df.loc[indices, f'id'].tolist()
        scores = cosine_similarities[indices].tolist()

        return similar, scores


def search(user_input):
    from ..dao import InstDao
    from ..dao.entity import Inst

    similar, scores = tfidf(user_input)
    res = InstDao().SelectBriefInfoByIds(similar)
    # 创建一个字典，键为id，值为顺序的大小
    order_dict = {value: index for index, value in enumerate(similar)}
    # 使用 sorted 函数以顺序大小进行排序
    sort = sorted(res, key=lambda x: order_dict[x[0]])
    res = [(*i[0], i[1]) for i in list(zip(sort, scores))]
    return res