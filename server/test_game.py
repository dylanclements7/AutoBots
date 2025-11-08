import random 
class TestGame: 

    def makeMove(move, state, players, player_num):
        """possible moves are 1 or 0, 1 lowers the count 0 does nothing"""
        """state: 
        
            {
            
            count: <current count> 
            
            }
        """
        
        count = state.get('count') + move 
        if count == 0: 
            return {'winner':True, 'player' : player_num} 
        
        else: 
            return {'count': count, 'players': players }, player_num + 1 % len(players)
        

    
    def generateState(): 
        return {
        
            'count': 15
            
            }
    def isMoveLegal(move, state, players, player_num ): 
        return move in [0,1]
    
    
