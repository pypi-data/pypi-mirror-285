from dataclasses import dataclass
from src.dao import BaseDao
import nltk
import os
import shutil
from datetime import datetime
from src.dao import SynonymsDao

@dataclass
class Process:
    tvp = 'src/assets/pickle/tfidf_vectorizer.pickle'
    tmp = 'src/assets/pickle/tfidf_matrix.pickle'
    backup_folder = 'src/assets/pickle/old'

    # 备份文件
    def backup_file(self, file_path, timestamp:str = datetime.now().strftime("%Y%m%d_%H%M%S")):
        # 创建备份文件夹（如果不存在）
        if not os.path.exists(self.backup_folder):
            os.makedirs(self.backup_folder)
        if os.path.exists(file_path):
            # 获取文件名和扩展名
            file_name, file_extension = os.path.splitext(os.path.basename(file_path))
            new_file_name = f"{file_name}_{timestamp}{file_extension}"
            destination = os.path.join(self.backup_folder, new_file_name)
            shutil.copy2(file_path, destination)
            print(f"copy {file_path} to {destination}")
        else:
            print(f"error: unknow {file_path}")

    def instDesc2csv(self, output:str = 'src/assets/csv/inst_data.csv'):
        import sqlite3
        import csv
        with BaseDao().connect() as (conn, cur):
            columns = ['id', 'brief', 'description']
            # 执行查询获取所有数据
            cur.execute("SELECT id, name, description FROM inst WHERE exist = 1")
            # 写入CSV文件
            with open(output, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                # 写入表头
                writer.writerow(columns)
                # 写入数据行
                writer.writerows(cur)
    def tdIdfDataInit(self):
        from sklearn.feature_extraction.text import TfidfVectorizer 
        import pickle 
        import pandas as pd

        nltk.download('stopwords')
        nltk.download('punkt')
        
        # 读取CSV数据
        df = pd.read_csv('src/assets/csv/inst_data.csv', delimiter=',')
        # 预处理
        df['combined_text'] = df[['brief','description']].apply(lambda x: self.Preprocessing(' '.join(x)), axis=1)
        # 初始化TF-IDF向量化器以及向量矩阵
        tfidf_vectorizer = TfidfVectorizer()
        tfidf_matrix = tfidf_vectorizer.fit_transform(df['combined_text'])

        # 时间戳
        # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # 备份
        while True:
            response = input("Do you want to create a backup? (yes/no): ").strip().lower()
            if response in ['yes', 'y']:
                self.backup_file(self.tvp)
                self.backup_file(self.tmp)
                break
            elif response in ['no', 'n']:
                break
            else:
                print("Invalid input. Please enter 'yes' or 'no'.")

        # 保存TF-IDF向量化器以及向量矩阵
        with open(self.tvp, 'wb') as vectorizer_file:
            pickle.dump(tfidf_vectorizer, vectorizer_file)

        with open(self.tmp, 'wb') as matrix_file:
            pickle.dump(tfidf_matrix, matrix_file)

    def Preprocessing(self, text):
        """
        文本预处理
        首次运行需下载必要的NLTK资源
        nltk.download('punkt') # 分割词语
        nltk.download('stopwords')
        # wordnet下载时间较长，特别在无代理的情况下，有几十兆，可下载离线版本
        nltk.download('wordnet') # 同义词
        """
        import string
        from nltk.corpus import stopwords, wordnet
        from nltk.tokenize import word_tokenize

        # 去除标点符号
        text = ''.join(ch for ch in text if ch not in string.punctuation)

        # 去除停用词
        ## 加载英文停用词列表
        stop_words = set(stopwords.words('english'))

        ## 对文本进行分词
        words = word_tokenize(text)

        ## 过滤掉停用词,并将内容化为小写
        text = ' '.join([word.lower() for word in words if word.lower() not in stop_words])
        
        # 替换同义词
        ## 对文本进行分词
        words = word_tokenize(text)
        
        ## 创建新字符串存储增加同义词后的文本
        new_text = ''

        for word in words:
            print(word + '----------') # 用于调试
            synonyms = []
            # 自定义同义词
            synonym_ids = SynonymsDao().SelectByString(word)
            for id in synonym_ids:
                synonym = SynonymsDao().SelectById(id)
                if synonym:
                    synonyms.append(synonym)

            # wordnet库同义词
            for syn in wordnet.synsets(word):
                for lm in syn.lemmas():
                    synonyms.append(lm.name())
            if synonyms:
                # print(list(set(synonyms))) # 用于调试
                # print()
                new_text += ' '.join(list(set(synonyms))) + ' '
            else:
                # print(word) # 用于调试
                # print()
                new_text += ''.join(word) + ' '

        return new_text