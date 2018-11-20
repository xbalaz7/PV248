import sys
import json
import pandas
import numpy
from datetime import datetime
from datetime import timedelta

# Unique dates
def get_dates(columns):
    if "student" in columns:
       columns.remove("student")    
    dates = []
    
    for column in columns:
        column_split = column.split("/")
        column_stripped = column_split[0].strip()      
        date = datetime.strptime(column_stripped, "%Y-%m-%d").date()

        if date not in dates:
           dates.append(date)    
  
    return dates

# Points for each date
def get_points(dates, specific_row):     
    data_frame = specific_row.to_frame()
    data_frame = data_frame.T
    
    date_columns = list(data_frame.head(0))
    
    points = []
    exercise = 0
    for date in dates:
        for date_column in date_columns:            
            if str(date) in date_column:
               exercise += float(data_frame[date_columns[date_columns.index(date_column)]])                
        points.append(exercise)         
    
    return points

# Points for each exercise
def get_points_per_exercise(specific_row):
    data_frame = specific_row.to_frame()
    data_frame = data_frame.T
    
    columns = list(data_frame.head(0))
    points = {}
    
    for column in columns:                    
        exercise = (column.split("/")[1]).strip()
        points[exercise] = float(data_frame[columns[columns.index(column)]])   
        columns.remove(column)
        
        for duplicate in columns:
            tmp_dup = (duplicate.split("/")[1]).strip()
            if exercise == tmp_dup:
               points[exercise] += float(data_frame[columns[columns.index(duplicate)]])   
               columns.remove(duplicate)
               columns.insert(0, duplicate)
        columns.insert(0, column)
    return pandas.Series(list(points.values()),index=pandas.MultiIndex.from_tuples(points.keys())) 


def calculate_student(input, id, specific_row): 
    dict = {}
    
    columns = list(input.head(0))     
    students = list(input[columns[0]])
    
    if specific_row is None:
       specific_student = students.index(id)
       specific_row =  input.loc[specific_student]    
       specific_row.pop("student")    
    
    points_per_exercise = get_points_per_exercise(specific_row)
    dict["mean"] = points_per_exercise.mean()    
    dict["median"] = points_per_exercise.median()
    dict["total"] = sum(points_per_exercise)
    dict["passed"] = len([result for result in points_per_exercise if result > 0])
    
    dates = get_dates(columns)
    points = numpy.array(get_points(dates, specific_row))
    
    start_date = datetime.strptime('2018-9-17', '%Y-%m-%d').date()
    dates_since = numpy.array([date - start_date for date in dates])
    days_since = numpy.array([[date.days] for date in dates_since])
    
    slope = numpy.linalg.lstsq(sorted(days_since), sorted(points), rcond=None)[0]    

    dict["regression slope"] = slope[0]
    sixteen_points = "inf" if slope[0] == 0.0 else start_date + timedelta(days=int(16 / slope))       
    dict["date 16"] = sixteen_points
    twenty_points = "inf" if slope[0] == 0.0 else start_date + timedelta(days=int(20 / slope))
    dict["date 20"] = twenty_points
       
    print(json.dumps(dict, ensure_ascii=False, indent=4, default=str))

def main(argv):        
    mode = sys.argv[2]
   
    if mode == "average":
       input = pandas.read_csv(sys.argv[1], index_col="student", delimiter=",", skipinitialspace=True)
       #average_points_per_exercise(input)
       specific_row = input.mean(axis=0)
       calculate_student(input, id = 0, specific_row = specific_row)
    else:
       input = pandas.read_csv(sys.argv[1], delimiter=",", skipinitialspace=True)
       calculate_student(input, id = int(mode), specific_row = None)   

if __name__ == "__main__":
    main(sys.argv[1:])
