import sys 
import scorelib

def main(argv):
    scores = open(sys.argv[1], 'r', encoding='utf_8')
    prints = scorelib.load(scores)
    
    for item in prints:
        item.format()         


if __name__ == "__main__":
   main(sys.argv[1:])
