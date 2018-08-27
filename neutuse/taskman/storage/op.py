class Op():
    pass


class And(Op):

    def __init__(self, a, b):
        self.a = a
        self.b = b


class Or(Op):
    
    def __init__(self, a, b):
        self.a = a
        self.b = b


class Greater(Op):
    
    def __init__(self, a, b):
        self.a = a
        self.b = b


class Equal(Op):
    
    def __init__(self, a, b):
        self.a = a
        self.b = b

class Not(Op):
    
    def __init__(self, a):
        self.a = a
