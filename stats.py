import sys
import re

file = open('scorelib.txt', 'r')
regex = re.compile(r"Composer: (.|\s)*\S(.|\s)*")

dict = {}
for line in file:
    match = regex.match(line)
    if match is not None:
       strippedLine = line.strip()
       print strippedLine
 



