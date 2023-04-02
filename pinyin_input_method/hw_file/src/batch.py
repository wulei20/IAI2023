import os

alpha_list = [0.9, 0.95, 0.99, 0.999, 0.9999, 0.99999, 0.999999]
beta_list = [0.9, 0.95, 0.99, 0.999, 0.9999]

def test_model():
    for alpha in alpha_list:
        os.system(f"python src/main.py -m 2 -a {alpha}")
    for alpha in alpha_list:
        for beta in beta_list:
            os.system(f"python src/main.py -m 3 -a {alpha} -b {beta}")

if __name__ == '__main__':
    test_model()
