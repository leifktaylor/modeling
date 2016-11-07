import sys


def evaluate(string):
    print(eval(string))


if __name__ == '__main__':
    math_expression = ' '.join(sys.argv[1:])
    evaluate(math_expression)

