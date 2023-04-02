# AI导论第一次作业——拼音输入法
## 项目代码介绍
### 项目仓库地址
[wulei20/IAI2023/pinyin_input_method](https://github.com/wulei20/IAI2023/tree/master/pinyin_input_method)
### 项目结构
```bash
├── README.md
├── img
├── data
│   ├── input.txt
│   ├── output.txt
│   └── std_output.txt
├── src
│   ├── main.py
│   ├── model.py
│   ├── data_preprocessor.py
│   ├── constant.py
│   ├── batch.py
│   └── requirements.txt
├── train_data
│   ├── character
│   │   ├── 拼音汉字表.txt
│   │   └── 一二级汉字表.txt
│   ├── pretrain
│   │   ├── sina_news_output    # 中间文件，占用空间较大，未上传
│   │   ├── c2s_table.json
│   │   ├── s2c_table.json
│   │   ├── triple_occurance.json
│   │   ├── tuple_occurance.json
│   │   └── unit_occurance.json
│   ├── sina_news_gbk           # 语料库文件，占用空间较大，未上传
│   └── SMP2020                 # 语料库文件，占用空间较大，未上传
├── result.txt
└── report.md
```
### 项目文件介绍
#### data
存放测试数据，包括输入数据、输出数据、标准输出数据。
#### src
存放源代码，包括模型代码、数据预处理代码、常量定义代码、批处理代码。
#### train_data
存放训练数据，包括训练数据、预训练数据、字典、字与词的频率统计数据。
#### result.txt
通过运行`python src/batch.py > result.txt`生成的结果文件，存放了对不同$\alpha、\beta$的测试结果。
#### report.md
实验报告，包括实验结果、实验分析、实验总结。

## 项目运行方式
### 数据预处理
#### 生成预训练数据
```bash
python src/data_preprocessor.py
```
#### 进行单次测试
```bash
python src/main.py [--model MODEL] [--alpha ALPHA] [--beta BETA] [--input INPUT] [--output OUTPUT] [--notcheck NOTCHECK] [--std_output STD_OUTPUT]
```
命令行参数：
```bash
-m, --model: 模型选择，输入2或3选择二元或三元模型
-a, --alpha: 二元组权重
-b, --beta: 三元组权重
-i, --input: 输入文件路径
-o, --output: 输出文件路径
-n, --notcheck: 是否对比输出文件与标准输出文件，默认进行对比，设置为true时不会对比
-s, --std_output: 用于对比的标准输出文件路径
```
### python环境配置
#### python环境
python版本：3.10.10
#### 依赖生成方式(基于已有代码)
```
cd src
python -m pipreqs.pipreqs ./
```
windows平台需要注意将所有文件通过gbk方式保存后才可使用该指令。
#### 依赖安装方式
```
cd src
pip install -r requirements.txt
```