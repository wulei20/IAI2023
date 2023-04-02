import json
from tqdm import tqdm
import functools
import time
import os
from pypinyin import lazy_pinyin
from constant import *

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

class DataPreprocessor():
    def __init__(self):
        self.mkpath()
        self.s2c_table = None
        self.c2s_table = None
        if os.path.exists(S2C_TABLE_PATH) and os.path.exists(C2S_TABLE_PATH):
            with open(S2C_TABLE_PATH, 'r', encoding='utf-8') as f:
                self.s2c_table = json.load(f)
            with open(C2S_TABLE_PATH, 'r', encoding='utf-8') as f:
                self.c2s_table = json.load(f)

    @show_fn_time
    def reconstitute_character_spell_data(self) -> None:
        """
        Reconstitute the character & spell data from the file
        """
        with open(CHARACTER_PATH, 'r', encoding='gbk') as f:
            character_list = list(f.read().strip())
        s2c_table = {}      # spell to character table
        c2s_table = {}      # character to spell table
        with open(SPELL_CHATACTER_RELATIVE_PATH, 'r', encoding='gbk') as f:
            for line in f:
                line = line.split()
                spell = line[0]
                s2c_table[spell] = []
                for character in line[1:]:
                    if character in character_list:
                        s2c_table[spell].append(character)
                        if character not in c2s_table:
                            c2s_table[character] = []
                        c2s_table[character].append(spell)
                    else:
                        print(f"Character {character} not in character list")
        with open(S2C_TABLE_PATH, 'w', encoding='utf-8') as f:
            json.dump(s2c_table, f, ensure_ascii=False)
        with open(C2S_TABLE_PATH, 'w', encoding='utf-8') as f:
            json.dump(c2s_table, f, ensure_ascii=False)
        self.s2c_table = s2c_table
        self.c2s_table = c2s_table

    def get_corpus_files(self, corpus_dir: str) -> list[str]:
        """
        Returns a list of all files in the corpus directory
        """
        return [os.path.join(corpus_dir, f) for f in os.listdir(corpus_dir) if f.endswith(".txt") and f != "README.txt"]

    @show_fn_time
    def strip_sina_news_corpus(self) -> None:
        """
        Strips the Sina News corpus
        Removes all the html tags and unrelated fields
        Add spellings to the title and html
        Format: [(title, title_spell), (html, html_spell), ...]
        """
        corpus_files = self.get_corpus_files(SINA_NEWS_CORPUS_DIR)
        for file_name in corpus_files:
            print(f"Processing {file_name}")
            with open(file_name, 'r', encoding='gbk') as f:
                with open(os.path.join(SINA_NEWS_CORPUS_OUTPUT_DIR, os.path.basename(file_name)), 'w', encoding='utf-8') as f_out:
                    num_lines = sum(1 for line in f)
                    f_out.write('[')
                    f.seek(0)
                    for (i, line) in enumerate(tqdm(f, total=num_lines)):
                        json_term = json.loads(line)
                        title_spell = lazy_pinyin(json_term['title'], errors = lambda item: ['*' for i in range(len(item))])
                        html_spell = lazy_pinyin(json_term['html'], errors = lambda item: ['*' for i in range(len(item))])
                        json.dump((json_term['title'], title_spell), f_out, ensure_ascii=False)
                        f_out.write(', ')
                        json.dump((json_term['html'], html_spell), f_out, ensure_ascii=False)
                        if i < num_lines - 1:
                            f_out.write(', ')
                    f_out.write(']')

    @show_fn_time
    def count_unit_and_tuple_occurance(self):
        """
        Count the occurance of each unit and tuple
        """
        corpus_files = self.get_corpus_files(SINA_NEWS_CORPUS_OUTPUT_DIR)
        unit_occurance = {}     # with the format of {"spell character": occurance}
        tuple_occurance = {}    # with the format of {"spell character": {"next spell character": occurance}}
        for file_name in corpus_files:
            print(f"Processing {file_name}")
            with open(file_name, 'r', encoding='utf-8') as f:
                sentence_spell_list = json.load(f)
            for sentence, spell in tqdm(sentence_spell_list):
                for i in range(len(sentence)):
                    if sentence[i] not in self.c2s_table:
                        continue
                    # count unit occurance
                    c_s_str = sentence[i] + ' ' + spell[i]
                    if c_s_str not in unit_occurance:
                        unit_occurance[c_s_str] = 0
                    unit_occurance[c_s_str] += 1
                    # count tuple occurance
                    if i < len(sentence) - 1 and sentence[i + 1] in self.c2s_table:
                        c_s_str_next = sentence[i + 1] + ' ' + spell[i + 1]
                        if c_s_str not in tuple_occurance:
                            tuple_occurance[c_s_str] = {}
                        if c_s_str_next not in tuple_occurance[c_s_str]:
                            tuple_occurance[c_s_str][c_s_str_next] = 0
                        tuple_occurance[c_s_str][c_s_str_next] += 1
        with open(UNIT_OCCURANCE_PATH, 'w', encoding='utf-8') as f:
            json.dump(unit_occurance, f, ensure_ascii=False)
        with open(TUPLE_OCCURANCE_PATH, 'w', encoding='utf-8') as f:
            json.dump(tuple_occurance, f, ensure_ascii=False)

    @show_fn_time
    def count_triple_occurance(self):
        """
        Count the occurance of each triple
        """
        corpus_files = self.get_corpus_files(SINA_NEWS_CORPUS_OUTPUT_DIR)
        triple_occurance = {}   # with the format of {"spell character": {"next spell character": {"next next spell character": occurance}}}
        for file_name in corpus_files:
            print(f"Processing {file_name}")
            with open(file_name, 'r', encoding='utf-8') as f:
                sentence_spell_list = json.load(f)
            for sentence, spell in tqdm(sentence_spell_list):
                for i in range(len(sentence)):
                    if sentence[i] not in self.c2s_table or \
                        i >= len(sentence) - 2 or \
                        sentence[i + 1] not in self.c2s_table or \
                        sentence[i + 2] not in self.c2s_table:
                        continue
                    # count triple occurance
                    c_s_str = sentence[i] + ' ' + spell[i]
                    c_s_str_next = sentence[i + 1] + ' ' + spell[i + 1]
                    c_s_str_next_next = sentence[i + 2] + ' ' + spell[i + 2]
                    if c_s_str not in triple_occurance:
                        triple_occurance[c_s_str] = {}
                    if c_s_str_next not in triple_occurance[c_s_str]:
                        triple_occurance[c_s_str][c_s_str_next] = {}
                    if c_s_str_next_next not in triple_occurance[c_s_str][c_s_str_next]:
                        triple_occurance[c_s_str][c_s_str_next][c_s_str_next_next] = 0
                    triple_occurance[c_s_str][c_s_str_next][c_s_str_next_next] += 1
        with open(TRIPLE_OCCURANCE_PATH, 'w', encoding='utf-8') as f:
            json.dump(triple_occurance, f, ensure_ascii=False)
            
    def mkpath(self):
        if not os.path.exists(PRETRAIN_DIR):
            os.makedirs(PRETRAIN_DIR)
        if not os.path.exists(SINA_NEWS_CORPUS_OUTPUT_DIR):
            os.makedirs(SINA_NEWS_CORPUS_OUTPUT_DIR)

    # the following functions are used to fix a bug in the preprocessing process
    # at first I forgot to remove the last comma after the last sentence in each json file
    # which means the last sentence in each json file still need a value after the comma
    # or the json file will be invalid to be loaded
    # so I wrote these functions to fix it
    # however, I found that the first method is not working
    # since using the file pointer to read each character and find the last comma takes too much time
    # so I wrote the second method to fix it
    # which is to read the whole file into a string and then find the last comma by iterating the string from the end
    # then save it back to the file
    # I thought the second method would be slower than the first one
    # since the first method only need to read the file once
    # while the second method need to read the file and rewrite the file
    # but it turns out that the second method is much faster than the first one
    # really weird
    # maybe related to the file system

    # def substitute_last_comma(self):
    #     corpus_files = self.get_corpus_files(SINA_NEWS_CORPUS_OUTPUT_DIR)
    #     for file_name in corpus_files:
    #         print(f"Processing {file_name}")
    #         with open(file_name, 'r', encoding='utf-8') as f:
    #             str = f.read()
    #             print(len(str))
    #             for i in range(len(str) - 1, -1, -1):
    #                 if str[i] == ',':
    #                     str = str[:i] + ' ' + str[i + 1:]
    #                     break
    #         with open(file_name, 'w', encoding='utf-8') as f:
    #             f.write(str)

    # def reset_comma(self):
    #     corpus_files = self.get_corpus_files(SINA_NEWS_CORPUS_OUTPUT_DIR)
    #     for file_name in corpus_files:
    #         with open(file_name, 'r+', encoding='utf-8') as f:
    #             cnt = 0
    #             while True:
    #                 char = f.read(1)
    #                 if not char:
    #                     break
    #                 if char == '"':
    #                     cnt += 1
    #                     if cnt == 2:
    #                         last_comma_pos = f.tell()
    #                         break
    #             f.seek(last_comma_pos)
    #             f.write(',')

if __name__ == '__main__':
    data_preprocessor = DataPreprocessor()
    data_preprocessor.reconstitute_character_spell_data()
    data_preprocessor.strip_sina_news_corpus()
    data_preprocessor.count_unit_and_tuple_occurance()
    data_preprocessor.count_triple_occurance()
    