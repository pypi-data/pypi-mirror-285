import sys

a = sys.argv[0]
x = int(sys.argv[1])
y = int(sys.argv[2])

def divide(x, y):
    if y == 0:
        raise ValueError("Division by zero is not allowed")
    else:
        return x / y

print(divide(x,y))
    
