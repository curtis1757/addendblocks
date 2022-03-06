# Just a test input file for addendblocks.py

def proc_a(a, b):
    if a == 3:
        for i in range(3): print(i)
        for j in range(4):
            print(j)
            if j == 2: break
        else:
            print('did not break out of for loop')
    else:
        print('a is not 3')
    #Do a for loop now
    for i in range(3): print(i)
    else: x = 2

    if a == 4: 
        print('c')
    if b == 'keywords': b = 'k'
    elif b == 'symbols': b = 's'
    print(b)
    match b:
        case 'push':
            print('pushing')
        case 'pull':
            print('pulling')

proc_a(3, 'push')
proc_a(4, 'keywords')
