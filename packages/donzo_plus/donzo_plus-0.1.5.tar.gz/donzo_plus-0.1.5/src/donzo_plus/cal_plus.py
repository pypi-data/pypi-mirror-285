import sys

def plus(a,b):
    print(a+b)

def main():

    a = int(sys.argv[1])
    b = int(sys.argv[2])

    plus(a,b)
if __name__ == "__main__":
    main()
