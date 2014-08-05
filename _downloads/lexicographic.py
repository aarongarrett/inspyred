import functools

@functools.total_ordering
class Lexicographic(object):
    def __init__(self, values=None, maximize=True):
        if values is None:
            values = []
        self.values = values
        try:
            iter(maximize)
        except TypeError:
            maximize = [maximize for v in values]
        self.maximize = maximize

    def __len__(self):
        return len(self.values)
    
    def __getitem__(self, key):
        return self.values[key]
        
    def __iter__(self):
        return iter(self.values)
        
    def __lt__(self, other):
        for v, o, m in zip(self.values, other.values, self.maximize):
            if m:
                if v < o:
                    return True
                elif v > o:
                    return False
            else:
                if v > o:
                    return True
                elif v < o:
                    return False
        return False

    def __eq__(self, other):
        return (self.values == other.values and self.maximize == other.maximize)

    def __str__(self):
        return str(self.values)
        
    def __repr__(self):
        return str(self.values)


def my_evaluator(candidates, args):
    fitness = []
    for candidate in candidates:
        f = candidate[0] ** 2 + 1
        g = candidate[0] ** 2 - 1
        fitness.append(Lexicographic([f, g], maximize=False))
    return fitness

def my_generator(random, args):
    return [random.random()]
    
if __name__ == '__main__':
    a = Lexicographic([1, 2, 3], maximize=True)
    b = Lexicographic([1, 3, 2], maximize=True)
    c = Lexicographic([2, 1, 3], maximize=True)
    d = Lexicographic([2, 3, 1], maximize=True)
    e = Lexicographic([3, 1, 2], maximize=True)
    f = Lexicographic([3, 2, 1], maximize=True)
    
    u = Lexicographic([1, 2, 3], maximize=False)
    v = Lexicographic([1, 3, 2], maximize=False)
    w = Lexicographic([2, 1, 3], maximize=False)
    x = Lexicographic([2, 3, 1], maximize=False)
    y = Lexicographic([3, 1, 2], maximize=False)
    z = Lexicographic([3, 2, 1], maximize=False)
    
    for p in [a, b, c, d, e, f]:
        for q in [a, b, c, d, e, f]:
            print('%s < %s : %s' % (p, q, p < q))
    print('----------------------------------------')
    for p in [u, v, w, x, y, z]:
        for q in [u, v, w, x, y, z]:
            print('%s < %s : %s' % (p, q, p < q))
    










