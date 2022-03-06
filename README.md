# addendblocks
This simple python program adds a comment line at the end of each indented code
block as shown in the below before/after example code below:
(has some bad coding style, but shows how it is handled)

  Before:
```python
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
```

  After:
```python
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
```
```
usage: python addendblocks.py [-h] [-r] [-o] [-t] [--do_case_blk_end]
                              [--blk_end_prefix 'end '] [--blk_end_suffix '']
                              [--blk_end_if 'endif'] [--blk_end_try 'endtry']
                              [--blk_end_for 'next'] [--blk_end_while 'wend']
                              [--blk_end_with 'endwith']
                              [--blk_end_def 'enddef']
                              [--blk_end_class 'endclass']
                              [--blk_end_match 'endmatch']
                              [--blk_end_case 'endcase']
                              [filename]

Program to read Python source code and add properly indented comments at the
end of indented code blocks, with appropriate names based on the keyword that
the indentation is for.

positional arguments:
  filename              the file to add/remove end block comments to/from. Can
                        use wild cards (*, ?) and will look in subdirectories
                        if the -r option is selected

optional arguments:
  -h, --help            show this help message and exit
  -r, --recursive       recurse through sub directories looking for matching
                        files
  -o, --onlyremove      only remove end block comments (previously added) from
                        source files, token file will not be made either (-t)
  -t, --tokensave       save tokens to file named filename.py.tokens.txt
  --do_case_blk_end     add block end comments for the 'match' 'case' blocks.
                        Normlly only end block comments are added for the
                        'match' statements, not the 'case' statements in the
                        'match' statements. (for Python 3.10 source code)
  --blk_end_prefix 'end '
                        prefix to prepend to end of block keyword, ie for
                        'if', 'end ' would generate '#end if'
  --blk_end_suffix ''   'suffix to append to end of block keyword, ie for
                        'if', ' end' would generate '#if end'
  --blk_end_if 'endif'  block end comment for 'if', overrides blk_end_prefix
                        and blk_end_suffix
  --blk_end_try 'endtry'
                        block end comment for 'try' exception blocks,
                        overrides blk_end_prefix and blk_end_suffix
  --blk_end_for 'next'  block end comment for 'for' loops, overrides
                        blk_end_prefix and blk_end_suffix
  --blk_end_while 'wend'
                        block end comment for 'while' loops, overrides
                        blk_end_prefix and blk_end_suffix
  --blk_end_with 'endwith'
                        block end comment for 'with' blocks, overrides
                        blk_end_prefix and blk_end_suffix
  --blk_end_def 'enddef'
                        block end comment for 'def' functions, overrides
                        blk_end_prefix and blk_end_suffix
  --blk_end_class 'endclass'
                        block end comment for 'class' definitions, overrides
                        blk_end_prefix and blk_end_suffix
  --blk_end_match 'endmatch'
                        block end comment for 'match' statement, overrides
                        blk_end_prefix and blk_end_suffix
  --blk_end_case 'endcase'
                        block end comment for 'case' used in 'match' statement
                        (--do_case_blk_end must be selected), overrides
                        blk_end_prefix and blk_end_suffix
```
