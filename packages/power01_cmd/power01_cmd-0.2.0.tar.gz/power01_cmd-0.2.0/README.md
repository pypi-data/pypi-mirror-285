# power01_cmd


# 설치 방법
```
$ pip install power01_cmd
```

# 코드
```
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
```

# 실행
```
$ cmd 5 10 
```

# 결과
```
a+b= 15

a-b= -5

a*b= 50

a/b= 0.5
success!!
```

# 참조
- https://github.com/baechu805/power01_plus
- https://github.com/baechu805/power01_min
- https://github.com/sooj1n/power01_mul
- https://github.com/sooj1n/power01_div
