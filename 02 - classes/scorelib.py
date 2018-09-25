import sys
import re

class Person:
    def __init__(self, name, born, died):
        self.name = name
        self.born = born
        self.died = died

class Voice:
    def __init__(self, name, range):
        self.name = name
        self.range = range

class Edition:
    def __init__(self, composition, authors, name):
        self.composition = composition
        self.authors = authors
        self.name = name

class Composition:
    def __init__(self, name, incipit, key, genre, year,voices, authors):
        self.name = name
        self.incipit = incipit
        self.key = key
        self.gere = genre
        self.year = year  
        self.voices = voices
        self.authors = authors

class Print:
    def __init__(self, edition, print_id, partiture):
        self.edition = edition
        self.print_id = print_id
        self.partiture = partiture 

def load(scores):
    regex = re.compile(r"Print Number: (.|\s)*\S(.|\s)*")
    for line in scores:
        match = regex.match(line)
        if match is not None:
           
     
       

def main():
    scores = open(sys.argv[1], "r")
    load(scores)

if __name__ == "__main__":
    main()
