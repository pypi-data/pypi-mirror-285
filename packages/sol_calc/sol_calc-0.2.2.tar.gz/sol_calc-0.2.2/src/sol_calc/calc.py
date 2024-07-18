from sol_add.add import add
from sol_mul.mul import mul
from sol_div.div import div

import sys
x = int(sys.argv[1])
y = int(sys.argv[2])

def a():
    add(x, y)

def m():
    mul(x, y)

def d():
    div(x, y)
