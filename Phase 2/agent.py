import random
import os.path as op

# decide if pieces are flippable in this direction
def flips( board, index, piece, step ):
   other = ('X' if piece == 'O' else 'O')
   # is an opponent's piece in first spot that way?
   here = index + step
   if here < 0 or here >= 36 or board[here] != other:
      return False
      
   if( abs(step) == 1 ): # moving left or right along row
      while( here // 6 == index // 6 and board[here] == other ):
         here = here + step
      # are we still on the same row and did we find a matching endpiece?
      return( here // 6 == index // 6 and board[here] == piece )
   
   else: # moving up or down (possibly with left/right tilt)
      while( here >= 0 and here < 36 and board[here] == other ):
         here = here + step
      # are we still on the board and did we find a matching endpiece?
      return( here >= 0 and here < 36 and board[here] == piece )
   
# decide if this is a valid move
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
    kb = 'Phase 2/'

    def __init__( self, xORo ):
        # call startGame
        self.startGame(xORo)

    def startGame( self, piece ):
        # set the symbol
        self.symbol = piece

        # declare move and board lists
        self.boards = []
        self.moves = []

        # declare the move dictionary
        self.move_dictionary = {}

        # set the knowledgebase filename
        if self.symbol == 'X':
            self.kb = self.kb
        else:
            self.kb += 'move_knowledgebase.txt'
        
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
    
    def getMove( self, board ):
        # add the board to the boards list
        self.boards.append(board)

        # set random valid move to start with
        move = random.randint(0,36)
        while not isValidMove(board, move, self.symbol):
            move = ( move + 1 ) % 36

        # check to see if the dictionary contains probabilities for moves
        value = self.move_dictionary.get(board)
        # if it does exist, then we get the move based on the probabilities
        if value != None:
            line = value.strip().split(',')
            elements = [int(line[i]) for i in range(0, len(line), 2)]
            probabilities = [float(line[i+1]) for i in range(0, len(line), 2)]
            move = random.choices(elements, probabilities)[0]
        # if it doesn't, then we keep the default random move
        # and add the board state to the dictionary
        else:
            # set the value back to an empty string
            value = ""
            # find the number of valid moves first
            count = 0
            for i in range(len(board)):
                if isValidMove(board, i, self.symbol):
                    count += 1
            # calculate the equal probability of choosing those valid moves
            prob = 1.0 / count
            # add those valid moves and their probabilities to the dictionary
            for i in range(len(board)):
                if isValidMove(board, i, self.symbol):
                    value += f"{i},{prob},"
            # remove comma at the end
            value = value[:-1]
            # add board state and probabilities to the dictionary
            self.move_dictionary[board] = value

        # add the move to the moves list
        self.moves.append(move)
            
        # return the move
        return move
    
    def endGame( self, status, board ):
        # reverse the board and moves lists so we can start from the end of the game
        self.boards.reverse()
        self.moves.reverse()

        # TODO: Fix reinforcement learning strategy

        for i in range(len(self.boards)):
            # check to see if the dictionary contains probabilities for moves
            value = self.move_dictionary.get(self.boards[i])
            # if it does exist, then we get the corresponding probabilities
            if value != None:
                line = value.strip().split(',')
                elements = [int(line[i]) for i in range(0, len(line), 2)]
                probabilities = [float(line[i+1]) for i in range(0, len(line), 2)]
    
            if status == 1:
               # agent won, add 1/2^i to that prob and subtract the appropriate amount from the rest
               mult = (1.0/2.0**i)
               temp = 0
               tile = 0
               for j in range(len(elements)):
                     if elements[j] == self.moves[i]:
                        tile = elements[j]
                        temp = probabilities[j] * mult
                        probabilities[j] += temp
                        break
               for j in range(len(probabilities)):
                  if j != tile:
                     probabilities[j] -= temp / len(elements)
            elif status == -1:
               # agent lost, decrease that prob by 1/2^i and add the appropriate amount to the rest
               mult = (1.0/2.0**i)
               temp = 0
               tile = 0
               for j in range(len(elements)):
                     if elements[j] == self.moves[i]:
                        tile = elements[j]
                        temp = probabilities[j] * mult
                        probabilities[j] -= temp
                        break
               for j in range(len(probabilities)):
                  if j != tile:
                     probabilities[j] += temp / len(elements)

            # normalize probabilities so that they sum to 1
            total_prob = sum(probabilities)
            if total_prob == 0:
                probabilities = [1.0 / len(probabilities) for i in range(len(probabilities))]
            else:
                probabilities = [p / total_prob for p in probabilities]
            
            # set value back to an empty string
            value = ""

            # iterate through the lists
            for j in range(len(elements)):
                value += f"{elements[j]},{probabilities[j]},"
            
            # remove the comma at the end
            value = value[:-1]

            # set the new probabilities in the dictionary
            self.move_dictionary[self.boards[i]] = value

        # delete everything in both lists to start over at the beginning of the next game
        del self.boards[:]
        del self.moves[:]
    
    def stopPlaying( self ):
        # write the new dictionary to the knowledgebase file
        with open(self.kb, 'w') as file:
            for key, value in self.move_dictionary.items():
                line = f"{key},{value}\n"
                file.write(line)
            file.close()