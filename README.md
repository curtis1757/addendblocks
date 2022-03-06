# addendblocks
This simple python program adds a comment line at the end of each indented code
block as shown in the below before/after example code below:
(has some bad coding style, but shows how it is handled)

  Before:
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


  After:
def proc_a(a, b):
    if a == 3:
        for i in range(3): print(i)
        for j in range(4):
            print(j)
            if j == 2: break
        else:
            print('did not break out of for loop')
        #end for
    else:
        print('a is not 3')
    #end if
    #Do a for loop now
    for i in range(3): print(i)
    else: x = 2
    #end for

    if a == 4: 
        print('c')
    #end if
    if b == 'keywords': b = 'k'
    elif b == 'symbols': b = 's'
    #end if
    print(b)
    match b:
        case 'push':
            print('pushing')
        case 'pull':
            print('pulling')
    #end match
#end def
