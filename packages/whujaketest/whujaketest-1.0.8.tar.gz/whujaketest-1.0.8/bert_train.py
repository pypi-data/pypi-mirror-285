import numpy as np 
import pandas as pd 
 
import torch 
from torch.utils.data import DataLoader 
 
import datasets
import re
import numpy as np
import pandas as pd
# 加载数据集
file_path = 'results/train_data.csv'
data = pd.read_csv(file_path)

# 合并相关文本列进行分析
data['text'] = data['title'].fillna('') + " " + data['company_profile'].fillna('') + " " + data['description'] + " " + data['requirements'].fillna('') + " " + data['benefits'].fillna('')

# 清理文本数据
def clean_text(text):
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text, re.I|re.A)
    text = text.lower()
    text = text.strip()
    return text

data['text'] = data['text'].apply(clean_text)

data['labels'] = data['fraudulent']
data=data[['labels','text']]
# data['fraudulent'] = data['fraudulent']
ds = datasets.Dataset.from_pandas(data) 


from transformers import AutoTokenizer #BertTokenizer
tokenizer = AutoTokenizer.from_pretrained(r'C:\Users\zx\.cache\modelscope\hub\tiansz\bert-base-chinese') #需要和模型一致
# print(tokenizer)

#分割成训练集和测试集

ds_encoded = ds.map(lambda example:tokenizer(example["text"],
                    max_length=100,truncation=True,padding='max_length'),
                    batched=True,
                    batch_size=20,
                    num_proc=1) #支持批处理和多进程map

print(ds_encoded[0])
#转换成pytorch中的tensor 
print("----")
ds_encoded.set_format(type="torch",columns = ["input_ids",'attention_mask','token_type_ids','labels'])
#ds_encoded.reset_format() 
print(ds_encoded[0])



ds_train_val,ds_test = ds_encoded.train_test_split(test_size=0.2).values()
ds_train,ds_val = ds_train_val.train_test_split(test_size=0.2).values()

#转换成pytorch中的tensor 
# ds_encoded.set_format(type="torch",columns = ["input_ids",'attention_mask','token_type_ids','labels'])
#ds_encoded.reset_format() 
# print(ds_encoded[0])

def collate_fn(examples):
    return tokenizer.pad(examples) #return_tensors='pt'
 
#以下方式等价
#from transformers import DataCollatorWithPadding
#collate_fn = DataCollatorWithPadding(tokenizer=tokenizer)
 
dl_train = torch.utils.data.DataLoader(ds_train, batch_size=16, collate_fn = collate_fn)
dl_val = torch.utils.data.DataLoader(ds_val, batch_size=16,  collate_fn = collate_fn)
dl_test = torch.utils.data.DataLoader(ds_test, batch_size=16,  collate_fn = collate_fn)

from transformers import AutoModelForSequenceClassification 
 
#加载模型 (会添加针对特定任务类型的Head)
model = AutoModelForSequenceClassification.from_pretrained(r'C:\Users\zx\.cache\modelscope\hub\tiansz\bert-base-chinese',num_labels=2)
print(dict(model.named_children()).keys() )



from torchkeras import KerasModel 
 
#我们需要修改StepRunner以适应transformers的数据集格式
 
class StepRunner:
    def __init__(self, net, loss_fn, accelerator, stage = "train", metrics_dict = None, 
                 optimizer = None, lr_scheduler = None
                 ):
        self.net,self.loss_fn,self.metrics_dict,self.stage = net,loss_fn,metrics_dict,stage
        self.optimizer,self.lr_scheduler = optimizer,lr_scheduler
        self.accelerator = accelerator
        if self.stage=='train':
            self.net.train() 
        else:
            self.net.eval()
    
    def __call__(self, batch):
        
        out = self.net(**batch)
        
        #loss
        loss= out.loss
        
        #preds
        preds =(out.logits).argmax(axis=1) 
    
        #backward()
        if self.optimizer is not None and self.stage=="train":
            self.accelerator.backward(loss)
            self.optimizer.step()
            if self.lr_scheduler is not None:
                self.lr_scheduler.step()
            self.optimizer.zero_grad()
        
        all_loss = self.accelerator.gather(loss).sum()
        
        labels = batch['labels']
        acc = (preds==labels).sum()/((labels>-1).sum())
        
        all_acc = self.accelerator.gather(acc).mean()
        
        #losses
        step_losses = {self.stage+"_loss":all_loss.item(), self.stage+'_acc':all_acc.item()}
        
        #metrics
        step_metrics = {}
        
        if self.stage=="train":
            if self.optimizer is not None:
                step_metrics['lr'] = self.optimizer.state_dict()['param_groups'][0]['lr']
            else:
                step_metrics['lr'] = 0.0
        return step_losses,step_metrics
    
KerasModel.StepRunner = StepRunner


optimizer = torch.optim.AdamW(model.parameters(), lr=3e-5)

from torchkeras import KerasModel

keras_model = KerasModel(model,
                   loss_fn=None,
                   optimizer = optimizer
                   )

keras_model.fit(
    train_data = dl_train,
    val_data= dl_val,
    ckpt_path='bert_waimai.pt',
    epochs=10,
    patience=10,
    monitor="val_acc", 
    mode="max",
    plot = True,
    wandb = False,
    quiet = True
)
import evaluate
metric = evaluate.load("accuracy")
model.eval()
dl_test = keras_model.accelerator.prepare(dl_test)
for batch in dl_test:
    with torch.no_grad():
        outputs = model(**batch)
 
    logits = outputs.logits
    predictions = torch.argmax(logits, dim=-1)
    metric.add_batch(predictions=predictions, references=batch["labels"])
 
metric.compute()

