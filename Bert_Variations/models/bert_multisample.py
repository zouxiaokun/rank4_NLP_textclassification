# coding: UTF-8
import torch
import torch.nn as nn
# from pytorch_pretrained_bert import BertModel, BertTokenizer
from pytorch_pretrained_bert import BertModel, BertTokenizer


class Config(object):

    """配置参数"""
    def __init__(self, dataset):
        self.model_name = 'bert-multisample'
        self.train_path = dataset + '/data/cv_1/cv1_train.txt'                                # 训练集
        self.dev_path = dataset + '/data/cv_1/cv1_dev.txt'                                    # 验证集
        self.test_path = dataset + '/data/cv_1/cv_valid.txt'                                  # 测试集
        self.submit_path = dataset + '/data/submit_test_b.txt'
        #self.class_list = [x.strip() for x in open(
        #    dataset + '/data/class.txt').readlines()]                                # 类别名单
        self.save_path = dataset + '/saved_dict/' + self.model_name + '512-1.bin'        # 模型训练结果
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')   # 设备

        self.require_improvement = 100000                                 # 若超过1000batch效果还没提升，则提前结束训练
        self.num_classes = 14                         # 类别数
        self.num_epochs = 2                                            # epoch数
        self.batch_size = 8                                           # mini-batch大小
        self.pad_size = 512                                              # 每句话处理成的长度(短填长切)
        self.learning_rate = 2e-5                                       # 学习率
        self.bert_path = './bert-small/'
        self.tokenizer = BertTokenizer.from_pretrained(self.bert_path)
        print(self.tokenizer,self.bert_path)
        self.hidden_size = 512


class Model(nn.Module):

    def __init__(self, config):
        super(Model, self).__init__()
        self.bert = BertModel.from_pretrained(config.bert_path)
        for param in self.bert.parameters():
            param.requires_grad = True
        self.fc = nn.Linear(config.hidden_size, config.num_classes)
        self.dropouts = nn.ModuleList([nn.Dropout(0.5) for _ in range(5)])


    def forward(self, x):
        context = x[0]  # 输入的句子
        mask = x[2]  # 对padding部分进行mask，和句子一个size，padding部分用0表示，如：[1, 1, 1, 1, 0, 0]
        _, pooled = self.bert(context, attention_mask=mask, output_all_encoded_layers=False)
        for i, dropout in enumerate(self.dropouts):
            if i==0:
                h = self.fc(dropout(pooled))
            else:
                h += self.fc(dropout(pooled))
        out = h/len(self.dropouts)
        return out
