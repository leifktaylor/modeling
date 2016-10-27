class HashMap:
    def __init__(self, **kwargs):
        self.size = (20 + len(kwargs))
        self.map = [None] * self.size
        for k, v in kwargs.iteritems():
            self.add(k, v)

    def _get_hash(self, key):
        # get index of map to place k_v in
        hash = 0
        for char in str(key):
            hash += ord(char)
        return hash % self.size

    def add(self, key, value):
        key_hash = self._get_hash(key)
        key_value = [key, value]

        # if bucket is empty
        if self.map[key_hash] is None:
            self.map[key_hash] = list([key_value])
            return True
        else:
            for pair in self.map[key_hash]:
                # if key already exists, update value
                if pair[0] == key:
                    pair[1] == value
                    return True
            # if bucket is filled, append new k_v
            self.map[key_hash].append(key_value)
            return True

    def get(self, key):
        key_hash = self._get_hash(key)
        # if bucket is not empty
        if self.map[key_hash] is not None:
            for pair in self.map[key_hash]:
                # if key exists in bucket
                if pair[0] == key:
                    return pair[1]
        return None

    def delete(self, key):
        key_hash = self._get_hash(key)
        # if bucket is not empty
        if self.map[key_hash] is not None:
            for i in range(0, len(self.map[key_hash])):
                # if key exists in bucket
                if self.map[key_hash][i][0] == key:
                    self.map[key_hash].pop(i)
                    return True
        else:
            return False

    def print_map(self):
        print('---PHONEBOOK---')
        for item in self.map:
            if item:
                print(str(item))


def test():
    h = HashMap()
    h.add('Mike', '555-3890')
    h.add('Jake', '555-2389')
    h.add('Mike', '434-3333')
    h.add('Ragu', '555-1234')
    h.add('Johan', '222-2345')
    h.add('Amanda', '322-1234')
    h.add('Bob', '123-1233')
    h.add('Ming', '123-4344')
    h.add('Ankit', '323-3424')
    h.add('Dan', '123-3232')
    h.add('naD', '213-2398')
    h.add('Xi', '123-3298')
    h.add('Ragu', '444-4321')
    h.print_map()
    h.delete('Mike')
    h.print_map()
    print('Ragu: ' + h.get('Ragu'))
    return h
