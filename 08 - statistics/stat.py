import sys
import json
import pandas

def calculate_statistics(results):
    dict = {}
    dict["mean"] = results.mean()
    dict["median"] = results.median()
    dict["first"] = results.quantile(0.25)
    dict["last"] = results.quantile(0.75)
    dict["passed"] = len([result for result in results if result > 0])
    return dict

def find_duplicate_columns(columns, column):   
    return_columns = []
    for clm in columns:
        if column in clm:           
           return_columns.append(clm)
    return return_columns

def solve_dates_or_exercises(input, split):
    columns = list(input.head(0))    
    solutions = {}
    solved = []

    for column in columns:
        if len(columns) == len(solved):
           break
        if column in solved:           
           continue
        
        column_split = column.split("/")
        column_stripped = column_split[split].strip()
        results = input[columns[columns.index(column)]]    
        results = results.astype("float")
        
        if column != columns[-1]:                
           columns.remove(column)           
           identical_columns = find_duplicate_columns(columns, column_stripped)          
 
           for identical_column in identical_columns:
              identical_column_split = identical_column.split("/")
              identical_column_stripped = identical_column_split[split].strip()
              
              if column_stripped == identical_column_stripped:
                 results_next = input[columns[columns.index(identical_column)]]
                 results_next = results_next.astype("float")
                 results = results.combine(results_next, lambda first, second: first + second)
                 solved.append(column)
                 solved.append(identical_column)
           columns.insert(0, column)      
   
        solution = calculate_statistics(results)
        solutions[column_stripped] = solution       
         
    print(json.dumps(solutions, ensure_ascii=False, indent=4))


def solve_deadline(input):
    columns = list(input.head(0))    
    solutions = {}
    solved = []

    for column in columns:      
        results = input[columns[columns.index(column)]]                    
        column_stripped = column.strip()
   
        solution = calculate_statistics(results)
        solutions[column_stripped] = solution       
         
    print(json.dumps(solutions, ensure_ascii=False, indent=4))



def main(argv):    
    input = pandas.read_csv(sys.argv[1], index_col="student", delimiter=",", skipinitialspace=True)
    mode = sys.argv[2]
   
    if mode == "dates":
       solve_dates_or_exercises(input, split=0)
    elif mode == "deadlines":
       solve_deadline(input)
    elif mode == "exercises":
       solve_dates_or_exercises(input, split=1)
    else:
       print("Unknown mode")

if __name__ == "__main__":
    main(sys.argv[1:])
