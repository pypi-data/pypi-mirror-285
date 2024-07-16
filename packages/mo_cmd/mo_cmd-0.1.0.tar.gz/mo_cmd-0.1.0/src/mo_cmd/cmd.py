from mo_plus.plus import add
from mo_minus.minus import substract
from mo_divide.divide import divide

def call():
    a=int(input())
    b=int(input())
    print('add:::',add(a,b))
    print('substract:::',substract(a,b))
    print('divide:::',divide(a,b))
