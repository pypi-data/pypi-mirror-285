#from front11_plus import add
#from front11_div import divide
#from front11_multi import multiply
import sys

a = sys.argv[0]
x = int(sys.argv[1])
y = int(sys.argv[2])

def add(x, y):
    return x + y
  
def multiply(x, y):
    return x * y

def divide(x, y):
    if y == 0:
        raise ValueError("Division by zero is not allowed")
    else:
        return x / y

#print(f"a={a}, b={b}, c={c}")
