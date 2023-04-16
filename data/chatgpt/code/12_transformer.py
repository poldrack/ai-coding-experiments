# create python code to implement a three-layer transformer model, and train that model using a small text corpus.
# failed with import error on first try
# failed with import error on the second try, gpt4 switched to torchtext.legacy
# failed again with import error - can't seem to figure out how to use the newest version - asked to generate code without using torchtext


import torch
import torch.nn as nn
import torch.optim as optim
from torchtext.legacy.data import Field, TabularDataset, BucketIterator
import spacy
import pandas as pd

# Define the Transformer model
class TransformerModel(nn.Module):
    def __init__(self, vocab_size, d_model, nhead, num_layers, dim_feedforward):
        super(TransformerModel, self).__init__()
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.transformer = nn.Transformer(d_model, nhead, num_layers, dim_feedforward)
        self.fc = nn.Linear(d_model, vocab_size)

    def forward(self, x):
        x = self.embedding(x)
        x = self.transformer(x)
        x = self.fc(x)
        return x

# Preprocess the dataset
spacy_en = spacy.load('en_core_web_sm')

def tokenize(text):
    return [tok.text for tok in spacy_en.tokenizer(text)]

with open('small_corpus.txt', 'r') as f:
    text = f.read()

tokenized_text = tokenize(text)
df = pd.DataFrame(tokenized_text, columns=['tokens'])
df.to_csv('small_corpus_tokens.csv', index=False)

# Set up the dataset and data iterator
TEXT = Field(sequential=True, tokenize=tokenize, lower=True, init_token='<sos>', eos_token='<eos>')
data_fields = [('tokens', TEXT)]

train_data = TabularDataset(path='small_corpus_tokens.csv', format='csv', fields=data_fields)
TEXT.build_vocab(train_data)

train_iter = BucketIterator(train_data, batch_size=32, sort_key=lambda x: len(x.tokens), device='cuda')

# Initialize the model, loss, and optimizer
vocab_size = len(TEXT.vocab)
d_model = 512
nhead = 8
num_layers = 3
dim_feedforward = 2048

model = TransformerModel(vocab_size, d_model, nhead, num_layers, dim_feedforward)
model.to('cuda')

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters())

# Train the model
num_epochs = 10

for epoch in range(num_epochs):
    model.train()
    total_loss = 0
    for i, batch in enumerate(train_iter):
        data, targets = batch.tokens[:-1], batch.tokens[1:]
        optimizer.zero_grad()
        outputs = model(data)
        loss = criterion(outputs.view(-1, vocab_size), targets.view(-1))
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    print(f"Epoch: {epoch+1}, Loss: {total_loss / len(train_iter)}")
