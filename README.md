SudokuSolver
============

Solver for Sudoku puzzles that uses logic based techniques.

## Usage

```
$ python solveSudoku.py --puzzle [puzzleFile]
```

## Input File Format

Place starting numbers into a 9x9 grid separated by spaces for unknown positions.
Example input files can also be found in the inputFiles directory.

```
97 652  8
   7395 6
563481279
62734    
815967423
43921    
 56873   
 9 52    
   19    
```

## Output

```
        Incomplete       
-------------------------
| 9 7 . | 6 5 2 | . . 8 | 
| . . . | 7 3 9 | 5 . 6 | 
| 5 6 3 | 4 8 1 | 2 7 9 | 
-------------------------
| 6 2 7 | 3 4 . | . . . | 
| 8 1 5 | 9 6 7 | 4 2 3 | 
| 4 3 9 | 2 1 . | . . . | 
-------------------------
| . 5 6 | 8 7 3 | . . . | 
| . 9 . | 5 2 . | . . . | 
| . . . | 1 9 . | . . . | 
-------------------------

         Solution        
-------------------------
| 9 7 4 | 6 5 2 | 1 3 8 | 
| 1 8 2 | 7 3 9 | 5 4 6 | 
| 5 6 3 | 4 8 1 | 2 7 9 | 
-------------------------
| 6 2 7 | 3 4 5 | 8 9 1 | 
| 8 1 5 | 9 6 7 | 4 2 3 | 
| 4 3 9 | 2 1 8 | 7 6 5 | 
-------------------------
| 2 5 6 | 8 7 3 | 9 1 4 | 
| 3 9 1 | 5 2 4 | 6 8 7 | 
| 7 4 8 | 1 9 6 | 3 5 2 | 
-------------------------
```

