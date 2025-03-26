# -*- coding: utf-8 -*-
"""NLP_HW3_NCCU_110306085

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1KsdjWYPBLHBL3MF5-FxtNwpMkPY6MsaG
"""

!pip install datasets==2.21.0
!pip install torchmetrics

import transformers as T
from datasets import load_dataset
import torch
from torch.utils.data import Dataset, DataLoader
from torch.optim import AdamW
from tqdm import tqdm
from torchmetrics import SpearmanCorrCoef, Accuracy, F1Score
device = "cuda:3" if torch.cuda.is_available() else "cpu"

# 有些中文的標點符號在tokenizer編碼以後會變成[UNK]，所以將其換成英文標點
token_replacement = [
    ["：" , ":"],
    ["，" , ","],
    ["“" , "\""],
    ["”" , "\""],
    ["？" , "?"],
    ["……" , "..."],
    ["！" , "!"]
]

tokenizer = T.BertTokenizer.from_pretrained("google-bert/bert-base-uncased", cache_dir="./cache/")

class SemevalDataset(Dataset):
    def __init__(self, split="train") -> None:
        super().__init__()
        assert split in ["train", "validation", "test"] # chatGPT: 加入 "test" 作為有效選項
        self.data = load_dataset(
            "sem_eval_2014_task_1", split=split, cache_dir="./cache/"
        ).to_list()

    def __getitem__(self, index):
        d = self.data[index]
        # 把中文標點替換掉
        for k in ["premise", "hypothesis"]:
            for tok in token_replacement:
                d[k] = d[k].replace(tok[0], tok[1])
        return d

    def __len__(self):
        return len(self.data)

data_sample = SemevalDataset(split="train").data[:3]
print(f"Dataset example: \n{data_sample[0]} \n{data_sample[1]} \n{data_sample[2]}")

# Define the hyperparameters
lr = 3e-5
epochs = 10
train_batch_size = 8
validation_batch_size = 8

# TODO1: Create batched data for DataLoader
# `collate_fn` is a function that defines how the data batch should be packed.
# This function will be called in the DataLoader to pack the data batch.

def collate_fn(batch):
    # TODO1-1: Implement the collate_fn function
    # Write your code here
    # The input parameter is a data batch (tuple), and this function packs it into tensors.
    # Use tokenizer to pack tokenize and pack the data and its corresponding labels.
    # Return the data batch and labels for each sub-task.

    # ChatGPT
    # 獲取文本數據和標籤
    texts = [item["premise"] + " " + item["hypothesis"] for item in batch]
    labels1 = torch.tensor([item["relatedness_score"] for item in batch])
    labels2 = torch.tensor([item["entailment_judgment"] for item in batch])

    # 使用 tokenizer 將文本數據轉換為模型輸入格式
    encoding = tokenizer(
        texts,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=512
    )

    return {
        "input_text": encoding,  # 將輸入文本編碼為 input_text
        "labels1": labels1,
        "labels2": labels2
    }

# TODO1-2: Define your DataLoader
dl_train = DataLoader(
    dataset=SemevalDataset(split="train"),
    batch_size=train_batch_size,
    shuffle=True,
    collate_fn=collate_fn
)# Write your code here

dl_validation = DataLoader(
    dataset=SemevalDataset(split="validation"),
    batch_size=validation_batch_size,
    shuffle=False,
    collate_fn=collate_fn
)# Write your code here

# testing data
dl_test = DataLoader(
    dataset=SemevalDataset(split="test"),
    batch_size=8,
    shuffle=False,
    collate_fn=collate_fn
)

print(next(iter(dl_train)))

# TODO2: Construct your model
class MultiLabelModel(torch.nn.Module):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Write your code here
        # Define what modules you will use in the model

        self.bert = T.BertModel.from_pretrained("google-bert/bert-base-uncased", cache_dir="./cache/")

        # dropout
        # self.dropout = torch.nn.Dropout(p=0.1)

        # regression (relatedness_score)
        self.linear1 = torch.nn.Linear(self.bert.config.hidden_size, 1)

        # classfication (entailment_judgement)
        self.linear2 = torch.nn.Linear(self.bert.config.hidden_size, 3)

    def forward(self, **kwargs):
        # Write your code here
        # Forward pass

        # ChatGPT
        # 從 kwargs 中提取所需的參數
        input_ids = kwargs.get("input_ids")
        attention_mask = kwargs.get("attention_mask")
        token_type_ids = kwargs.get("token_type_ids")

        # 使用 BERT 處理輸入
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask, token_type_ids=token_type_ids)

        # 取出 [CLS] 標記的輸出向量
        cls_output = outputs.last_hidden_state[:, 0, :]

        # 使用 Dropout 層
        # cls_output = self.dropout(cls_output)

        # 對應的兩個任務的輸出
        relatedness_score = self.linear1(cls_output).squeeze(-1)  # 回歸任務
        entailment_judgement = self.linear2(cls_output)  # 分類任務

        return relatedness_score, entailment_judgement

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
print(device)

