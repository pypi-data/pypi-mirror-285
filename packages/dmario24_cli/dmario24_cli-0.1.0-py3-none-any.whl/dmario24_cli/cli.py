import sys
from dmario24_cli.utils import plus

def main():
    a = int(sys.argv[1])
    b = int(sys.argv[2])
    print(plus(a, b))

if __name__ == "__main__":
    main()
