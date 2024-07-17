mo조 [김태민, 오지현]: mo_cmd

## 설치
```
pip install mo_cmd
```
## 실행
```
$ mo-cmd
$ 정수 입력1
$ 정수 입력2 
```
## 코드
```
from mo_plus.plus import add
from mo_minus.minus import substract
from mo_divide.divide import divide

def call():
    a=int(input())
    b=int(input())
    print('add:',add(a,b))
    print('substract:',substract(a,b))
    print('divide:',divide(a,b))
```

## Dependencies

    "mo-plus>=0.1.0",
    "mo-minus>=0.1.0",
    "mo-divide>=0.1.0",
