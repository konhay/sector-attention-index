# Sector Attention Index
## Introduction

This open source project is specifically built for the research proposal: ***Estimating sector attention index with deep learning methods : example of Chinese stock market***, *Jan. 4, 2024, Bing Han*. ([*Download*](https://konhay.github.io/docs/04_Sector_Attention_Index_in_Chinese_stock_market.pdf))

Abstract

For Chinese stock market, we define SAI (Sector Attention Index) to quantify the retail investor attention of a specific sector according to the online post volume of the sector’s most representative stocks. We define an abnormal SAI to distinguish extra attention, and a sentiment SAI for sentiment analysis. The text data of post is taken from the most active online stock forum Eastmoney (aka Guba) in mainland China. We rebuild a new sentiment dictionary and design a deep learning model to classify the sentiment tendency in stock posts. We conduct a series of regression analyses to test the predictive power of the SAIs and their correlation with stock returns and trading amount. 

Key words: Sector Investor Attention, Sentiment Analysis, Alternative Data, Chinese Stock Market, Deep Learning

## guba
This package is built for getting retail investor post data from [*EasyMoney*](https://guba.eastmoney.com/) Stock Forum. It provides text data preprocessing, sentiment marking and other advanced NLP functions.
#### Get Text data

We will develop a web crawler program to collect retail investor posts in Eastmoney’s stock forum and insert them into database. For sector and component information, we also need to execute a separate program (*package sector*) to collect sector list and constituent stock list.

#### Data preprocessing

We need delete posts that do not meet the requirements, including those that are suspected of advertising and those that are too short. We adopt [*Jieba*](https://github.com/fxsjy/jieba) tokenizer for word segmentation. *Jieba* tokenizer is a highly effective Chinese segmentation device that supports multiple segmentation modes. 

In order to adapt to the embedding layer of AI model, We make all sequences equal length by cutting them or adding zeros at the end. We will fix the length of all posts to 40 characters. This step can be achieved through the methods provided by [*Keras*](https://keras.io/), an open-source artificial neural network library written in Python.

#### Available pre-trained resource

Pre-trained models or algorithms publicly disclosed by some AI giants (e.g. Tencent and Baidu) will help us improve the efficiency of NLP tasks for Chinese text. We will choose some of these including kinds of 1) Pre-trained models which can complete typical sentiment analysis tasks such as Sentence-level Sentiment Classification and Aspect-level Sentiment Classification. 2) Embedding corpora for Chinese words and phrases which provide finite-dimensional vector representations, a.k.a. embeddings, for Chinese words. We will introduce these pre-trained models to build our word embedding layer and BiLSTM layer, after finetuning them to suit our stock analysis scenarios. We have tried some of these and gives examples in `nlp_processor.py`, such as [*Tencent AI Lab Embedding Corpora*](https://ai.tencent.com/ailab/nlp/en/embedding.html), [*Baidu Senta*](https://github.com/baidu/Senta), etc. It will provide support for us to finish the classification task for sentiment SAI and to build the *BiLSTM-CNN-Attention* model in the research proposal.

## sector
This package is built to collecting basic information and daily market data for [*RoyalFlush*](https://q.10jqka.com.cn/thshy/) Sectors (bk).

TableName: finance.bk_info

| bk_code | bk_name                             | bk_source  | bk_type  | use_flag | data_date |
| ------- | ----------------------------------- | ---------- | -------- | -------- | --------- |
| 881105  | Coal Mining and Processing          | RoyalFlush | industry | 0        | 20230901  |
| 881107  | Oil and Gas Extraction and Services | RoyalFlush | industry | 0        | 20230901  |
| 881112  | Iron and Steel                      | RoyalFlush | industry | 0        | 20230901  |
| 881114  | New Metal Materials                 | RoyalFlush | industry | 0        | 20230901  |
| 881115  | Electrical Equipment                | RoyalFlush | industry | 0        | 20230901  |
| ...     | ...                                 | ...        | ...      | ...      | ...       |

TableName: finance.bk_daily

| bk_code | trade_date | open    | high    | low     | close   | vol       | amount     |
| ------- | ---------- | ------- | ------- | ------- | ------- | --------- | ---------- |
| 881101  | 20170103   | 3377.61 | 3443.5  | 3375.48 | 3443.5  | 274943000 | 3716640000 |
| 881101  | 20170104   | 3460.55 | 3485.34 | 3450.91 | 3483.28 | 274666000 | 3556330000 |
| 881101  | 20170105   | 3497.98 | 3509.4  | 3485.54 | 3496.86 | 317430000 | 4151030000 |
| 881101  | 20170106   | 3482.32 | 3482.52 | 3425.53 | 3427.62 | 277866000 | 3730740000 |
| 881101  | 20170109   | 3420.59 | 3442.88 | 3410.14 | 3442.88 | 284142000 | 3557920000 |
| ...     | ...        | ...     | ...     | ...     | ...     | ...       | ...        |

