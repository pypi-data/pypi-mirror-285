import sys

def divide(a,b):
    print(a/b)

def main():

    a = int(sys.argv[1])
    b = int(sys.argv[2])

    divide(a,b)
if __name__ == "__main__":
    main()