model = MultiLabelModel().to(device)

# TODO3: Define your optimizer and loss function

# TODO3-1: Define your Optimizer
optimizer = torch.optim.AdamW(model.parameters(), lr=lr) # Write your code here

# TODO3-2: Define your loss functions (you should have two)
# Write your code here
regression_loss_fn = torch.nn.MSELoss()
classification_loss_fn = torch.nn.CrossEntropyLoss()

# scoring functions
spc = SpearmanCorrCoef().to(device)
acc = Accuracy(task="multiclass", num_classes=3).to(device)
f1 = F1Score(task="multiclass", num_classes=3, average='macro').to(device)

import os

# chatGPT:檢查並創建目錄
os.makedirs("./saved_models", exist_ok=True)

for ep in range(epochs):
    pbar = tqdm(dl_train)
    pbar.set_description(f"Training epoch [{ep+1}/{epochs}]")
    model.train()
    # TODO4: Write the training loop
    # Write your code here
    # train your model
    # clear gradient
    # forward pass
    # compute loss
    # back-propagation
    # model optimization

    # chatGPT
    for batch in pbar:
        optimizer.zero_grad()  # 清除梯度

        # 提取批次數據
        input_text = {k: v.to(device) for k, v in batch['input_text'].items()}
        labels1 = batch['labels1'].to(device)
        labels2 = batch['labels2'].to(device)

        # 前向傳播
        relatedness_score, entailment_judgement = model(**input_text)

        # 計算損失（將兩個損失相加）
        loss1 = regression_loss_fn(relatedness_score, labels1)  # 對應 relatedness_score 的損失
        loss2 = classification_loss_fn(entailment_judgement, labels2)  # 對應 entailment_judgement 的損失
        loss = loss1 + loss2

        # 反向傳播和優化
        loss.backward()
        optimizer.step()

        # 更新進度條描述
        pbar.set_postfix({"loss": loss.item()})

    pbar = tqdm(dl_validation)
    pbar.set_description(f"Validation epoch [{ep+1}/{epochs}]")
    model.eval()
    # TODO5: Write the evaluation loop
    # Write your code here
    # Evaluate your model
    # Output all the evaluation scores (SpearmanCorrCoef, Accuracy, F1Score)

    # chatGPT
    for batch in pbar:
      input_text = {k: v.to(device) for k, v in batch['input_text'].items()}
      labels1 = batch['labels1'].to(device)
      labels2 = batch['labels2'].to(device)

      with torch.no_grad():
          relatedness_score, entailment_judgement = model(**input_text)

      # 計算分數
      spc.update(relatedness_score, labels1)
      acc.update(entailment_judgement, labels2)
      f1.update(entailment_judgement, labels2)

    # 最後計算並輸出評分結果
    spearman_score = spc.compute()
    accuracy_score = acc.compute()
    f1_score = f1.compute()
    print(f"Spearman Correlation: {spearman_score:.4f}, Accuracy: {accuracy_score:.4f}, F1 Score: {f1_score:.4f}")

    # 清除評分器的狀態，為下一個 epoch 做準備
    spc.reset()
    acc.reset()
    f1.reset()

    torch.save(model, f'./saved_models/ep{ep}.ckpt')

"""For test set predictions, you can write perform evaluation simlar to #TODO5."""

import matplotlib.pyplot as plt
import seaborn as sns

spearman_scores = []
accuracy_scores = []
f1_scores = []

# 評估testing data的表現
pbar = tqdm(dl_test)
pbar.set_description("Evaluating on test set")
model.eval()

for batch in pbar:
    input_text = {k: v.to(device) for k, v in batch['input_text'].items()}
    labels1 = batch['labels1'].to(device)
    labels2 = batch['labels2'].to(device)

    with torch.no_grad():
        relatedness_score, entailment_judgement = model(**input_text)

    spc.update(relatedness_score, labels1)
    acc.update(entailment_judgement, labels2)
    f1.update(entailment_judgement, labels2)

    # chatGPT: 記錄每個 batch 的分數
    spearman_scores.append(spc.compute().item())
    accuracy_scores.append(acc.compute().item())
    f1_scores.append(f1.compute().item())

