"""
Provide functions for searching for word occurrences using a two-level
input dictionary generated by 'create_corpus_dict.py'

This implementation should work on memory constrained devices. The current
implementation will execute O(k lg(N)) file seek and read operations in the
worst case. Here N is the length of the trie representing all the unique words
in the input text and k represents the length of the longest word in the input
text.
"""
from os import stat

_END = " end"
ENDCHAR = ' '


def corpus_extraction(offsetf, idx, cdf):
    """
    Return source text references from the first level index for the word
    represented at file offset idx in the second level index.
    
    If idx does not represent a word terminator this will return the empty
    string.
    """
    offsetf.seek(idx)
    line = offsetf.readline()
    vals = [s.strip() for s in line.split(':')]
    if len(vals) != 3:
        return ''
    cdf.seek(int(vals[2]))
    return cdf.readline()


def line_extraction(line):
    """
    Given an input string from the second level index extract the node letter
    and offset for the parent node and return these as a tuple. In the case of
    a word terminator return the character ENDCHAR as the node letter.
    """
    vals = [seg.strip() for seg in line.split(':')]
    if len(vals) == 3:
        return (ENDCHAR, int(vals[1]))
    return (vals[0], int(vals[1]))


def retrieve_partial_word(offsetfile, offset):
    """
    Return the partial word from the second level trie at position offset.
    """
    if offset is -1:
        return ''
    offsetfile.seek(offset)
    line = offsetfile.readline()
    info = line_extraction(line)
    return retrieve_partial_word(offsetfile, info[1]) + info[0]


def prev_newline(infile, pos):
    """
    Find newline preceding the current position pos in the input file.
    """
    while infile.read(1) != '\n':
        pos -= 1
        infile.seek(pos)
    return pos


def word_find(offsetf, left, right, word):
    """
    Attempt to find a word via bisection, returns index if successful
    else -1
    """
    # Invariant left, right and mid are after newline characters
    # Word must end in ENDCHAR for complete matching
    if word[-1:] != ENDCHAR:
        word += ENDCHAR
    mid = (left + right) / 2 - 1
    mid = prev_newline(offsetf, mid)
    mid += 1
    if mid <= left:
        offsetf.seek(mid)
        offsetf.readline()
        mid = offsetf.tell()
    if mid >= right:
        return -1
    pword = retrieve_partial_word(offsetf, mid)
    if pword == word:
        return mid
    if pword < word:
        return word_find(offsetf, mid, right, word)
    if pword > word:
        return word_find(offsetf, left, mid, word)

def corpus_search(word):
    """
    Execute a full corpus search for a given word, returns the word and offsets
    of every location if successful. Returns the empty string upon failure.
    """
    fname = "offsetdict.txt"
    fsize = stat(fname).st_size
    offsetfile = open(fname, "r")

    corpus_dict_file = open("corpus_dict.txt")

    word_idx = word_find(offsetfile, 0, 
                            prev_newline(offsetfile, fsize) + 1, word)
    if word_idx == -1:
        return ''

    return corpus_extraction(offsetfile, word_idx, corpus_dict_file)

if __name__ == "__main__":
    # Search examples
    
    # Successes on Beowulf
    print corpus_search('be')
    print corpus_search('beowulf')
    # Fails on Beowulf
    print corpus_search('abracadabra')
