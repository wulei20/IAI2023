import os

MODEL_NAME_LIST = ["CNN", "RNN", "MLP"]
LEARNING_RATE_LIST = [0.1, 0.01, 0.001, 0.0001, 0.00001]
DROPOUT_LIST = [0.1, 0.2, 0.3, 0.4, 0.5]
def test_modules():
    for model_name in MODEL_NAME_LIST:
        print(f"Testing {model_name}")
        os.system(f"python src/main.py --model {model_name}")

def test_learning_rate():
    for learning_rate in LEARNING_RATE_LIST:
        print(f"Testing learning rate {learning_rate}")
        os.system(f"python src/main.py --learning_rate {learning_rate}")

def test_dropout():
    for dropout in DROPOUT_LIST:
        print(f"Testing dropout {dropout}")
        os.system(f"python src/main.py --dropout {dropout}")

if __name__ == "__main__":
    test_modules()
    test_learning_rate()
    test_dropout()