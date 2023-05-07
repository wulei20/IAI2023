from data_reader import DataReader, show_fn_time
import argparse
import torch
from model import TextCNN, RNNLSTM, MLP, Config
from tqdm import tqdm
from sklearn.metrics import f1_score
import numpy as np
import wandb

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

def parse_input():
    parser = argparse.ArgumentParser(description="Sentiment Analysis")
    parser.add_argument("--model", type=str, default="CNN", help="Model to use: CNN, RNN, MLP")
    parser.add_argument("--learning_rate", type=float, default=0.001, help="Learning rate")
    parser.add_argument("--epoch", type=int, default=10, help="Number of epochs")
    parser.add_argument("--batch_size", type=int, default=64, help="Batch size")
    parser.add_argument("--dropout", type=float, default=0.2, help="Dropout rate")
    args = parser.parse_args()
    if (args.model == "CNN"):
        Model = TextCNN
    elif (args.model == "RNN"):
        Model = RNNLSTM
    elif (args.model == "MLP"):
        Model = MLP
    else:
        raise ValueError("Invalid model")
    return Model, args.learning_rate, args.epoch, args.batch_size, args.dropout

def train(data_loader, model, optimizer, criterion, scheduler, batch_size):
    model.train()
    train_loss, train_acc = 0, 0
    sum, correct = 0, 0
    true, pred = [], []
    for x, y in data_loader:
        x, y = x.to(DEVICE), y.to(DEVICE)
        optimizer.zero_grad()
        y_pred = model(x)
        loss = criterion(y_pred, y)
        loss.backward()
        optimizer.step()
        train_loss += loss.item()
        sum += y.size(0)
        correct += (y_pred.argmax(dim=1) == y).float().sum().item()
        true.extend(y.cpu().numpy().tolist())
        pred.extend(y_pred.argmax(dim=1).cpu().numpy().tolist())
    train_acc = correct / sum
    train_loss *= batch_size
    train_loss /= len(data_loader)
    scheduler.step()
    f1 = f1_score(np.array(true), np.array(pred), average="binary")
    return train_loss, train_acc, f1

def validation_or_test(data_loader, model, criterion, batch_size):
    model.eval()
    valid_loss, valid_acc = 0, 0
    sum, correct = 0, 0
    true, pred = [], []
    for x, y in data_loader:
        x, y = x.to(DEVICE), y.to(DEVICE)
        y_pred = model(x)
        loss = criterion(y_pred, y)
        valid_loss += loss.item()
        sum += y.size(0)
        correct += (y_pred.argmax(dim=1) == y).float().sum().item()
        true.extend(y.cpu().numpy().tolist())
        pred.extend(y_pred.argmax(dim=1).cpu().numpy().tolist())
    valid_acc = correct / sum
    valid_loss *= batch_size
    valid_loss /= len(data_loader)
    f1 = f1_score(np.array(true), np.array(pred), average="binary")
    return valid_loss, valid_acc, f1

if __name__ == "__main__":
    Model, learning_rate, epoch, batch_size, dropout = parse_input()
    data_reader = DataReader()
    train_loader, test_loader, validation_loader = data_reader.read_Corpus(batch_size)
    config = Config(data_reader.word_id_dict, data_reader.word_vectors)
    config.dropout = dropout
    model = Model(config).to(DEVICE)
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    criterion = torch.nn.CrossEntropyLoss()
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=4, gamma=0.6)
    wandb.init(project="sentiment-analysis", name=f"{Model.__name__}_{learning_rate}_{epoch}_{batch_size}_{dropout}")
    wandb.config.update({"model": Model.__name__, "learning_rate": learning_rate, "epoch": epoch, "batch_size": batch_size, "dropout": dropout})
    for i in tqdm(range(epoch)):
        train_loss, train_acc, train_f1 = train(train_loader, model, optimizer, criterion, scheduler, batch_size)
        validation_loss, validation_acc, validation_f1 = validation_or_test(validation_loader, model, criterion, batch_size)
        test_loss, test_acc, test_f1 = validation_or_test(test_loader, model, criterion, batch_size)
        wandb.log({"train_loss": train_loss, "train_acc": train_acc, "train_f1": train_f1, "validation_loss": validation_loss, "validation_acc": validation_acc, "validation_f1": validation_f1, "test_loss": test_loss, "test_acc": test_acc, "test_f1": test_f1})
        print(f"Epoch {i + 1}: train_loss: {train_loss:.4f}, train_acc: {train_acc:.4f}, train_f1: {train_f1:.4f}, validation_loss: {validation_loss:.4f}, validation_acc: {validation_acc:.4f}, validation_f1: {validation_f1:.4f}, test_loss: {test_loss:.4f}, test_acc: {test_acc:.4f}, test_f1: {test_f1:.4f}")
    torch.save(model.state_dict(), "trained_model/model_{Model.__name__}_{learning_rate}_{epoch}_{batch_size}_{dropout}.pt")
