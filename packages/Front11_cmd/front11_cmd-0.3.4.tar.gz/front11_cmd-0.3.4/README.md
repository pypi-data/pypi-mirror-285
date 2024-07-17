# Front11_cmd

## **install**

```
$ pip install Front11_cmd

```

## **Usage**

```
x = int(sys.argv[1])
y = int(sys.argv[2])
```

```
$ Front11-plus x y 
$ Front11-multi x y 
$ Front11-div x y
```

## **Code**
```python
from front11_plus.front11_plus import add           #더하기
from front11_div.front11_div import divide          #나누기
from front11_multi.front11_multi import multiply    #곱하기

import sys
a = sys.argv[0]
x = int(sys.argv[1])
y = int(sys.argv[2])


def a():
    add(x, y)

def m():
    multiply(x, y)

def d():
    divide(x, y)
```

## **Reference**
-https://github.com/Nicou11/Front11_cmd

-https://github.com/Nicou11/Front11_div

-https://github.com/minju210/Front11_plus

-https://github.com/minju210/Front11_multi

## **Thank you**
