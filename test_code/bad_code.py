# 나쁜 코드 예제
import os

def add(a, b):
    return a + b

def div(x, y):
    return x / y  # 0으로 나누면 에러!

if __name__ == "__main__":
    print(add(1, 2))
    print(div(10, 0))
