import os
def payl():
    
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'payload.txt'))
    return path
