import sys 
import scorelib
import operator

def main(argv):
    scores = open(sys.argv[1], 'r', encoding='utf_8')
    prints = scorelib.load(scores)
    
    for item in sorted(prints, key=operator.attrgetter('print_id')):
        item.format()         


if __name__ == "__main__":
   main(sys.argv[1:])