import sys
import sqlite3
import json

def people_and_dates_to_list(people):
    final_people = []
    for person in people:
        author = {"name" : person[3]}
        if person[1] is not None:
           author["born"] = person[1]
        if person[2] is not None:
           author["died"] = person[2]
        final_people.append(author)
    return final_people

def get_editors(connection, edition_id):
    cursor = connection.cursor() 
    cursor.execute("SELECT * FROM person JOIN edition_author ON person.id = edition_author.editor WHERE edition_author.edition = ?", (edition_id,))
    editors = cursor.fetchall()

    return people_and_dates_to_list(editors)

def get_composers(connection, score_id):
    cursor = connection.cursor() 
    cursor.execute("SELECT * FROM person JOIN score_author ON person.id = score_author.composer WHERE score_author.score = ?", (score_id,))
    composers = cursor.fetchall()
    
    return people_and_dates_to_list(composers)

def get_voices(connection, score_id):
    cursor = connection.cursor() 
    cursor.execute("SELECT * FROM voice WHERE score = ?", (score_id,))       
    voices = cursor.fetchall()

    final_voices = {}
    for voice in voices:          
        final_voice = {}
        if voice[4] is not None:
           final_voice["name"] = voice[4]
        if voice[3] is not None:
           final_voice["range"] = voice[3]
        final_voices[str(voice[1])] = final_voice

    return final_voices

def final_print(print_item, edition, editors, score, composers, voices):
    final_print = {"Print Number" : print_item[0]}
    if composers:
       final_print["Composer"] = composers 
    if score[1] is not None:
       final_print["Title"] = score[1]
    if score[2] is not None:
       final_print["Genre"] = score[2]
    if score[3] is not None:
       final_print["Key"] = score[3]
    if score[5] is not None:
       final_print["Composition Year"] = score[5]
    if edition[1] is not None:
       final_print["Edition"] = edition[1]
    if editors:
       final_print["Editor"] = editors
    if voices:
       final_print["Voices"] = voices
    if print_item[1] is not None:
       final_print["Partiture"] = True if print_item[1] == "Y" else False
    if score[4] is not None:
       final_print["Incipit"] = score[4]

    return final_print

def search_composers(connection, input):
    cursor =connection.cursor()
    cursor.execute("SELECT * FROM person WHERE name LIKE ? AND person.id IN (SELECT id from score_author)", ('%' + input + '%',))
    composers = cursor.fetchall()
    
    composer_prints = []
    for composer in composers:        
        cursor.execute("SELECT print.id, print.partiture FROM print JOIN edition ON print.edition = edition.id JOIN score ON edition.score = score.id \
                        JOIN score_author ON score.id = score_author.score WHERE score_author.composer = ?", (composer[0],))
        prints = cursor.fetchall()

        full_prints = []
        for print_item in prints:            
            full_print = {"Print Number" : print_item[0]}
            cursor.execute("SELECT edition.id, edition.name FROM edition JOIN print ON edition.id = print.edition WHERE print.id = ?", (print_item[0],))
            edition = cursor.fetchone()            
            editors = get_editors(connection, edition[0])

            cursor.execute("SELECT * FROM score WHERE score.id IN (SELECT score FROM edition WHERE edition.id = ?)", (edition[0],))
            score = cursor.fetchone()                        
            score_composers = get_composers(connection, score[0]) 

            voices = get_voices(connection, score[0])
            finished = final_print(print_item, edition, editors, score, score_composers, voices)
            full_prints.append(finished)

        composer_prints.append({composer[3] : full_prints})

    print(json.dumps(composer_prints, indent=4, ensure_ascii=False))

def main(argv):
    input = sys.argv[1]
    connection = sqlite3.connect( "scorelib.dat" )

    search_composers(connection, input)

if __name__ == "__main__":
    main(sys.argv[1:])