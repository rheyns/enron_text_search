from os import stat
from mmap import mmap

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
        return ('', int(vals[1]))
    return (vals[0], int(vals[1]))

def retrieve_partial_word(f, offset):
    if offset is 0:
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
    #Invariant left and right are after newline characters
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


fname = "offsetdict.txt"
fsize = stat(fname).st_size
f = open(fname, "r")

cdf = open("corpus_dict.txt")

#fm = mmap(f.fileno(),0)
f.seek(2000)
f.readline()
retrieve_partial_word(f, f.tell())
word1 = word_find(f,0,prev_newline(f,fsize)+1, 'ebook')
word2 = word_find(f,0,prev_newline(f,fsize)+1, 'beowulf')

corpus_extraction(f, word1, cdf)
corpus_extraction(f, word2, cdf)
