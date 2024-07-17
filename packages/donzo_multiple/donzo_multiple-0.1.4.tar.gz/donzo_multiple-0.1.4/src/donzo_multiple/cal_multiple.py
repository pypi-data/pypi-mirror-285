import sys

def multiple(a,b):
    print(a*b)

def main():

    a = int(sys.argv[1])
    b = int(sys.argv[2])

    multiple(a,b)
if __name__ == "__main__":
    main()          
