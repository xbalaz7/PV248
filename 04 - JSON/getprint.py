import sys
import sqlite3
import json

def get_composers(connection, input_print_id):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM person JOIN score_author ON person.id = score_author.composer \
                    JOIN edition ON edition.score = score_author.score \
                    JOIN print ON edition.id = print.edition WHERE print.id = ?", (input_print_id,))
    return cursor.fetchall()

def json_composers(composers):
    comp_list = []
    for composer in composers:
        author = {"name" : composer[3]}
        if composer[1] is not None:
           author["born"] = composer[1]
        if composer[2] is not None:
           author["died"] = composer[2]
        comp_list.append(author)
  
    print(json.dumps(comp_list, indent=4, ensure_ascii=False))

def main(argv):
    input_print_id = sys.argv[1]
    connection = sqlite3.connect( "scorelib.dat" )

    composers = get_composers(connection,input_print_id)
    json_composers(composers)

if __name__ == "__main__":
    main(sys.argv[1:])
