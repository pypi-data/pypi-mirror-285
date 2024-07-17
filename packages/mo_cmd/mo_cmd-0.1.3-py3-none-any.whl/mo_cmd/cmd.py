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
