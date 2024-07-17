import sys

def add(x, y):
    return x + y


a = int(sys.argv[0])
b = int(sys.argv[1])

result = add(a, b)
print(f"a={a},"+" b={b} : {result}")
