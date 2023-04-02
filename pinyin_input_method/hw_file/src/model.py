from constant import *
import json
import math

class BinaryModel:
    def __init__(self, alpha: float = 0.999) -> None:
        # alpha is the weight of the tuple probability, 1 - alpha is the weight of the unit probability
        self.alpha = alpha
        with open(UNIT_OCCURANCE_PATH, 'r', encoding='utf-8') as f:
            self.unit_occurance = json.load(f)
        sum = 0
        for key in self.unit_occurance:
            sum += self.unit_occurance[key]
        self.CHARACTER_SUM = sum
        with open(TUPLE_OCCURANCE_PATH, 'r', encoding='utf-8') as f:
            self.tuple_occurance = json.load(f)
        with open(S2C_TABLE_PATH, 'r', encoding='utf-8') as f:
            self.s2c_table = json.load(f)
    
    def calculate_most_likely_sentence(self, spell: str) -> str:
        """
        Calculate the most likely sentence given the spell
        """
        spell = list(map(lambda item : item.lower(), spell.split(' ')))
        pypinyin_spell = list(map(lambda item : item.replace('lue', 'lve').replace('nue', 'nve'), spell))
        # Initialize the probability list and character chain list
        # with the format of [{c_s_str: prob, ...}, {c_s_str: prob, ...}, ...]
        # prob_list[i][c_s_str] means the probability of the most likely sentence ending with c_s_str
        prob_list = [{} for i in range(len(spell))]
        # with the format of [{c_s_str: c_s_str_prev, ...}, {c_s_str: c_s_str_prev, ...}, ...]
        # character_chain_list[i][c_s_str] means the previous character chain of c_s_str
        character_chain_list = [{} for i in range(len(spell))]
        # Initialize the first character
        for character in self.s2c_table[spell[0]]:
            if (character + ' ' + pypinyin_spell[0]) in self.unit_occurance:
                prob_list[0][character + ' ' + pypinyin_spell[0]] = math.log(self.unit_occurance[character + ' ' + pypinyin_spell[0]])
                character_chain_list[0][character + ' ' + pypinyin_spell[0]] = ''
        # Calculate the probability of each character
        for i in range(len(spell) - 1):
            for character in self.s2c_table[spell[i + 1]]:
                c_s_str = character + ' ' + pypinyin_spell[i + 1]
                if c_s_str in self.unit_occurance:
                    for c_s_str_prev in prob_list[i]:
                        if (c_s_str_prev in self.tuple_occurance) and (c_s_str in self.tuple_occurance[c_s_str_prev]):
                            prob = math.log (self.alpha * (self.tuple_occurance[c_s_str_prev][c_s_str]) / self.unit_occurance[c_s_str_prev] \
                                              + (1 - self.alpha) * self.unit_occurance[c_s_str] / self.CHARACTER_SUM)
                        else:
                            prob = math.log((1 - self.alpha) * self.unit_occurance[c_s_str] / self.CHARACTER_SUM)
                        if (c_s_str not in prob_list[i + 1]) or (prob_list[i + 1][c_s_str] < prob_list[i][c_s_str_prev] + prob):
                            prob_list[i + 1][c_s_str] = prob_list[i][c_s_str_prev] + prob
                            character_chain_list[i + 1][c_s_str] = c_s_str_prev
        max_prob = float('-inf')
        max_prob_end = ''
        # Find the most likely sentence
        for c_s_str in prob_list[-1]:
            if prob_list[-1][c_s_str] > max_prob:
                max_prob = prob_list[-1][c_s_str]
                max_prob_end = c_s_str
        ret_sentence = ''
        # Backtrace to get the most likely sentence
        for i in range(len(spell) - 1, -1, -1):
            ret_sentence = max_prob_end[0] + ret_sentence
            max_prob_end = character_chain_list[i][max_prob_end]
        return ret_sentence
    
