#coding:utf-8
from aip import AipNlp
from gensim.models import KeyedVectors
import matplotlib
matplotlib.use('TkAgg')
import numpy as np
import jieba.posseg as pseg
import paddlehub as hub
import pandas as pd
import jieba


#
# Tencent AI Lab Embedding Corpora for Chinese and English Words and Phrases
#
def test_embedding():
    filename = "database/east_guba_cmt.csv"
    data = pd.read_csv(filename, names=["code","dtime","title","author"], header=0)
    data = data[data["code"]=="zssh000001"]
    data = data.reset_index(drop=True)
    bk = pd.read_csv("database/bk_info.txt", sep='\t', header=None)
    bk.columns = ['bk_code','bk_name']
    x = []
    for i in bk.bk_name:
        lcut = pseg.lcut(i)
        words_nv = [x for (x,y) in lcut if y in ['n','v']]
        x.append(words_nv)
    bk['seg'] = x

    model = KeyedVectors.load('C:/Users/Administrator/Downloads/tencent-ailab-embedding-zh-d100-v0.2.0-s/tencent-ailab-embedding-zh-d100-v0.2.0-s/Tencent_AILab_ChineseEmbedding.bin')
    x = []
    for i in data.title:
        lcut = pseg.lcut(i)
        try:
            smean = np.mean([model.similarity(x, '钢铁') for (x, y) in lcut if y in ['n']])
            x.append((round(smean,3), i))
        except Exception as e:
            print(e)
            continue
    df = pd.DataFrame(x, columns=['similarity','title'])
    df.sort_values('similarity', inplace=True, ascending=False)
    df.dropna(inplace=True)
    df.to_csv('words_n.txt', sep='\t', header=True, index=False)


#
# Senta-BiLSTM by Baidu Papaddlehub
#
def test_senta():
    # Load Data
    filename = "database/east_guba_cmt.csv"
    data = pd.read_csv(filename, names=["code","dtime","title","author"], header=0)
    data = data[data["code"]=="600999"]
    data = data.reset_index(drop=True)
    data.dropna(inplace=True)# necessarily

    # Load Senta-BiLSTM module
    senta = hub.Module(name="senta_bilstm")
    test_text = list(data.title)
    input_dict = {"text": test_text}
    results = senta.sentiment_classify(data=input_dict)

    # [..., {'text': '牛市来了，他来了！证券为先，南京证券绝对龙头！每次证券启动，不到三五倍不算完。',
    #  'sentiment_label': 1,
    #  'sentiment_key': 'positive',
    #  'positive_probs': 0.8575,
    #  'negative_probs': 0.1425}, ...]

    df = pd.DataFrame(results)
    df = df[['sentiment_label', 'sentiment_key', 'positive_probs', 'negative_probs','text']]

    return df


#
# Baidu AipNlp
#
def get_sentiment(text):
    """
    利用百度nlp应用,进行文本情绪分析
    text: Chinese text string
    reference: https://github.com/Baidu-AIP
    """
    try:
        client = init_aip_client()
        items = client.sentimentClassify(text)['items'][0] #dict
        positive_prob = items['positive_prob']
        confidence = items['confidence']
        negative_prob = items['negative_prob']
        sentiment = items['sentiment'] #0表示消极，1表示中性，2表示积极
        output = '{}\t{}\t{}\n'.format(positive_prob, confidence, sentiment)
        # f = codecs.open('sentiment.txt', 'a+', 'utf-8')
        # f.write(output)
        # f.close()
        print(output)
        return output
    except Exception as e:
        print(e)


def init_aip_client():
    """
    初始化百度nlp应用
    reference: https://console.bce.baidu.com/
    """
    APP_ID = '***'
    API_KEY = '***'
    SECRET_KEY = '***'
    client = AipNlp(APP_ID, API_KEY, SECRET_KEY)
    return client


#
# Jieba Tokenizer
#
def get_segment_list(comment_list):
    """
    结巴分词
    comment_list: List[str], get_page_comment() or get_batch_comment(()
    """
    segment_list = []
    for comment in comment_list:
        # ss = SnowNLP(comment[1])
        # print(round(ss.sentiments,3), comment[1])
        segments = jieba.cut(comment[1], cut_all=False)
        segments = remove_stopwords(segments)
        print(" ".join(segments))
        segment_list.append(segments)
    return segment_list


#
# Common Methods
#
def remove_stopwords(segments):
    """
    过滤停止词
    segments: 剔除停止词前的结巴分词
    segments_nstop: 剔除停止词后的结巴分词
    """
    stopwords = list([line.strip() for line in open('stopwords.txt')])
    stopwords.append("XXX")
    stopwords.append("YYY")
    segments_nstop = []
    for segment in segments:
        if segment[0] not in stopwords:
            segments_nstop.append(segment)
    return segments_nstop


def label_comment(comment_list):
    """
    给评论内容打标签,即看多还是看空
    comment_list: List[str], get_page_comment() or get_batch_comment(()
    txt: words_bearish and words_bullish needs to be constantly expanded
    """
    put_words = list([line.strip() for line in open('words_bearish.txt', encoding='UTF-8')])
    call_words = list([line.strip() for line in open('words_bullish.txt', encoding='UTF-8')])
    put_label = False
    call_label = False
    i = 1
    for comment in comment_list:
        print('正在处理第{}条,还剩{}条'.format(i, len(comment_list)-i))
        i = i+1
        for word in put_words:
            if word in comment[1] :
                put_label = True
                break
        for word in call_words:
            if word in comment[1] :
                call_label = True
                break
        if put_label and not call_label:
            comment.append('put')
        elif not put_label and call_label:
            comment.append('call')
        else :
            comment.append('unknown')
    return comment_list


def load_content(startdate:str):
    data = pd.DataFrame(pd.read_excel('eastmoney.xlsx', sheet_name=0))
    data.columns = ['Dates', 'viewpoints']  # 重设表头
    data = data.sort_values(by=['Dates'])  # 按日期排列
    vdata = data[data.Dates >= startdate]  # 提取对应日期的数据
    newvdata = vdata.groupby('Dates').agg(lambda x: list(x))  # 按日期分组，把同一天的评论并到一起
    return newvdata