spearman_score = spc.compute()
accuracy_score = acc.compute()
f1_score = f1.compute()
print(f"Test Set - Spearman Correlation: {spearman_score:.4f}, Accuracy: {accuracy_score:.4f}, F1 Score: {f1_score:.4f}")

# chatGPT: 畫出Spearman Correlation, Accuracy, F1 Score
plt.figure(figsize=(12, 6))
sns.set_style("whitegrid")

# Spearman Correlation
plt.subplot(1, 3, 1)
plt.plot(spearman_scores, label='Spearman Correlation', color='blue')
plt.xlabel('Batch')
plt.ylabel('Score')
plt.title('Spearman Correlation per Batch')
plt.ylim(0.5, 1)
plt.legend()

# Accuracy
plt.subplot(1, 3, 2)
plt.plot(accuracy_scores, label='Accuracy', color='green')
plt.xlabel('Batch')
plt.ylabel('Score')
plt.title('Accuracy per Batch')
plt.ylim(0.5, 1)
plt.legend()

# F1 Score
plt.subplot(1, 3, 3)
plt.plot(f1_scores, label='F1 Score', color='red')
plt.xlabel('Batch')
plt.ylabel('Score')
plt.title('F1 Score per Batch')
plt.ylim(0.5, 1)
plt.legend()

plt.tight_layout()
plt.show()

spc.reset()
acc.reset()
f1.reset()

"""## Multi-Output v.s. Separate Models

### regression model
"""

class RegressionModel(torch.nn.Module):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bert = T.BertModel.from_pretrained("google-bert/bert-base-uncased", cache_dir="./cache/")
        self.linear1 = torch.nn.Linear(self.bert.config.hidden_size, 1)  # Regression task

    def forward(self, **kwargs):
        input_ids = kwargs.get("input_ids")
        attention_mask = kwargs.get("attention_mask")
        token_type_ids = kwargs.get("token_type_ids")

        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask, token_type_ids=token_type_ids)
        cls_output = outputs.last_hidden_state[:, 0, :]  # CLS token hidden state for regression

        relatedness_score = self.linear1(cls_output).squeeze(-1)  # Output relatedness score

        return relatedness_score

regression_model = RegressionModel().to(device)

# regression: optimizer and loss function
regression_optimizer = torch.optim.AdamW(regression_model.parameters(), lr=lr)
regression_loss_fn = torch.nn.MSELoss()

regression_spc = SpearmanCorrCoef().to(device)

for ep in range(epochs):
    pbar = tqdm(dl_train)
    pbar.set_description(f"Training epoch [{ep+1}/{epochs}]")
    regression_model.train()

    for batch in pbar:
        regression_optimizer.zero_grad()

        input_text = {k: v.to(device) for k, v in batch['input_text'].items()}
        labels1 = batch['labels1'].to(device)

        relatedness_score = regression_model(**input_text)

        loss1 = regression_loss_fn(relatedness_score, labels1)

        loss1.backward()
        regression_optimizer.step()

        pbar.set_postfix({"loss": loss1.item()})

    pbar = tqdm(dl_validation)
    pbar.set_description(f"Validation epoch [{ep+1}/{epochs}]")
    regression_model.eval()

    for batch in pbar:
      input_text = {k: v.to(device) for k, v in batch['input_text'].items()}
      labels1 = batch['labels1'].to(device)

      with torch.no_grad():
          relatedness_score = regression_model(**input_text)

      regression_spc.update(relatedness_score, labels1)

    regression_spearman_score = regression_spc.compute()
    print(f"Spearman Correlation: {regression_spearman_score:.4f}")

    regression_spc.reset()

    # torch.save(model, f'./saved_models/ep{ep}.ckpt')

regression_spearman_scores = []

# 評估testing data的表現
pbar = tqdm(dl_test)
pbar.set_description("Evaluating on test set")
regression_model.eval()

for batch in pbar:
    input_text = {k: v.to(device) for k, v in batch['input_text'].items()}
    labels1 = batch['labels1'].to(device)

    with torch.no_grad():
        relatedness_score = regression_model(**input_text)

    regression_spc.update(relatedness_score, labels1)

    regression_spearman_scores.append(regression_spc.compute().item())

regression_spearman_score = regression_spc.compute()
print(f"Test Set - Spearman Correlation: {regression_spearman_score:.4f}")

