import sys
import re
import operator

def format_people(people):
    people_string = ""    

    for person in people:
        people_string += person.name
        
        if person.born or person.died:
           people_string += "("
           if person.born: 
              people_string += str(person.born)
           people_string += "--"
           if person.died: 
              people_string += str(person.died)
           people_string += ")"

        if person != people[-1]:
           people_string += "; "

    return people_string

def format_to_string(attribute):
    return_value = ""    

    if attribute is not None:
       return_value = str(attribute)

    return return_value

def format_voices(voices):
    result_string = "Voice 1: "
    counter = 1;

    for voice in voices:
        if voice.range and (voice.name is None):
           result_string += voice.range
        elif voice.name and (voice.range is None):
           result_string += voice.name
        elif voice.name and voice.range:
           result_string += voice.range + "; " + voice.name
        
        if voice != voices[-1]:
           counter += 1
           result_string += ("\nVoice " + str(counter) + ": ")

    return result_string

def format_partiture(partititure):
    return_value = "no"

    if partititure:
       return_value = "yes"
   
    return return_value

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
    def __init__(self, name, incipit, key, genre, year, voices, authors):
        self.name = name
        self.incipit = incipit
        self.key = key
        self.genre = genre
        self.year = year  
        self.voices = voices
        self.authors = authors

class Print:
    def __init__(self, edition, print_id, partiture):
        self.edition = edition
        self.print_id = print_id
        self.partiture = partiture 

    def format(self):
        print("Print Number: " + str(self.print_id))
        print("Composer: " + format_people(self.edition.composition.authors))
        print("Title: " + format_to_string(self.edition.composition.name))
        print("Genre: " + format_to_string(self.edition.composition.genre))
        print("Key: " + format_to_string(self.edition.composition.key))
        print("Composition Year: " + format_to_string(self.edition.composition.year))
        print("Edition: " + format_to_string(self.edition.name))
        print("Editor: " + format_people(self.edition.authors))
        print(format_voices(self.edition.composition.voices))
        print("Partiture: " + format_partiture(self.partiture))
        print("Incipit: " + format_to_string(self.edition.composition.incipit))
        print("")

    def composition(self):
        return self.edition.composition


def load_people(line):
    line_stripped = line.strip() 
    split = re.split(r";\s", line_stripped)     
    people = []    

    if split[0] == '':
       return people
    
    for person in split:  
        born = None
        died = None

        date_birth = re.search(r"\*[0-9]{4}", person)
        if date_birth:
           born = int(date_birth.group(0)[1:5])
           
        date_death = re.search(r"\+[0-9]{4}", person)
        if date_death:
           died = int(date_death.group(0)[1:5])
           
        dates = re.search(r"(\([0-9]{4}--[0-9]{4}\))|(\([0-9]{4}-[0-9]{4}\))", person)        
        if dates:          
           dates_split = re.split(r"--", dates.group(0))
           if len(dates_split) == 2:              
              if dates_split[0]: born = int(dates_split[0][1:5])
              if dates_split[1]: died = int(dates_split[1][0:4])              
           elif len(re.split(r"-", dates.group(0))) == 2:                  
              dates_split = re.split(r"-", dates.group(0))
              if dates_split[0]: born = int(dates_split[0][2:6])
              if dates_split[1]: died = int(dates_split[1][0:4])                      
        
        parentheses_removed = re.sub(r"\([^a-zA-Z]*\)", '', person) 
        person = Person(str(parentheses_removed), born, died)
        people.append(person)       
    
    return people

def load_partiture(line):
    partiture = False
    partiture_removed = re.sub(r"Partiture: ", '', line)  
    partiture_stripped = partiture_removed.strip()

    if "yes" in str(partiture_stripped): 
       partiture = True
   
    return partiture
    
def load_composition_year(line):
    composition_year = None
    composition_year_removed = re.sub(r"Composition Year: ", '', line)  
    composition_year_stripped = composition_year_removed.strip()
    
    year = re.search(r"\d{4}", composition_year_stripped)
    if year:
       composition_year = int(year.group(0))
    
    return composition_year

