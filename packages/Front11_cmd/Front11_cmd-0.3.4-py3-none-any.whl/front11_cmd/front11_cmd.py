from front11_plus.front11_plus import add           #더하기
from front11_div.front11_div import divide          #나누기
from front11_multi.front11_multi import multiply    #곱하기

import sys
a = sys.argv[0]
x = int(sys.argv[1])
y = int(sys.argv[2])


def a():
    add(x, y)
#    x = int(sys.argv[1])
#    y = int(sys.argv[2])
#    return x + y
  
def m():
    multiply(x, y)
#    return x * y

def d():
    divide(x, y)
#    if y == 0:
#        raise ValueError("Division by zero is not allowed")
#    else:
#        return x / y


#print(f"a={a}, b={b}, c={c}")