"""### classification model"""

class ClassificationModel(torch.nn.Module):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bert = T.BertModel.from_pretrained("google-bert/bert-base-uncased", cache_dir="./cache/")
        self.linear2 = torch.nn.Linear(self.bert.config.hidden_size, 3)  # 3 classes for classification

    def forward(self, **kwargs):
        input_ids = kwargs.get("input_ids")
        attention_mask = kwargs.get("attention_mask")
        token_type_ids = kwargs.get("token_type_ids")

        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask, token_type_ids=token_type_ids)
        cls_output = outputs.last_hidden_state[:, 0, :]  # CLS token hidden state for classification

        entailment_judgement = self.linear2(cls_output)  # Output classification logits

        return entailment_judgement

classification_model = ClassificationModel().to(device)

# classification: optimizer and loss function
classification_optimizer = torch.optim.AdamW(classification_model.parameters(), lr=lr) # Write your code here
classification_loss_fn = torch.nn.CrossEntropyLoss()

acc = Accuracy(task="multiclass", num_classes=3).to(device)
f1 = F1Score(task="multiclass", num_classes=3, average='macro').to(device)

for ep in range(epochs):
    pbar = tqdm(dl_train)
    pbar.set_description(f"Training epoch [{ep+1}/{epochs}]")
    classification_model.train()

    for batch in pbar:
        classification_optimizer.zero_grad()

        input_text = {k: v.to(device) for k, v in batch['input_text'].items()}
        labels2 = batch['labels2'].to(device)

        entailment_judgement = classification_model(**input_text)

        loss2 = classification_loss_fn(entailment_judgement, labels2)

        loss2.backward()
        classification_optimizer.step()

        pbar.set_postfix({"loss": loss2.item()})

    pbar = tqdm(dl_validation)
    pbar.set_description(f"Validation epoch [{ep+1}/{epochs}]")
    classification_model.eval()

    for batch in pbar:
      input_text = {k: v.to(device) for k, v in batch['input_text'].items()}
      labels2 = batch['labels2'].to(device)

      with torch.no_grad():
          entailment_judgement = classification_model(**input_text)

      acc.update(entailment_judgement, labels2)
      f1.update(entailment_judgement, labels2)

    classification_accuracy_score = acc.compute()
    classification_f1_score = f1.compute()
    print(f"Accuracy: {classification_accuracy_score:.4f}, F1 Score: {classification_f1_score:.4f}")

    acc.reset()
    f1.reset()

    # torch.save(model, f'./saved_models/ep{ep}.ckpt')

classification_f1_scores = []
classification_accuracy_scores = []

# 評估testing data的表現
pbar = tqdm(dl_test)
pbar.set_description("Evaluating on test set")
classification_model.eval()

for batch in pbar:
    input_text = {k: v.to(device) for k, v in batch['input_text'].items()}
    labels2 = batch['labels2'].to(device)

    with torch.no_grad():
        entailment_judgement = classification_model(**input_text)

    acc.update(entailment_judgement, labels2)
    f1.update(entailment_judgement, labels2)

    classification_accuracy_scores.append(acc.compute().item())
    classification_f1_scores.append(f1.compute().item())

classification_accuracy_score = acc.compute()
classification_f1_score = f1.compute()
print(f"Test Set - Accuracy: {classification_accuracy_score:.4f}, F1 Score: {classification_f1_score:.4f}")

# chatGPT: 畫出Spearman Correlation, Accuracy, F1 Score
plt.figure(figsize=(12, 6))
sns.set_style("whitegrid")

# Spearman Correlation
plt.subplot(1, 3, 1)
plt.plot(regression_spearman_scores, label='Spearman Correlation', color='blue')
plt.xlabel('Batch')
plt.ylabel('Score')
plt.title('Spearman Correlation per Batch')
plt.ylim(0.5, 1)
plt.legend()

# Accuracy
plt.subplot(1, 3, 2)
plt.plot(classification_accuracy_scores, label='Accuracy', color='green')
plt.xlabel('Batch')
plt.ylabel('Score')
plt.title('Accuracy per Batch')
plt.ylim(0.5, 1)
plt.legend()

# F1 Score
plt.subplot(1, 3, 3)
plt.plot(classification_f1_scores, label='F1 Score', color='red')
plt.xlabel('Batch')
plt.ylabel('Score')
plt.title('F1 Score per Batch')
plt.ylim(0.5, 1)
plt.legend()

plt.tight_layout()
plt.show()

spc.reset()
acc.reset()
f1.reset()