class TrigramModel:
    def __init__(self, alpha: float = 0.999, beta: float = 0.99) -> None:
        # beta is the weight of the triple probability, (1 - beta) * alpha is the weight of the tuple probability
        # (1 - beta) * (1 - alpha) is the weight of the unit probability
        # which means the weight of the tuple probability compared to the unit probability is still alpha / (1 - alpha)
        self.alpha = alpha
        self.beta = beta
        with open(UNIT_OCCURANCE_PATH, 'r', encoding='utf-8') as f:
            self.unit_occurance = json.load(f)
        sum = 0
        for key in self.unit_occurance:
            sum += self.unit_occurance[key]
        self.CHARACTER_SUM = sum
        with open(TUPLE_OCCURANCE_PATH, 'r', encoding='utf-8') as f:
            self.tuple_occurance = json.load(f)
        with open(TRIPLE_OCCURANCE_PATH, 'r', encoding='utf-8') as f:
            self.triple_occurance = json.load(f)
        with open(S2C_TABLE_PATH, 'r', encoding='utf-8') as f:
            self.s2c_table = json.load(f)
    
    def calculate_most_likely_sentence(self, spell: str) -> str:
        """
        Calculate the most likely sentence given the spell
        """
        spell = list(map(lambda item : item.lower(), spell.split(' ')))
        pypinyin_spell = list(map(lambda item : item.replace('lue', 'lve').replace('nue', 'nve'), spell))
        # Initialize the probability list and character chain list
        # with the format of [{c_s_str: {c_s_str_next: prob, ...}, ...}, {c_s_str: {c_s_str_next: prob, ...}, ...}, ...]
        # prob_list[i][c_s_str][c_s_str_next] means the probability of the most likely sentence ending with c_s_str_next
        prob_list = [{} for i in range(len(spell) - 1)]
        # with the format of [{c_s_str: {c_s_str_next: c_s_str_prev, ...}, ...}, {c_s_str: {c_s_str_next: c_s_str_prev, ...}, ...}, ...]
        character_chain_list = [{} for i in range(len(spell) - 1)]
        # Initialize first two characters
        for character in self.s2c_table[spell[0]]:
            c_s_str = character + ' ' + pypinyin_spell[0]
            if c_s_str in self.unit_occurance:
                prob_list[0][c_s_str] = {}
                character_chain_list[0][c_s_str] = {}
                for character_next in self.s2c_table[spell[1]]:
                    c_s_str_next = character_next + ' ' + pypinyin_spell[1]
                    if c_s_str_next in self.unit_occurance:
                        if (c_s_str in self.tuple_occurance) and (c_s_str_next in self.tuple_occurance[c_s_str]):
                            prob = math.log (self.alpha * self.tuple_occurance[c_s_str][c_s_str_next] / self.unit_occurance[c_s_str] \
                                                 + (1 - self.alpha) * self.unit_occurance[c_s_str_next] / self.CHARACTER_SUM)
                        else:
                            prob = math.log((1 - self.alpha) * self.unit_occurance[c_s_str_next] / self.CHARACTER_SUM)
                        prob_list[0][c_s_str][c_s_str_next] = prob
                        character_chain_list[0][c_s_str][c_s_str_next] = ''
        # Calculate the probability of each character
        for i in range(len(spell) - 2):
            for character in self.s2c_table[spell[i + 2]]:
                c_s_str_next = character + ' ' + pypinyin_spell[i + 2]
                if c_s_str_next in self.unit_occurance:
                    for c_s_str_prev in prob_list[i]:
                        for c_s_str in prob_list[i][c_s_str_prev]:
                            if (c_s_str_prev in self.triple_occurance) and (c_s_str in self.triple_occurance[c_s_str_prev]) and (c_s_str_next in self.triple_occurance[c_s_str_prev][c_s_str]):
                                prob = math.log (self.beta * self.triple_occurance[c_s_str_prev][c_s_str][c_s_str_next] / self.tuple_occurance[c_s_str_prev][c_s_str] \
                                                     + (1 - self.beta) * self.alpha * self.tuple_occurance[c_s_str_prev][c_s_str] / self.unit_occurance[c_s_str_prev] \
                                                     + (1 - self.beta) * (1 - self.alpha) * self.unit_occurance[c_s_str] / self.CHARACTER_SUM)
                            elif (c_s_str in self.tuple_occurance) and (c_s_str_next in self.tuple_occurance[c_s_str]):
                                prob = math.log ((1 - self.beta) * self.alpha * self.tuple_occurance[c_s_str][c_s_str_next] / self.unit_occurance[c_s_str] \
                                                     + (1 - self.beta) * (1 - self.alpha) * self.unit_occurance[c_s_str_next] / self.CHARACTER_SUM)
                            else:
                                prob = math.log ((1 - self.beta) * (1 - self.alpha) * self.unit_occurance[c_s_str_next] / self.CHARACTER_SUM)
                            if c_s_str not in prob_list[i + 1]:
                                prob_list[i + 1][c_s_str] = {}
                                character_chain_list[i + 1][c_s_str] = {}
                            if (c_s_str_next not in prob_list[i + 1][c_s_str]) or (prob_list[i + 1][c_s_str][c_s_str_next] < prob + prob_list[i][c_s_str_prev][c_s_str]):
                                prob_list[i + 1][c_s_str][c_s_str_next] = prob + prob_list[i][c_s_str_prev][c_s_str]
                                character_chain_list[i + 1][c_s_str][c_s_str_next] = c_s_str_prev
        # Find the most likely sentence
        max_prob = -float('inf')
        max_prob_c_s_str = ''
        max_prob_c_s_str_prev = ''
        for c_s_str in prob_list[-1]:
            for c_s_str_next in prob_list[-1][c_s_str]:
                if prob_list[-1][c_s_str][c_s_str_next] > max_prob:
                    max_prob = prob_list[-1][c_s_str][c_s_str_next]
                    max_prob_c_s_str = c_s_str_next
                    max_prob_c_s_str_prev = c_s_str
        # Backtrace to find the most likely sentence
        ret_sentence = max_prob_c_s_str[0]
        for i in range(len(spell) - 2, -1, -1):
            ret_sentence = max_prob_c_s_str_prev[0] + ret_sentence
            tmp = max_prob_c_s_str
            max_prob_c_s_str = max_prob_c_s_str_prev
            max_prob_c_s_str_prev = character_chain_list[i][max_prob_c_s_str_prev][tmp]
        return ret_sentence
            

