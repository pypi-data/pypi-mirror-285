## 설치
```
pip install mo_cmd
```
## 실행
```
$ mo-plus <정수 입력1> <정수입력2>
mo-plus 5 6
11

$ mo-minus <정수 입력1> <정수입력2>
mo-minus 9 23
-14

$ mo-divide <정수 입력1> <정수입력2>
mo-minus 10 4
2.5
```

## 실행결과
![image](https://github.com/user-attachments/assets/9ff4bcbd-03d8-42be-8455-34ac4f6a6977)

## 코드
```
import sys
from mo_plus.plus import add
from mo_minus.minus import substract
from mo_divide.divide import divide

def plus():
    a=int(sys.argv[1])
    b=int(sys.argv[2])
    print('',add(a,b))

def minus():
    a=int(sys.argv[1])
    b=int(sys.argv[2])
    print('',substract(a,b))

def div():
    a=int(sys.argv[1])
    b=int(sys.argv[2])
    print('',divide(a,b))
```

## Dependencies

    "mo-plus>=0.1.0",
    "mo-minus>=0.1.0",
    "mo-divide>=0.1.0",
