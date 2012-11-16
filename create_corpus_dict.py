"""
Provide functions for creating a two-level dictionary of medium-sized
input text. Representations of the input text must fit into available
machine memory.

See run() for a usage example.
"""
from mmap import mmap
from collections import defaultdict
import re


def recursive():
    """Define a recursive data structure containing defaultdicts"""
    return defaultdict(recursive)

_END = ' end'


def make_trie(words):
    """Construct a trie based on nested dictionaries from an
    iterable containing strings."""
    trie = {}
    for word in words:
        current_dict = trie
        for letter in word:
            current_dict = current_dict.setdefault(letter, {})
        current_dict = current_dict.setdefault(_END, word)
    return trie


def trie_print(trie):
    """Print a representation of a trie based on nested dictionaries
    mostly used for debugging"""
    for key in trie:
        print key
        if key != _END:
            trie_print(trie[key])


def trie_write(trie, outfile, parent_pos=-1):
    """Write a nested-dictionary based trie to file outfile
    Per line output consists of a single character followed by a colon
    and the file offset of the parent node."""
    for key in sorted(trie):
        if key is _END:
            outfile.write(
                key + ': ' + str(parent_pos) + ' : ' + str(trie[key]) + "\n")
        if key is not _END:
            idx = outfile.tell()
            outfile.write(key + ': ' + str(parent_pos) + "\n")
            trie_write(trie[key], outfile, idx)


def clean(dirtystring):
    """Remove non-alphanumeric characters and lowercase all input"""
    pattern = re.compile(r'[\W_]+')
    return pattern.sub('', dirtystring).lower()


def make_worddict(mappedfile):
    """Construct an in-memory dictionary containing file offsets of unique
    space delimited words in a memory-mapped file."""
    worddict = defaultdict(list)
    idx = 0

    while idx <= len(mappedfile):
        newidx = mappedfile.find(" ", idx)
        if newidx == -1:
            break
        word = clean(mappedfile[idx:newidx])
        worddict[word].append(idx)
        idx = newidx + 1
    return worddict

def create_dicts(source_text_file):
    """Creates a two-level index of words occurring in an input text
    First level 'corpus_dict.txt' contains references to individual occurrences
    of words in the source text file. 
    
    Meanwhile the second level 'offsetdict.txt' contains a serialized
    representation of a trie of words from the first level index. Representing
    words in a trie allows full-text search of devices with severe memory
    contraints."""
    mappedfile = mmap(source_text_file.fileno(), 0)
    worddict = make_worddict(mappedfile)

    keys = sorted(worddict)
    trie = make_trie(keys)

    with open("corpus_dict.txt", "w") as outfile:
        # Attach primary dictionary offset information to terminator nodes in
        # the trie representing the second level lookup index.
        for key in keys:
            node = trie
            for letter in key:
                node = node[letter]
            node[_END] = outfile.tell()
            outfile.write(key + ":" + worddict[key].__repr__() + "\n")

    with open("offsetdict.txt", "w") as outfile:
        trie_write(trie, outfile)
    
    mappedfile.close()

def run():
    """Demonstrates the creation of multilevel dictionary files."""
    source_text_file = open("beowulf.txt", "r+b")
    create_dicts(source_text_file)
    


if __name__ == "__main__":
    run()
