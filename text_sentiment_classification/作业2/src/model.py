import torch
import torch.nn as nn
import torch.nn.functional as F

class Config:
    update_word2vec = True      # whether to update word2vec
    embedding_dim = 50          # dimension of word embedding
    hidden_num = 128            # number of hidden units
    num_classes = 2             # number of classes
    num_layers = 2              # number of hidden layers
    dropout = 0.2               # the probability for dropout
    kernel_num = 32            # number of kernel in convolutional layer
    kernel_sizes = [3, 5, 7]    # sizes of kernels in convolutional layer
    # TODO: set vocab_size
    vocab_size = 0              # number of words + 1
    # TODO: set pre_trained
    pre_trained = None          # use vector_char trained by word2vec
    def __init__(self, word_id_dict, word_vectors):
        self.vocab_size = len(word_id_dict) + 1
        self.pre_trained = word_vectors

class TextCNN(nn.Module):
    def __init__(self, config: Config):
        super(TextCNN, self).__init__()
        self.config = config
        # set the pre-trained word vector
        self.embedding = nn.Embedding(config.vocab_size, config.embedding_dim)
        self.embedding.weight.requires_grad = config.update_word2vec
        self.embedding.weight.data.copy_(torch.from_numpy(config.pre_trained))
        # convolutional layer
        self.convs = [nn.Conv2d(1, config.kernel_num, (k, config.embedding_dim)) for k in config.kernel_sizes]
        # full connection layer
        self.fc = nn.Linear(config.kernel_num * len(config.kernel_sizes), config.num_classes)
        # dropout
        self.dropout = nn.Dropout(config.dropout)
        # initialize weights
        for n, p in self.named_parameters():
            if p.requires_grad:
                torch.nn.init.normal_(p, mean = 0, std = 0.01)

    # convolution and pooling
    def conv_and_pool(self, x: torch.Tensor, conv: nn.Conv2d):
        # convolve tensor x with conv
        # use relu as activation function
        # squeeze the last dimension
        x = F.relu(conv(x).squeeze(3))
        # max pooling
        x = F.max_pool1d(x, x.size(2)).squeeze(2)
        return x
    
    def forward(self, x: torch.Tensor):
        out = self.embedding(x.to(torch.int64))
        out = out.unsqueeze(1)
        out = torch.cat([self.conv_and_pool(out, conv) for conv in self.convs], dim=1)
        out = self.dropout(out)
        out = self.fc(out)
        out = F.log_softmax(out, dim=1)
        return (out)
    
class RNNLSTM(nn.Module):
    def __init__(self, config: Config):
        super(RNNLSTM, self).__init__()
        self.config = config
        # set the pre-trained word vector
        self.embedding = nn.Embedding(config.vocab_size, config.embedding_dim)
        self.embedding.weight.requires_grad = config.update_word2vec
        self.embedding.weight.data.copy_(torch.from_numpy(config.pre_trained))
        # LSTM layer
        self.lstm = nn.LSTM(input_size=config.embedding_dim, hidden_size=config.hidden_num, num_layers=config.num_layers, bidirectional=True)
        # full connection layer
        self.fc = nn.Linear(config.hidden_num * 2, config.num_classes)
        # dropout
        self.dropout = nn.Dropout(config.dropout)
        # initialize weights
        for n, p in self.named_parameters():
            if p.requires_grad:
                torch.nn.init.normal_(p, mean = 0, std = 0.01)
        
    def forward(self, x: torch.Tensor):
        output, (h_n, c_n) = self.lstm(self.embedding(x.to(torch.int64)).permute(1, 0, 2)) # permute to fit LSTM with shape (seq_len(2 * num_layers), batch, hidden_size)
        # output: (seq_len, batch, num_directions * hidden_size)
        # h_n: (num_layers * num_directions, batch, hidden_size)
        # c_n: (num_layers * num_directions, batch, hidden_size)
        h_n = h_n.view(self.config.num_layers, 2, -1, self.config.hidden_num)       # get the last layer of hidden state
        h_n = torch.cat((h_n[-1, 0, :, :], h_n[-1, 1, :, :]), dim=1)                # concatenate the last layer of hidden state
        h_n = self.dropout(h_n)
        h_n = self.fc(h_n)
        return h_n
    
class MLP(nn.Module):
    def __init__(self, config: Config):
        super(MLP, self).__init__()
        self.config = config
        # set the pre-trained word vector
        self.embedding = nn.Embedding(config.vocab_size, config.embedding_dim)
        self.embedding.weight.requires_grad = config.update_word2vec
        self.embedding.weight.data.copy_(torch.from_numpy(config.pre_trained))
        self.ReLU = nn.ReLU()
        # full connection layer
        self.fc = nn.Linear(config.embedding_dim, config.hidden_num)
        # linear layer
        self.linear = nn.Linear(config.hidden_num, config.num_classes)
        # initialize weights
        for n, p in self.named_parameters():
            if p.requires_grad:
                torch.nn.init.normal_(p, mean = 0, std = 0.01)
        
    def forward(self, x: torch.Tensor):
        out = self.embedding(x.to(torch.int64))
        out = self.fc(out)                                  # full connection
        out = self.ReLU(out).permute(0, 2, 1)               # permute to fit max_pool1d
        out = F.max_pool1d(out, out.size(2)).squeeze(2)     # max pooling to get the most important feature
        out = self.linear(out)                              # linear layer
        return out