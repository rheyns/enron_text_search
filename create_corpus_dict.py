from mmap import mmap
from collections import defaultdict
import re

def recursive():
    return defaultdict(recursive)

_end = ' end'

def make_trie(words):
    trie = {}
    for word in words:
        current_dict = trie
        for letter in word:
            current_dict = current_dict.setdefault(letter, {})
        current_dict = current_dict.setdefault(_end, word)
    return trie

def tp(trie):
    for key in trie:
        print key
        if key != _end:
            tp(trie[key])

def trie_write(trie, f, parent_pos=-1):
    for key in sorted(trie):
        if key is _end:
            f.write(key + ': ' + str(parent_pos) + ' : ' + str(trie[key]) + "\n")
        if key is not _end:
            idx = f.tell()
            f.write(key + ': ' + str(parent_pos) + "\n")
            trie_write(trie[key], f, idx)

def clean(str):
    pattern = re.compile('[\W_]+')
    return pattern.sub('', str).lower()

def make_worddict(mappedfile):
    worddict = defaultdict(list)
    idx = 0
    
    while idx <= len(mappedfile):
        newidx = mappedfile.find(" ",idx)
        if newidx == -1:
            break
        word = clean(mappedfile[idx:newidx])
        worddict[word].append(idx)
        idx = newidx + 1
    return worddict

def run():
    f = open("beowulf.txt", "r+b")
    mappedfile = mmap(f.fileno(),0)
    worddict = make_worddict(mappedfile)
    
    keys = sorted(worddict)
    trie = make_trie(keys)
    
    with open("corpus_dict.txt", "w") as of:
        for key in keys:
            t = trie
            for letter in key:
                t = t[letter]
            t[_end] = of.tell()
            of.write(key + ":" + worddict[key].__repr__() + "\n")
    
    with open("offsetdict.txt", "w") as of:
        trie_write(trie, of)


if __name__ == "__main__":
    run()
