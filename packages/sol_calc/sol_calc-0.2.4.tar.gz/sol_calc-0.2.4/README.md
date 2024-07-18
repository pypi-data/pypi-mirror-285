# sol_calc

## Intro
simple calcaulator

<img src="./src/sol_calc/img/test_sol_calc.png">

## Usage
### Install
```
$ pip install sol_calc
```
### Python code
```python
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
```
### Add pyproject.toml option
```
dependencies = ["sol_add>=0.1.0", "sol_mul>=0.1.0", "sol_div>=0.1.0"]

[project.scripts]
sol-add = "sol_calc.calc:a"
sol-mul = "sol_calc.calc:m"
sol-div = "sol_calc.calc:d"
```
### References
- add : https://github.com/j25ng/sol_add
- mul : https://github.com/j25ng/sol_mul
- div : https://github.com/j25ng/sol_div
