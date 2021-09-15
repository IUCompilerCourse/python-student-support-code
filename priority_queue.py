def swap(A, i, j):
    tmp = A[i]
    A[i] = A[j]
    A[j] = tmp

def less(x, y):
    return x < y

def less_key(x, y):
    return x.key < y.key

def update_position(obj, pos):
    obj.position = pos

def get_position(obj):
    return obj.position

def ignore_update(obj, pos):
    pass

class Heap:
    def __init__(self, data, 
                 less = less,
                 update = ignore_update):
        self.data = data
        self.less = less
        self.update = update
        i = 0
        for obj in self.data:
            self.update(obj, i)
            i += 1
        build_max_heap(self)
        
    def __repr__(self):
        return repr(self.data[:self.heap_size])

    def maximum(self):
        return self.data[0]

    def insert(self, obj):
        self.heap_size += 1
        if len(self.data) < self.heap_size:
            self.data.append(obj)
        else:
            self.data[self.heap_size - 1] = obj
        self.update(obj, self.heap_size - 1)
        heap_increase_key(self, self.heap_size - 1)

    def extract_max(self):
        assert self.heap_size != 0
        max = self.data[0]
        self.data[0] = self.data[self.heap_size-1]
        self.update(self.data[0], 0)
        self.heap_size -= 1
        max_heapify(self, 0)
        return max
        
def left(i):
    return 2 * i + 1

def right(i):
    return 2 * (i + 1)

def parent(i):
    return (i-1) // 2

def heap_increase_key(H, i):
    while i > 0 and H.less(H.data[parent(i)], H.data[i]):
        swap(H.data, i, parent(i))
        H.update(H.data[i], i)
        H.update(H.data[parent(i)], parent(i))
        i = parent(i)

def max_heapify(H, i):
    l = left(i)
    r = right(i)
    if l < H.heap_size and H.less(H.data[i], H.data[l]):
        largest = l
    else:
        largest = i
    if r < H.heap_size and H.less(H.data[largest], H.data[r]):
        largest = r
    if largest != i:
        swap(H.data, i, largest)
        H.update(H.data[i], i)
        H.update(H.data[largest], largest)
        max_heapify(H, largest)

def build_max_heap(H):
    H.heap_size = len(H.data)
    last_parent = len(H.data) // 2
    for i in range(last_parent, -1, -1):
        max_heapify(H, i)

def heap_sort(H):
    build_max_heap(H)
    for i in range(len(H.data)-1, 0, -1):
        swap(H.data, 0, i)
        H.update(H.data[0], 0); H.update(H.data[i], i)
        H.heap_size -= 1
        max_heapify(H, 0)

class PriorityQueue:
    def __init__(self, less=less_key, update=update_position, get=get_position):
        self.heap = Heap([], less=less, update=update)
        self.get_position = get
        self.get_object = {}

    def __repr__(self):
        return repr(self.heap)

    def push(self, key):
        o = Obj(key)
        self.get_object[key] = o
        self.heap.insert(o)

    def pop(self):
        return self.heap.extract_max().key

    def increase_key(self, key):
        obj = self.get_object[key]
        heap_increase_key(self.heap, self.get_position(obj))

    def empty(self):
        return self.heap.heap_size == 0

class Obj:
    def __init__(self, k):
        self.key = k
        self.position = -1

    def __repr__(self):
        return str(self.key) + '@' + repr(self.position)

if __name__ == "__main__":
    # test build and extract_max
    L = [4,3,5,1,2]
    h = Heap(L)
    for i in range(5, 0, -1):
        assert h.extract_max() == i

    # test insert
    L = [4,3,5,1,2]
    for k in L:
        h.insert(k)
    for i in range(5, 0, -1):
        assert h.extract_max() == i
    
    # test sort
    L = [4,3,5,1,2]
    heap_sort(Heap(L))
    for i in range(0, 5):
        assert L[i] == i + 1

    # Test priority queue
    # Q = PriorityQueue()
    # for i in range(1, 6):
    #     Q.push(Obj(i))
    # for i in range(5, 0, -1):
    #     assert Q.pop().key == i

    L = {'a': 4, 'b': 3, 'c':5,'d':1,'e':2}
    def less(x, y):
        return L[x.key] < L[y.key]
    Q = PriorityQueue(less)
    for k, v in L.items():
        Q.push(k)

    # test increase_key
    for k, v in L.items():
        L[k] = v + 2
        Q.increase_key(k)
    for i in range(5, 0, -1):
        k = Q.pop()
        assert L[k] == i + 2

    print('passed all tests')
