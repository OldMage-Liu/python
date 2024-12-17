import sys
lines = {}
for i in sys.stdin():
    if i in lines:
        lines[i] += 1
    else:
        lines[i] = 1
print(lines)