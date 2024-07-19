# from huggingface_hub import notebook_login
import torch


# # 将训练好的模型提交到 huggingface
# notebook_login()

from transformers import AutoModel
from torch import nn
import transformers
from transformers import AutoTokenizer, DistilBertForSequenceClassification

access_token = "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"


# pt_model = DistilBertForSequenceClassification.from_pretrained("PyModelComplete.pt", from_tf=True,token=access_token)
# pt_model.save_pretrained("PyModelComplete.pt")

# model = AutoModel.from_pretrained("private/model", token=access_token)

# Save the entire model, and get it back
# torch.save(model_pt, 'PyModelComplete.pt')
# model_reloaded2 = torch.load('PyModelComplete.pt')
# # model_reloaded2.eval()
# model_reloaded2.pu

# config = transformers.DistilBertConfig(dropout=0.2, attention_dropout=0.2)
# dbert_pt = transformers.DistilBertModel.from_pretrained('distilbert-base-uncased', config=config)
# class DistilBertClassification(nn.Module):
#     def __init__(self):
#         super(DistilBertClassification, self).__init__()
#         self.dbert = dbert_pt
#         self.dropout = nn.Dropout(p=0.2)
#         self.linear1 = nn.Linear(768,64)
#         self.ReLu = nn.ReLU()
#         self.linear2 = nn.Linear(64,5)

#     def forward(self, x):
#         x = self.dbert(input_ids=x)
#         x = x["last_hidden_state"][:,0,:]
#         x = self.dropout(x)
#         x = self.linear1(x)
#         x = self.ReLu(x)
#         logits = self.linear2(x)
#         # No need for a softmax, because it is already included in the CrossEntropyLoss
#         return logits

# # Get cpu or gpu device for training.
# device = "cuda" if torch.cuda.is_available() else "cpu"
# print(f"Using {device} device")
# model_pt = DistilBertClassification().to(device)
# model_pt._save_to_state_dict

pt_model = DistilBertForSequenceClassification.from_pretrained("./export_models/PyModelComplete.pt", from_tf=False)
# pt_model.save_pretrained("path/to/awesome-name-you-picked")