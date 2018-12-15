import numpy
import sys
import re

def solve(input):
    left_variables = []
    left_equations = []
    right_constants = []

    for line in input:   
        equation_dict = {}

        strip_line = line.strip()
         
        if strip_line == "":
           break
        
        split_line = strip_line.split(" = ")        
        right_constants.append(int(split_line[1].strip()))
        
        split_equation = split_line[0].split()
        operator = 1        
        for spl in split_equation: 
            spl = spl.strip()                       
           
            if spl == "+":
               operator = 1
               continue
            elif spl == "-":
               operator = -1               
               continue

            variable = re.search("[a-z]", spl)
            coeficient = re.search("[0-9]+", spl)
            
            if coeficient is None:
               equation_dict[variable.group(0)] = 1 * operator
            else:
               equation_dict[variable.group(0)] = int(coeficient.group(0)) * operator
            
            if variable.group(0) not in left_variables:
               left_variables.append(variable.group(0))

        left_equations.append(equation_dict)
        
    coeficient_matrix = []
    for equation in left_equations:        
        matrix_item = len(left_variables)*[0]                  

        for variable in sorted(left_variables):
            matrix_item[left_variables.index(variable)] = equation.get(variable)
        
        for coeficient in matrix_item:
            if coeficient is None: matrix_item[matrix_item.index(coeficient)] = 0

        coeficient_matrix.append(matrix_item)
      

    # Rouche-Capelli theorem
    augmented_matrix = numpy.c_[coeficient_matrix, right_constants] 
    
    coef_matrix_rank = numpy.linalg.matrix_rank(coeficient_matrix)
    augm_matrix_rank = numpy.linalg.matrix_rank(augmented_matrix)
   
  
    if coef_matrix_rank != augm_matrix_rank:
       print("no solution")
    elif coef_matrix_rank < len(left_variables):
       print("solution space dimension: " + str(len(left_variables) - coef_matrix_rank))
    else:
       result = numpy.linalg.solve(coeficient_matrix, right_constants)
       output = 'solution: '
       
       for variable in sorted(left_variables):
           variable_result = result[left_variables.index(variable)]
           output += (variable + " = " + str(variable_result))
           
           if variable != sorted(left_variables)[-1] :
              output += ", "

       print(output)       

def main(argv):
    input = open(sys.argv[1], 'r', encoding='utf_8')    
    solve(input)
    input.close()

if __name__ == "__main__":
    main(sys.argv[1:])
