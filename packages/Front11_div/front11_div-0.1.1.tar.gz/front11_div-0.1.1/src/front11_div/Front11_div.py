from calculator import divide

def divide(x, y):
    if y == 0:
        raise ValueError("Division by zero is not allowed")
    return x /y
