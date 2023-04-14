import random
import os.path as op

def flips( board, index, piece, step ):
   # other - opponent's piece
   other = ('X' if piece == 'O' else 'O')
   # is an opponent's piece in first spot that way?
   here = index + step
   if board[here] != other:
      return False
   # how is index mod changing?
   diff = index % 6 - here % 6
   while( here % 6 - ( here + step ) % 6 == diff and 
          here > 0 and here < 36 and 
          board[here] == other ):
      here = here + step
   return( here % 6 - ( here + step ) % 6 == diff and 
           here > 0 and here < 36 and
           board[here] == piece )
   
def isValidMove( b, x, p ): # board, index, piece
   # invalid index
   if x < 0 or x >= 36:
      return False
   # space already occupied
   if b[x] != '-':
      return False 
   # otherwise, check for flipping pieces
   up    = x >= 12   # at least third row down
   down  = x <  24   # at least third row up
   left  = x % 6 > 1 # at least third column
   right = x % 6 < 4 # not past fourth column
   return (          left  and flips(b,x,p,-1)  # left
         or up   and left  and flips(b,x,p,-7)  # up/left
         or up             and flips(b,x,p,-6)  # up
         or up   and right and flips(b,x,p,-5)  # up/right
         or          right and flips(b,x,p, 1)  # right
         or down and right and flips(b,x,p, 7)  #down/right
         or down           and flips(b,x,p, 6)  # down
         or down and left  and flips(b,x,p, 5)) # down/left

class Agent:

    symbol = 'O'
    kb = 'Phase 2/move_knowledgebase.txt'

    def __init__( self ):
        # set the move dictionary
        self.move_dictionary = {}
        # read in the knowledgebase to a dictionary if it exists 
        # (only time that will not occur is the first time running)
        if op.isfile(self.kb):
            with open(self.kb, 'r') as file:
                for line in file:
                    items = line.strip().split(',')
                    key = items[0]
                    value = ','.join(items[1:])
                    self.move_dictionary[key] = value
                file.close()
    

    def startGame( self, piece ):
        # set piece to be played with
        self.symbol = piece
    
    def getMove( self, board ):
        # set random valid move to start with
        move = random.randint(0,36)
        while not isValidMove(board, move ,self.symbol):
            move = ( move + 1 ) % 36

        # check to see if the dictionary contains probabilities for moves
        value = self.move_dictionary.get(board)
        # if it does exist, then we get the move based on the probabilities
        if value != None:
            line = value.strip().split(',')
            elements = [int(line[i]) for i in range(0, len(line), 2)]
            probabilities = [float(line[i+1]) for i in range(0, len(line), 2)]
            move = random.choices(elements, probabilities)
        # if it doesn't, then we keep the default random move
        # and add the board state to the dictionary
        else:
            # find the number of valid moves first
            count = 0
            for spot in board:
                if isValidMove(board, spot, self.symbol):
                    count += 1
            # calculate the equal probability of choosing those valid moves
            prob = 1.0 / count
            # add those valid moves and their probabilities to the dictionary
            for i in range(len(board)):
                if isValidMove(board, board[i], self.symbol):
                    value += f",{i},{prob}"
            self.move_dictionary[board] = value
        # return the move
        return move
    
    def endGame( self, status, board ):
        return
    
    def stopPlaying( self ):
        with open(self.kb, 'w') as file:
            for key, value in self.move_dictionary.items():
                line = f"{key},{value}\n"
                file.write(line)
            file.close()