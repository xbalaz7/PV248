import sys 
import scorelib

def main(argv):    
    prints = scorelib.load(sys.argv[1])
    
    for item in prints:
        item.format()         


if __name__ == "__main__":
   main(sys.argv[1:])
