'''
Simulates Conway's Game of Life with periodic boundary conditions. Has options for using Python multiprocessing.
'''
# Imports
import time, os
from timeit import default_timer as defaultTimer
import multiprocessing as mp

# General configuration
# ----------------------------------------------
# Type of output. Options are None and 'Console'.
OUTPUT_TYPE = None
# Character to represent dead cells
DEAD_CHARACTER = '  '
# Character to represent alive cells.
ALIVE_CHARACTER = '[]'
# Number of iterations to run. If GENERATING_DATA is True, this many iterations will be ran every test.
ITERATION_COUNT = 1000
# Time between generations.
TIME_BETWEEN_ITERATIONS = 0

# Data generation configuration
# ----------------------------------------------
# Whether or not to display data or to generate and store it in a file.
GENERATING_DATA = True
# Number of test sets. Each test is ITERATION_COUNT iterations, growing by five rows every test.
NUM_TESTS = 5
# Number of test columns, stays constant throughout testing.
TEST_WIDTH = 10
# Type of processing to use while iterating. Only applicable when GENERATING_DATA is false.
PROCESSING_TYPE = 'Multi'

# Game rules
# ----------------------------------------------
# Number of neighboring cells at which a cell is revived at.
RESURRECTION_THRESHOLD = 3
# Number of neighboring cells where a cell survives to the next iteration.
LIFE_THRESHOLD = 2
# Number of rows and columns.
ROWS, COLS = 5, 10
# The starting cells on the board. These initial five are a basic glider.
START_CELLS = [(0, 2), (1, 2), (2, 2), (2, 1), (1, 0)]


class Grid:
  ''' 
      A class to represent a grid of cells for Conway's Game of Life.
  
    Attributes:
      rows : int
        Number of rows.
        
      cols : int
        Number of columns.
        
      grid : list of integer lists
        The underlying data for the grid itself. Each value is either 1 for alive or 0 for dead.
  '''
  def __init__(self, _rows, _cols, _startOn):
    '''
        Initializes the grid.
        
      Parameters:
        rows : int
          Number of rows.
        
        cols : Int
          Number of columns.
        
        startOn : list of length 2 integer tuples
          The starting cells for the grid.
    '''
    self.rows = _rows
    self.cols = _cols
    self.grid = [[1 if (i, k) in _startOn else 0 for i in range(_cols)]
                 for k in range(_rows)]

  def __str__(self):
    ''' 
        Returns a string representation of the current board state.
    '''

    return '\n'.join(''.join(DEAD_CHARACTER if (self.grid[i][k] == 0) else ALIVE_CHARACTER \
                               for k in range(self.cols)) for i in range(self.rows))

  def neighborChecks(self, point):
    ''' 
        Returns the number of alive cells adjacent to a given point on the board.

      Parameters:
        point : integer tuple
          representation of a point on the board (x, y) 
    '''

    x, y = point
    # Number of neighboring cells
    neighborCount = sum(sum(0 if (i==x and k==y) else self.grid[i%self.rows][k%self.cols] \
                            for i in range(x-1, x+2)) for k in range(y-1, y+2))
    if (neighborCount == RESURRECTION_THRESHOLD and not self.grid[x][y]): # Check if the cell will be alive
      return (point, 1)
    elif (neighborCount != LIFE_THRESHOLD and neighborCount != RESURRECTION_THRESHOLD and self.grid[x][y]):
      return (point, 0) # Check if the cell will be dead

  def iterateMultiCore(self, p):
    '''
        Iterates the board using multiprocessing, returns the time elapsed.

      Parameters:
        p - Multiprocessing pool
          A pool of all available processes.
    '''
    startTime = defaultTimer()
    grid1Ds = [(i // self.cols, i % self.cols)
               for i in range(self.rows * self.cols)] # Create a 1D list from the previous 2D list.

    for point, v in filter(lambda x: x != None, p.map(self.neighborChecks, grid1Ds)):
      self.grid[point[0]][point[1]] = v
      
    deltaTime = defaultTimer() - startTime
    return deltaTime

  def iterateSingleCore(self):
    '''
        Iterates the board using singleprocessing, returns the time elapsed.
    '''

    startTime = defaultTimer()
    grid1Ds = [(i // self.cols, i % self.cols)
               for i in range(self.rows * self.cols)]

    changeList = map(self.neighborChecks, grid1Ds)
    for point, v in filter(lambda x: x != None, changeList):
      self.grid[point[0]][point[1]] = v
      
    deltaTime = defaultTimer() - startTime
    return deltaTime

  def run(self, p, processing='Multi'):
    '''
        Iterates the board ITERATION_COUNT times, returns the average time to iterate.

      Parameters:
        p - Multiprocessing pool
          A pool of all available processes.
          
        processing - String
          The type of processing to utilize in the iteration of the board. Must be either 'Single'
          or 'Multi'.
      '''
      
    timeSum = 0
    for n in range(ITERATION_COUNT):
      if (OUTPUT_TYPE == 'Console'):
        print(str(self))
        
      if (processing == 'Multi'):
        timeSum += self.iterateMultiCore(p)
        
      elif (processing == 'Single'):
        timeSum += self.iterateSingleCore()
        
      else:
        print('Please input a valid processing type.')
        
      time.sleep(TIME_BETWEEN_ITERATIONS)
    return timeSum * 1000 / ITERATION_COUNT # Average time between iterations in ms

if __name__ == '__main__':
  p = mp.Pool()

  if GENERATING_DATA:
    mTimes, sTimes, cellCount = [], [], []
    testRCs = [(TEST_WIDTH, n) for n in range(5, 5 * (NUM_TESTS+1), 5)] # Generate testing data
    for RC in testRCs:
      r, c = RC
      grid = Grid(r, c, START_CELLS)
      mTimes.append(grid.run(p, processing='Multi'))
      sTimes.append(grid.run(p, processing='Single'))
      cellCount.append(r * c)

    p.close()

    f = open(r'./Conways-Periodic-Multithreaded/output.txt', 'w')
    f.write(str(mTimes) + '\n')
    f.write(str(sTimes) + '\n')
    f.write(str(cellCount))
  else:
    g = Grid(ROWS, COLS, START_CELLS)
    g.run(p, processing=PROCESSING_TYPE)
    p.close()