import sys
from power01_plus.plus import plus
from power01_min.min import minus
from power01_mul.mul import mul
from power01_div.div import div


def call():
    a = int(sys.argv[1])
    b = int(sys.argv[2])    
    print('a+b= ',end="")
    plus(a,b)
    print()
    print('a-b= ',end="")
    minus(a,b)
    print()
    print('a*b= ',end="")
    mul(a,b)
    print()
    print('a/b= ',end="")
    div(a,b)

    print('success!!')
