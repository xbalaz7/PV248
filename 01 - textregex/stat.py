import sys
import re


def composer(file, dict):    
    regex = re.compile(r"Composer: (.|\s)*\S(.|\s)*")
    
    for line in file:
        match = regex.match(line)
        if match is not None:            
           composerRemoved = re.sub(r"Composer: ", '', line)
           yearsRemoved = re.sub(r"\([^a-zA-Z]*\)", '', composerRemoved) 
           strippedLine = re.sub(r"\s*$", '', yearsRemoved)   
           splitLine = re.split(r";\s", strippedLine)
           for composer in splitLine:  
               if composer in dict:  
                  dict[composer] += 1    
               else:
                  dict[composer] = 1

    for key, value in dict.items():
        print(str(key) + ': ' + str(value))


def century(file, dict):    
    regex = re.compile(r"Composition Year: (.|\s)*\S(.|\s)*")
        
    for line in file:
        match = regex.match(line)
        if match is not None:
           compYearRemoved = re.sub(r"Composition Year: ", '', line)           
           strippedLine = re.sub(r"\s*$", '', compYearRemoved)           
           year = re.search(r"\d{4}", strippedLine)
           century = 0
           if year is None:
              centuryFound = re.search(r"([0-9]{2}th)", strippedLine)
              century = re.sub(r"th", '', centuryFound.group())  
           else:              
              century = int((int(year.group()) / 100) + 1)
              
           century = str(century)
           
           if century in dict:  
              dict[century] += 1    
           else:
              dict[century] = 1

    for key, value in sorted(dict.items()):
        if int(key) == 21:
           print(key + 'st century: ' + str(value))
        else:           
           print(str(key) + 'th century: ' + str(value))


def main(argv):
    file = open(sys.argv[1], 'r', encoding='utf_8')
    dict = {}
    
    if sys.argv[2] == 'composer':
       composer(file, dict)
    if sys.argv[2] == 'century':
       century(file, dict)
  
  
if __name__== "__main__":
   main(sys.argv[1:]) 