def load_string(line):
    string = None     
    line_stripped = line.strip()
    
    if line_stripped != '':
       string = line_stripped   
    
    return string

def load_voice(line): 
    name = None
    range_attribute = None

    voice_removed = re.sub(r"Voice (\S)*:", '', line)     
    voice_stripped = voice_removed.strip() 
    
    match = re.match(r"((\S)*--(\S)*)(,|;)", voice_stripped)
    if match:
       range_string = match.group(0)
       name_string = re.sub(r"((\S)*--(\S)*)", '', voice_stripped)
       name = name_string.strip()
       range_attribute = re.sub(r";|,", '', range_string)  
    elif voice_stripped != '':
       name = voice_stripped
        
    voice = Voice(name, range_attribute)
    return voice

def load_editors(line):    
    line_stripped = line.strip()
    editors = line_stripped
    
    counter = len(line.split(","))    
    checks = 0  
    
    while checks <= counter:
        editors_check = re.search(r"(.|;)(\S)*, (\S)[^,]*,", editors)        
        if editors_check:
           editors_check_split = editors_check.group(0).split(",")
           semicolon = editors_check_split[0] + editors_check_split[1] + ";"           
           editors = editors.replace(editors_check.group(0), semicolon)
           checks += 1
           editors_check = None    
        else:
           break

    checks = 0
    while checks <= counter:
        editors_check = re.search(r"(.|;)(\S)[^,]* (\S)[^,]*, (\S)[^,]* (\S)[^,]*", editors)
        if editors_check:           
           semicolon = re.sub(r",", ';', editors_check.group(0))
           editors = editors.replace(editors_check.group(0), semicolon)
           checks += 1
           editors_check = None                
        else:
           break
    
    return load_people(editors)


def load(filename):  
    scores = open(filename, 'r', encoding='utf_8')
    prints = []    

    print_id = None
    partiture = False

    composition_authors = []
    composition_name = None
    genre = None
    key = None
    composition_year = None
    voices = []
    incipit = None    
        
    edition_name = None
    edition_authors = None
    
    regex = re.compile(r"Print Number: (.|\s)*\S(.|\s)*")
    for line in scores:       
        if line.startswith("Print Number:"):                      
           print_removed = re.sub(r"Print Number:", '', line)  
           print_stripped = print_removed.strip()
           print_id = int(print_stripped)           
        elif line.startswith("Composer:"):
           composer_removed = re.sub(r"Composer:", '', line)                          
           composition_authors = load_people(composer_removed)
        elif line.startswith("Title:"):
           title_removed = re.sub(r"Title:", '', line)
           composition_name = load_string(title_removed)  
        elif line.startswith("Genre:"):
           genre_removed = re.sub(r"Genre:", '', line)
           genre = load_string(genre_removed)           
        elif line.startswith("Key:"):
           key_removed = re.sub(r"Key:", '', line)  
           key = load_string(key_removed)             
        elif line.startswith("Composition Year:"):
           composition_year = load_composition_year(line)
        elif line.startswith("Edition:"):
           edition_removed = re.sub(r"Edition:", '', line)
           edition_name = load_string(edition_removed)             
        elif line.startswith("Editor:"):
           editor_removed = re.sub(r"Editor:", '', line)                                
           edition_authors = load_editors(editor_removed)              
        elif line.startswith("Voice"):   
           voices.append(load_voice(line)) 
        elif line.startswith("Partiture:"):   
           partiture = load_partiture(line)               
        elif line.startswith("Incipit:"):
           incipit_removed = re.sub(r"Incipit:", '', line)
           incipit_split = incipit_removed.split("|")  
           incipit = load_string(incipit_split[0])   
   
           composition = Composition(composition_name, incipit, key, genre, composition_year, voices, composition_authors)
           edition = Edition(composition, edition_authors, edition_name)           
           loaded_print = Print(edition, print_id, partiture)           
           prints.append(loaded_print)
           voices = []       
           
    return sorted(prints, key=operator.attrgetter('print_id'))
           

def main(argv):    
    load(sys.argv[1])

if __name__ == "__main__":
   main(sys.argv[1:])
