import sqlite3
import scorelib
import sys

   

def initialize_database(file):
    connection = sqlite3.connect(file)
    cursor = connection.cursor()    
    cursor.execute("create table score ( id integer primary key not null, \
                                         name varchar, \
                                         genre varchar, \
                                         key varchar, \
                                         incipit varchar, \
                                         year integer );")
    cursor.execute("create table voice ( id integer primary key not null, \
                                         number integer not null, \
                                         score integer references score( id ) not null, \
                                         range varchar, \
                                         name varchar )")   
    cursor.execute("create table edition ( id integer primary key not null, \
                                           score integer references score( id ) not null, \
                                           name varchar, \
                                           year integer )")
    cursor.execute("create table person ( id integer primary key not null, \
                                          born integer, \
                                          died integer, \
                                          name varchar not null )")
    cursor.execute("create table print ( id integer primary key not null, \
                                         partiture char(1) default 'N' not null, \
                                         edition integer references edition( id ) )")
    cursor.execute("create table score_author( id integer primary key not null, \
                                               score integer references score( id ) not null, \
                                               composer integer references person( id ) not null )")
    cursor.execute("create table edition_author( id integer primary key not null, \
                                                 edition integer references edition( id ) not null, \
                                                 editor integer references person( id ) not null )")
    connection.commit()
    return connection


def find_author_in_database(author, connection):
    cursor = connection.cursor()    
    cursor.execute("SELECT * FROM person WHERE name = ?", (author.name,))
    return cursor.fetchone()

def find_score_in_database(composition, connection):    
    cursor = connection.cursor()    
    cursor.execute("SELECT * FROM score WHERE (name = ? OR name IS NULL) AND (genre = ? OR genre IS NULL) AND \
                   (key = ? or key IS NULL) AND (incipit = ? OR incipit IS NULL) AND (year = ? OR year is NULL)",
                   (composition.name, composition.genre, composition.key, composition.incipit, composition.year,))
    scores = cursor.fetchall()

    # Finds the correct score based on the authors and voices
    for score in scores: 
        if score[1] is None:
           if composition.name:
              continue
        elif score[2] is None:
           if composition.genre:
              continue
        elif score[3] is None:
           if composition.key:
              continue
        elif score[4] is None:
           if composition.incipit:
              continue
        elif score[5] is None:
           if composition.year:
              continue

        cursor.execute("SELECT * FROM person WHERE id IN (SELECT composer FROM score_author WHERE score = ?)", (score[0],))       
        authors = cursor.fetchall()  
        
        found = True
        for author in authors:            
            names = [composition_author.name for composition_author in composition.authors]            
            if author[3] not in names:
               found = False
    
        cursor.execute("SELECT * FROM voice WHERE score = ?", (score[0],))       
        voices = cursor.fetchall()
        
        if (len(voices) == len(composition.voices)) and found:             
           counter = 1
           for comp_voice in composition.voices:
               for found_voice in voices:
                   if found_voice[1] == counter:                      
                      if comp_voice.name != found_voice[4] or comp_voice.range != found_voice[3]:                         
                         found = False                        
                         break
               counter += 1              
           
        elif (len(voices) != len(composition.voices)) and found:
           found = False

        if found:            
           return score
        

def find_edition_in_database(edition, score_id, connection):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM edition WHERE (name = ? OR name IS NULL) AND score = ?", (edition.name, score_id,))
    editions = cursor.fetchall()    
    
    # Finds the correct edition based on the authors
    for db_edition in editions:    
        if db_edition[2] is None:
           if edition.name:
              continue
    
        cursor.execute("SELECT * FROM person WHERE id IN (SELECT editor FROM edition_author WHERE edition = ?)", (db_edition[0],))       
        authors = cursor.fetchall()  
        
        found = True
        for author in authors:            
            names = [edition_author.name for edition_author in edition.authors]            
            if author[3] not in names:
               found = False

        if found:            
           return db_edition


def get_people(prints):
    people = []
    for item in prints:
        people.extend(item.composition().authors)
        people.extend(item.edition.authors)
    return people


def insert_people_to_database(people, connection):
    for person in people:        
        existing_person = find_author_in_database(person, connection)

        cursor = connection.cursor()    
        if existing_person is None:
           cursor.execute("INSERT INTO person(born, died, name) VALUES (?,?,?)", (person.born, person.died, person.name))
        else:            
            if existing_person[1] is None:
                cursor.execute("UPDATE person SET born = (?) WHERE id = (?)", (person.born, existing_person[0]))
            if existing_person[2] is None:
                cursor.execute("UPDATE person SET died = (?) WHERE id = (?)", (person.died, existing_person[0]))
        

def get_compostions(prints):
    compositions = []
    for item in prints:
        compositions.append(item.composition())
    return compositions


def insert_compositions_to_database(compositions, connection):
    for composition in compositions:        
        if find_score_in_database(composition, connection) is None:
           cursor = connection.cursor()    
           cursor.execute("INSERT INTO score(name, genre, key, incipit, year) VALUES (?, ?, ?, ?, ?)",
                          (composition.name, composition.genre, composition.key, composition.incipit, composition.year,))
           
           score_id = cursor.lastrowid           
           for author in composition.authors:
               author_id = find_author_in_database(author, connection)[0]
               cursor.execute("INSERT INTO score_author(score, composer) VALUES (?, ?)", (score_id, author_id)) 

           number = 1
           for voice in composition.voices:               
               cursor.execute("INSERT INTO voice(number, score, range, name) VALUES (?, ?, ?, ?)", 
                              (number, score_id, voice.range, voice.name)) 
               number += 1

def get_editions(prints):
    editions = []
    for item in prints:
        editions.append(item.edition)
    return editions

def insert_editions_to_database(editions, connection):
    for edition in editions:
        score = find_score_in_database(edition.composition, connection)
        if find_edition_in_database(edition, score[0], connection) is None:
           cursor = connection.cursor()    
           score_id = find_score_in_database(edition.composition, connection)[0]
           cursor.execute("INSERT INTO edition(score, name, year) VALUES (?, ?, ?)", (score_id, edition.name, None))

           edition_id = cursor.lastrowid           
           for author in edition.authors:
               author_id = find_author_in_database(author, connection)[0]
               cursor.execute("INSERT INTO edition_author(edition, editor) VALUES (?, ?)", (edition_id, author_id))  

def insert_prints_to_database(prints, connection):
    for item in prints:
        cursor = connection.cursor() 
        score = find_score_in_database(item.composition(), connection)
        edition_id = find_edition_in_database(item.edition, score[0], connection)[0]

        partiture = "NO"
        if item.partiture is True:
           partiture = "YES"

        cursor.execute("INSERT INTO print(id, partiture, edition) VALUES (?, ?, ?)", (item.print_id, partiture, edition_id))

def main(argv):   
    prints = scorelib.load(sys.argv[1])
    connection = initialize_database(sys.argv[2])
    
    people = get_people(prints)   
    insert_people_to_database(people, connection)

    compositions = get_compostions(prints)
    insert_compositions_to_database(compositions, connection)

    editions = get_editions(prints)
    insert_editions_to_database(editions, connection)
    
    insert_prints_to_database(prints, connection)
    
    connection.commit()
    

if __name__ == "__main__":
    main(sys.argv[1:])
