'''
HELPER FUNCTIONS TO SIMPLIFY EVAL PROCESSING OF RETURN VALUES FROM API CALLS
'''

def getFunc(piece):
    def piece_func():
        return piece
    return piece_func()

def Bishop():
    return getFunc("Bishop")

def Pawn():
    return getFunc("Pawn")

def King():
    return getFunc("King")

def Queen():
    return getFunc("Queen")

def Knight():
    return getFunc("Knight")

def Rook():
    return getFunc("Rook")
