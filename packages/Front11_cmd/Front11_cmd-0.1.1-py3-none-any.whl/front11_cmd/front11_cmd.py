from front11_plus.py import add
from front11_div.py import divide
from front11_multi.py import multiply

def add(x, y):
    return x + y

def multiply(x, y):
    return x * y

def divide(x, y):
    if y == 0:
        raise ValueError("Division by zero is not allowed")
    return x / y
