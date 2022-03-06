#!/usr/bin/python3
"""
MIT License

Copyright (c) 2022 Curtis Case

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
---------------------------------------------------------------------------------
This simple python program adds a comment line at the end of each indented code
block as shown in the below example code 
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
"""

import os
import sys
import datetime
import pathlib
import argparse
import glob
from tokenize import generate_tokens, detect_encoding, TokenError
from token import *

indent_key_words = {'if': ('elif', 'else'),
                    'try': ('except', 'else', 'finally'),
                    'for': ('else',),
                    'while': ('else',),
                    'with': (),
                    'def': (),
                    'class': (),
                    'match':()}

#-------------------------------------------------------------------------------------------------------------
def untokenize(tokens):
    """
    Rebuild the python code source file from the tokdens list and add in
    properly indented comments at the end of each indented block. ie

    tokens_out = []

    prev_row = 1
    prev_col = 0

    indents = []
    newline = True
    last_indent = 0
    last_cmt_nl = -1
    last_tok_type = 0
    got_async = False
    newline_end = None
      
    for t in tokens:
        tok_type, token, start, end, line = t

        if last_cmt_nl == -1 and tok_type in (COMMENT, NL):

            #--Remember position in tokens_out of first COMMENT or NL
            last_cmt_nl = len(tokens_out)
        #end if

        #--are we all done?
        if tok_type == ENDMARKER: break

        if tok_type == NAME:
            if newline:
                if len(indents) > 0:
                    #--Do we need an end block for this?
                    if (token in indent_key_words[indents[-1][0]] and start[1] == indents[-1][1]) or start[1] > indents[-1][1]: indents[-1][2] = True

                    #--If our last indent was for a keyword (like 'if) with associated keywords (like 'else') and the current token/kew word is not one these associated keywords
                    #-- and we are at the same indent level  OR is the current indent level is less than the nlast indent level... then we need add min one or more 'end block comments'
                    if ((token not in indent_key_words[indents[-1][0]] and start[1] == indents[-1][1]) or start[1] < indents[-1][1]):

                        #--determine where to add then e d block comment; should be after last line of code, before comments or blank lines
                        ins_at = last_cmt_nl if last_cmt_nl != -1 else len(tokens_out)

                        #--Now add in the 'end block comments' until the indent level is less than the curremnt indent level 
                        for _ in range(len(indents),0,-1): 

                            dedent_name, indent_size, need_endblk = indents[-1]

                            #--if at same indent level and token is in the list of kw's for the current kw (ie 'else' for 'if'), then don't add end blk comment yet
                            if start[1] == indent_size and token in indent_key_words[indents[-1][0]]: break

                            indents.pop()

                            #--if we have something like 'if a == b: print(a)' ie all on one line with no folowing 'else' or 'elif', then we won't put the end blk comment in
                            if need_endblk:
                                tokens_out.insert(ins_at, f"{' ' * indent_size}{end_blk_cmts_dict[dedent_name]}{newline_end}")
                                ins_at += 1
                            #end if

                            if indent_size <= start[1]: break
                        #end for
                    #end if
                #end if

                #--Handle 'async def' and 'async for' by waiting for next name, which if first is 'async', then next should be 'def' or 'for' (but that is not checked)
                if token == 'async':
                    got_async = True
                    last_indent = start[1]
                else:
                    if got_async:
                        got_async = False
                    else:

                        #--did not have a sync xxx, so save current indent level as our current indent level
                        last_indent = start[1]
                    #end if

                    newline = False

                    if token in indent_key_words.keys():

                        #--Will we need an end block? ie the current keyword has caused another indent it will need an end blk comment 
                        if len(indents) > 0: indents [-1][2] = True
                        indents.append([token, last_indent, False])
                    #end if
                #end if
            #end if

        elif tok_type == INDENT:
            last_cmt_nl = -1
            last_tok_type = INDENT
            continue
            
        elif tok_type == DEDENT:
            continue
            
        elif tok_type in (NEWLINE, NL):
            if newline_end == None: newline_end = token

            if token not in ("\n", "\r\n", "\r"):
                #--sometimes at end of .py source file if there is no \n at end of last line, 
                #--then token is '', whereas it should always an end sequence consistent with the source file
                token = newline_end 
            #end if

            if tok_type == NEWLINE: newline = True
        #end if

        #--add any needed whitespace
        row, col = start

        row_offset = row - prev_row
        if row_offset > 0:
            tokens_out.append(f" \\{newline_end}" * row_offset)
            prev_col = 0
        #end if

        col_offset = col - prev_col
        if col_offset > 0:
            if prev_col == 0:
                tokens_out.append(' ' * col_offset)
            else:
                tokens_out.append(' ')
            #end if
        #end if

        #--Finally, add the token to output
        tokens_out.append(token)
        prev_row, prev_col = end

        if tok_type in (NEWLINE, NL):
            prev_row += 1
            prev_col = 0
        #end if

        #--sometines at end of .py source file if there is no \n at end of last source code line,
        #--then before the DENT there is a NEWLINE, this is the check for that---+
        #                                                                        V
        #                                      /-----------------------------------------------\
        if not (tok_type in (COMMENT, NL)) and not (last_tok_type == NL and tok_type == NEWLINE): 
            last_cmt_nl = -1
        #end if

        last_tok_type = tok_type
    #end for

    #--Do dedenting if needed at end of file
    ins_at = last_cmt_nl if last_cmt_nl != -1 else len(tokens_out)
    for _ in range(len(indents),0,-1): 
        dedent_name, indent_size, need_endblk = indents.pop()

        #--if we have something like 'if a == b: print(a)' ie all on one line with no following 'else' or 'elif', then we won't put the end blk comment in
        if need_endblk:
            tokens_out.insert(ins_at, f"{' ' * indent_size}{end_blk_cmts_dict[dedent_name]}{newline_end}")
            ins_at += 1
        #end if
    #end for

    return "".join(tokens_out)
#end def

#-------------------------------------------------------------------------------------------------------------
def remove_end_blocks(source_lines):
    stripped = []
    for line in source_lines: #.splitlines():
        ls = line.strip()
        if ls.replace('# ','#') not in end_blk_cmts_dict.values() and ls not in end_blk_cmts_dict.values(): stripped.append(line)
    #end for

    return stripped
#end def

#-------------------------------------------------------------------------------------------------------------
def make_tokens(source_lines):
    def readsource(lines):
        for line in lines:
            yield line
        #end for

        yield ''
    #end def

    return list(generate_tokens(readsource(source_lines).__next__))
#end def

#-------------------------------------------------------------------------------------------------------------
def check_to_overide_end_blk(kw, str):
    global end_blk_cmts_dict
    if str != '':
        sout = []
        did_hash = False
        for s in str:
            if s != ' ' and not did_hash:
                if s != '#': sout.append('#')
                did_hash = True
            #end if

            sout.append(s)
        #end for

        end_blk_cmts_dict[kw] = ''.join(sout)
    #end if
#end def

#-------------------------------------------------------------------------------------------------------------
def get_options_from_cmd_line():

    #--Set up cmd line pargser and add arguments
    parser = argparse.ArgumentParser(prog='python pyformatter.py')
    parser.add_argument(dest='filename', metavar='filename', default='test_input-b', nargs='?', help='the file to format')
    parser.add_argument('-r', '--recursive', dest='recursive', action='store_true', help='recurse through sub directories')
    parser.add_argument('-o', '--onlyremove', dest='onlyremove', action='store_true', help='only remove end blocxk comment (previously added) from source files, token file will not be made either')
    parser.add_argument('-t', '--tokensave', dest='tokensave', action='store_true', help='save tokens to file named filename.py.tokens.txt')
    parser.add_argument('--do_case_blk_end', dest='do_case_blk_end', action='store_true', help='add block end comments for then match case blocks (for Python 3.10 source code)')
    parser.add_argument('--blk_end_prefix', dest='block_end_prefix', metavar="' end '", default='end ', help='prefix to prepend to end of block keyword, ie for ''if'' ''end '' would generate ''#end if''')
    parser.add_argument('--blk_end_suffix', dest='block_end_suffix', metavar="''", default='', help='suffix to append to end of block keyword, ie for ''if'' '' end'' would generate ''#if end''')
    parser.add_argument('--blk_end_if', dest='block_end_if', metavar="'endif'", default='', help='block end comment for ''if'', overrides blk_end_prefix and blk_end_suffix')
    parser.add_argument('--blk_end_try', dest='block_end_try', metavar="'endtry'", default='', help='block end comment for ''try'' exception blocks, overrides blk_end_prefix and blk_end_suffix')
    parser.add_argument('--blk_end_for', dest='block_end_for', metavar="'next'", default='', help='block end comment for ''for'' loops, overrides blk_end_prefix and blk_end_suffix')
    parser.add_argument('--blk_end_while', dest='block_end_while', metavar="'wend'", default='', help='block end comment for ''while'' loops, overrides blk_end_prefix and blk_end_suffix')
    parser.add_argument('--blk_end_with', dest='block_end_with', metavar="'endwith'", default='', help='block end comment for ''with'' blocks, overrides blk_end_prefix and blk_end_suffix')
    parser.add_argument('--blk_end_def', dest='block_end_def', metavar="'enddef'", default='', help='block end comment for ''def'' functions, overrides blk_end_prefix and blk_end_suffix')
    parser.add_argument('--blk_end_class', dest='block_end_class', metavar="'endclass'", default='', help='block end comment for ''class'' definitions, overrides blk_end_prefix and blk_end_suffix')
    parser.add_argument('--blk_end_match', dest='block_end_match', metavar="'endmatch'", default='', help='block end comment for ''match'' statement, overrides blk_end_prefix and blk_end_suffix')
    parser.add_argument('--blk_end_case', dest='block_end_case', metavar="'endcase'", default='', help='block end comment for ''case'' used in ''match'' statement (--do_case_blk_end must be selected), overrides blk_end_prefix and blk_end_suffix')

    #--Parse the arguments and options
    return parser.parse_args()
#end def

#-------------------------------------------------------------------------------------------------------------
def setup_end_blocks(options):
    global filename, recursive, onlyremove, tokensave, end_blk_cmts_dict

    filename = options.filename
    recursive = options.recursive
    tokensave = options.tokensave
    onlyremove = options.onlyremove

    #--Normanlly we don't add in 'case' end blk comments, unless asked for
    if options.do_case_blk_end: indent_key_words['case'] = ()

    #--Create end block comments dictrionary, used to add end block comments for indenting keywords
    end_blk_cmts_dict = {dedent_name:f"#{options.block_end_prefix}{dedent_name}{ options.block_end_suffix}" for dedent_name in indent_key_words.keys()}

    #--Always add this in so we remove 'case' end block comments
    if not options.do_case_blk_end: end_blk_cmts_dict['case'] = f"#{options.block_end_prefix}case{ options.block_end_suffix}"

    #--Optionally override individual end block comments for specific key words 
    check_to_overide_end_blk('if', options.block_end_if)
    check_to_overide_end_blk('try', options.block_end_try)
    check_to_overide_end_blk('for', options.block_end_for)
    check_to_overide_end_blk('while', options.block_end_while)
    check_to_overide_end_blk('with', options.block_end_with)
    check_to_overide_end_blk('def', options.block_end_def)
    check_to_overide_end_blk('class', options.block_end_class)
    check_to_overide_end_blk('match', options.block_end_match)
    check_to_overide_end_blk('case', options.block_end_case)
#end def

#-------------------------------------------------------------------------------------------------------------
def add_end_blocks(source_lines, filename, encoding):

    try:
        tokens = make_tokens(source_lines)
        
        #--optionally save the tokens to a file
        if tokensave: 
            with open(f"{filename}.tokens.txt", 'w', encoding=encoding) as fout: fout.writelines(f"{token}\n" for token in tokens)
        #end if

        #--Regenerate the source code file with previously set options and write to file

        return untokenize(tokens)

    except IndentationError as err:
        sys.stderr.write(f"IndentationError exception in {err.args[1][0]} while processing file:\n{filename}\nat line:{err.args[1][1]}, column:{err.args[1][2]} error: {err.args[0]}in line:\n{err.args[1][3]}")
        return ''

    except TokenError as err:
        sys.stderr.write(f"{filename}: at line:{err.args[1][0]}, column:{err.args[1][1]} error: {err.args[0]}\n")
        return ''

    except SyntaxError as err:
        sys.stderr.write(f"{filename}: at line:{err.args[1][1]}, column:{err.args[1][2]} error: {err.args[0]}\n")
        return ''

    except ValueError as err:
        sys.stderr.write(f"stderr> {filename}: at line:{err.args[1][0]}, column:{err.args[1][1]} error: {err.args[0]}\n")
        sys.stderr.write(f"{err}\n")
        raise
    #end try
#end def

def get_encoding(filename):
    """Return file encoding."""
    try:
        with open(filename, 'rb') as input_file: encoding = detect_encoding(input_file.readline)[0]

        with open(filename, mode='r', encoding=encoding, newline='') as test_file: test_file.read()

        return encoding
    except (LookupError, SyntaxError, UnicodeDecodeError):
        return 'latin-1'
    #end try
#end def

#-------------------------------------------------------------------------------------------------------------
def main():
    
    #--With options and file name form command line, set up end block comment parameters
    setup_end_blocks(get_options_from_cmd_line())

    try:
        #--Make list of files to process using glob and only include *.py files
        file_list = [fn for fn in glob.glob(filename, recursive=recursive) if pathlib.Path(fn).suffix.lower() == '.py' and os.path.isfile(fn)]

        for fn in file_list:
            encoding = get_encoding(fn)

            #--read the spython source file
            with open(fn, mode='rt', encoding=encoding, newline='') as f: source = f.readlines()

            #--remove any old end block comments (Note: only removes comments in the same format that is currently selected)
            source = remove_end_blocks(source)

            #--Now add the end block commants
            if not onlyremove: source = add_end_blocks(source, fn, encoding)

            #--Save the new Python source file (replaces original)
            with open(fn, 'w', encoding=encoding, newline='') as fout: fout.write(source)
        #end for

    except OSError as err:
        sys.stderr.write(f"OSError Exception: {err}\n")
        sys.exit(1)

    except KeyboardInterrupt:
        print("interrupted\n")
    except Exception as err:
        sys.stderr.write(f"Exception error: {err}\n")
        raise
    #end try
#end def

if __name__ == "__main__": main()
