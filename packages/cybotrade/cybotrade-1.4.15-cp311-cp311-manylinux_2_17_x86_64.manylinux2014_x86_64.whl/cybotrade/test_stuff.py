import collections
import numpy as np

x = {}
x['test'] = collections.deque()
y = x['test']

if len(y) == 0:
    y.append("123")


print(x['test'])



# deque = collections.deque(['jank','value','stuff', 'interesting'])



# print(arr)


