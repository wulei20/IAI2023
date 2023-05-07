import functools
import time
import os
import numpy as np
import torch
import gensim
from torch.utils.data import DataLoader, TensorDataset

def show_fn_time(fn: callable):
    """
    Decorator to show how long a function takes to run
    """
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        start = time.time()
        print(f"Running {fn.__name__}...")
        result = fn(*args, **kwargs)
        end = time.time()
        print(f"{fn.__name__} took {end - start} seconds")
        return result
    return wrapper

DATASET_PATH = os.path.join(os.path.dirname(__file__), "..", "Dataset\\")
WORD_DICT_FILE_LIST = [DATASET_PATH + "test.txt", DATASET_PATH + "train.txt"]
WIKI_WORD2VEC_FILE = DATASET_PATH + "wiki_word2vec_50.bin"
MAX_LINE_WORD_LENGTH = 100
class DataReader:
    """
    Class to read data from a file
    """
    def __init__(self):
        self.word_id_dict = self.generate_word_id_dict()
        self.word_vectors = self.read_word2vec_file()

    @show_fn_time
    def generate_word_id_dict(self, path_list: list = WORD_DICT_FILE_LIST) -> dict:
        """
        Generate a dictionary of words and their ids
        """
        word_id_dict = {}
        for path in path_list:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip().split()
                    for word in line[1:]:
                        if word not in word_id_dict:
                            word_id_dict[word] = len(word_id_dict)
        print(len(word_id_dict))
        return word_id_dict

    @show_fn_time
    def read_word2vec_file(self, path: str = WIKI_WORD2VEC_FILE) -> np.ndarray[np.float64]:
        """
        Read a word2vec bin file and return NDArray of word vectors
        """
        model = gensim.models.KeyedVectors.load_word2vec_format(path, binary=True)
        word_vectors = np.array(np.zeros([len(self.word_id_dict) + 1, model.vector_size]))
        for word, id in self.word_id_dict.items():
            if word in model:
                word_vectors[id] = model[word]
            else:
                pass
        return word_vectors
    
    @show_fn_time
    def read_file(self, path: str) -> tuple[np.ndarray[np.int64], np.ndarray[np.int64]]:
        """
        Read a corpus file and return NDArray of sentences with word ids and classifications
        """
        sentences_with_word_id = np.array([])
        classifications = np.array([])  
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip().split()
                classifications = np.append(classifications, int(line[0]))
                content = np.array([])
                for word in line[1:]:
                    content = np.append(content, self.word_id_dict[word] if word in self.word_id_dict else 0)
                if len(content) < MAX_LINE_WORD_LENGTH:
                    content = np.append(content, np.zeros(MAX_LINE_WORD_LENGTH - len(content)))
                else:
                    content = content[:MAX_LINE_WORD_LENGTH]
                sentences_with_word_id = np.vstack((sentences_with_word_id, content)) if sentences_with_word_id.size else content
        return sentences_with_word_id, classifications
    
    @show_fn_time
    def read_Corpus(self, batch_size: int = 64) -> DataLoader[3]:
        """
        Read corpus files and return DataLoader
        """
        train_sentences_with_word_id, train_classifications = self.read_file(DATASET_PATH + "train.txt")
        test_sentences_with_word_id, test_classifications = self.read_file(DATASET_PATH + "test.txt")
        validation_sentences_with_word_id, validation_classifications = self.read_file(DATASET_PATH + "validation.txt")
        train_dataset = TensorDataset(torch.from_numpy(train_sentences_with_word_id).type(torch.float), torch.from_numpy(train_classifications).type(torch.long))
        test_dataset = TensorDataset(torch.from_numpy(test_sentences_with_word_id).type(torch.float), torch.from_numpy(test_classifications).type(torch.long))
        validation_dataset = TensorDataset(torch.from_numpy(validation_sentences_with_word_id).type(torch.float), torch.from_numpy(validation_classifications).type(torch.long))
        train_dataloader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=2)
        test_dataloader = DataLoader(test_dataset, batch_size=batch_size, shuffle=True, num_workers=2)
        validation_dataloader = DataLoader(validation_dataset, batch_size=batch_size, shuffle=True, num_workers=2)
        return train_dataloader, test_dataloader, validation_dataloader