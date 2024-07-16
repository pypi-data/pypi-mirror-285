from seokbong_add.add import add
from seokbong_division.division import divide
from seokbong_mul.mul import mul

def call():
    choose = int(input("덧셈(1), 곱셈(2), 나눗셈(3) 입력 : "))
    if choose == 1:
        add()
        pass
    elif choose == 2:
        mul()
        pass
    elif choose == 3:
        divide()
