from os import stat
from mmap import mmap

_end = " end"
ENDCHAR = ' '

def corpus_extraction(f, idx, cdf):
    f.seek(idx)
    str = f.readline()
    vals = [s.strip() for s in str.split(':')]
    if len(vals) != 3:
        return ''
    cdf.seek(int(vals[2]))
    return cdf.readline()

def line_extraction(str):
    vals = [s.strip() for s in str.split(':')]
    if len(vals) == 3:
        return (ENDCHAR, int(vals[1]))
    return (vals[0], int(vals[1]))

def retrieve_partial_word(f, offset):
    if offset is -1:
        return ''
    f.seek(offset)
    line = f.readline()
    info = line_extraction(line)
    return retrieve_partial_word(f, info[1]) + info[0]

def prev_newline(f,pos):
    while f.read(1) != '\n':
        pos -= 1
        f.seek(pos)
    return pos

def word_find(f, left, right, word):
    """ Attempt to find a word via bisection"""
    # Invariant left, right and mid are after newline characters
    # Word must end in ENDCHAR for complete matching
    if word[-1:] != ENDCHAR:
        word += ENDCHAR
    mid = (left+right)/2-1
    mid = prev_newline(f, mid)
    mid += 1
    if mid <= left:
        f.seek(mid)
        f.readline()
        mid = f.tell()
    if mid >= right:
        return -1
    pword = retrieve_partial_word(f,mid)
    if pword == word:
        return mid
    if pword < word:
        return word_find(f, mid, right, word)
    if pword > word:
        return word_find(f, left, mid, word)

if __name__ == "__main__":
    fname = "offsetdict.txt"
    fsize = stat(fname).st_size
    f = open(fname, "r")
    
    cdf = open("corpus_dict.txt")
    
    #fm = mmap(f.fileno(),0)
    f.seek(20)
    f.readline()
    print retrieve_partial_word(f, f.tell())
    word1 = word_find(f,0,prev_newline(f,fsize)+1, 'be')
    word2 = word_find(f,0,prev_newline(f,fsize)+1, 'beowulf')
    print word1, word2
    
    print corpus_extraction(f, word1, cdf)
    print corpus_extraction(f, word2, cdf)
