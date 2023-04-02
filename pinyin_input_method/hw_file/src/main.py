from model import *
from tqdm import tqdm
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', '-m', default = '2', help = 'The element num of model.', choices = ['2', '3'])
    parser.add_argument('--input', '-i', default = 'data/input.txt', help = 'Input file.')
    parser.add_argument('--output', '-o', default = 'data/test.txt', help = 'Output file.')
    parser.add_argument('--notcheck', '-n', default = False, type = bool)
    parser.add_argument('--std_output', '-a', default = 'data/std_output.txt', help = 'Standard output file.')
    args = parser.parse_args()
    if args.model == '2':
        model = BinaryModel()
    elif args.model == '3':
        model = TrigramModel()
    else:
        raise Exception('Wrong model.')
    input_path = args.input
    output_path = args.output
    std_output_path = args.std_output
    with open(output_path, 'w', encoding = 'utf-8') as output:
        with open(input_path, 'r', encoding = 'utf-8') as input:
            spells_list = input.readlines()
        output_sentence_list = []
        for spells in tqdm(spells_list):
            sentence = model.calculate_most_likely_sentence(spells.strip())
            output.write(sentence + '\n')
            output_sentence_list.append(sentence)
        if not args.notcheck:
            with open(std_output_path, 'r', encoding = 'utf8') as std_output:
                std_sentences = std_output.readlines()
            correct_sentence_num = 0
            character_num = 0
            correct_character_num = 0
            for i in tqdm(range(len(spells_list))):
                if output_sentence_list[i] == std_sentences[i].strip():
                    correct_sentence_num += 1
                for j in range(len(output_sentence_list[i])):
                    if output_sentence_list[i][j] == std_sentences[i][j]:
                        correct_character_num += 1
                character_num += len(output_sentence_list[i])
            print(f'整句正确率：{str(int(correct_sentence_num / len(spells_list) * 10000) / 100)}%')
            print(f'单字正确率：{str(int(correct_character_num / character_num * 10000) / 100)}%')
