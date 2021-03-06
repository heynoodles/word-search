"""Word Search solver"""

from itertools import izip, ifilter
import re
import sys


class Grid(object):
    """A grid of letters together with methods for finding words in the grid."""

    def __init__(self, grid):
        self.rows = grid
        self.num_rows = len(grid)
        self.num_cols = len(grid[0]) if grid else 0


    def find_words(self, words, wrap):
        """Attempt to find all the input words in the grid.

        Args:
          words: a list of words to search for in the grid
          wrap: boolean indicating whether words can wrap around the grid
        Returns:
          a list where each element is the start and end coordinates where
          the word at that index is found. If the word isn't found then the
          element is None
        """
        return [self.find_word(w, wrap) for w in words]
        

    def find_word(self, word, wrap):
        """Find `word` in the grid.

        Args:
          word: the word to look for
          wrap: bool indicating whether a word can wrap around the grid
        Returns:
          two tuples indicating the start and end position 
        """

        if not word:
            return None

        for m, n in self.positions_that_have_letter(word[0]):
            for span in self.spans((m, n), len(word), wrap):
                if self.word_at_indices(span) == word:
                    return span[0], span[-1]
        return None

    def __getitem__(self, (m, n)):
        """Return the letter at the mth row and nth column."""
        return self.rows[m][n]

    def __len__(self):
        """Return the number of letter slots in the grid."""
        return self.num_rows * self.num_cols

    def __iter__(self):
        """Return a generator of each letter in the grid."""
        for row in self.rows:
            for item in row:
                yield item

    def __str__(self):
        return '\n'.join(''.join('*' if item is None else item for item in row) 
                         for row in self.rows)

    @property
    def index_letter_pairs(self):
        """Return a generator of ((m, n), letter) pairs.""" 
        for m, row in enumerate(self.rows):
            for n, letter in enumerate(row):
                yield ((m, n), letter)

    def letters_at_indices(self, indices):
        """Return the list of chars at these indices."""
        return (self[idx] for idx in indices)


    def word_at_indices(self, indices):
        """Return the word (a str) at these indices."""
        return ''.join(self.letters_at_indices(indices))


    def positions_that_have_letter(self, letter):
        """Return a generator of (m, n) pairs where self[(m, n)] is the letter.
        """
        return ((m, n) for ((m, n), let) in self.index_letter_pairs
                       if let == letter)


    def spans(self, start_index, length, wrap):
        """Return all the spans of length `length` beginning at `start_index`.

        Args:
          start_index: an (m, n) pair representing a position in the grid
          length: the length of each span
          wrap: a boolean indicating whether a span can wrap around the grid
        Returns:
          a list of spans where each span is like [(0, 0), (0, 1), (0, 2)]
        """
        return ifilter(None, 
            (self._up_span(start_index, length, wrap),
             self._down_span(start_index, length, wrap),
             self._right_span(start_index, length, wrap),
             self._left_span(start_index, length, wrap),
             self._left_down_span(start_index, length, wrap),
             self._left_up_span(start_index, length, wrap),
             self._right_down_span(start_index, length, wrap),
             self._right_up_span(start_index, length, wrap)))

    def _up_span(self, (m, n), length, wrap):
        """Return a generator of length indices starting at (m, n) or None.

        The indices go from bottom to top and can wrap around the grid if wrap
        is True. 
        """

        if length > self.num_rows or (not wrap and m - length + 1 < 0):
            return None

        return [(mm % self.num_rows, n) for mm in xrange(m, m - length, -1)]


    def _down_span(self, (m, n), length, wrap):
        """Return a generator of length indices starting at (m, n) or None.

        The indices go from top to bottom and can wrap around the grid if wrap
        is True. 
        """

        if length > self.num_rows or (not wrap and m + length > self.num_rows):
            return None

        return [(mm % self.num_rows, n) for mm in xrange(m, m + length)]


    def _right_span(self, (m, n), length, wrap):
        """Return a generator of length indices starting at (m, n) or None.

        The indices go from left to right and can wrap around the grid if wrap
        is True. 
        """
        if length > self.num_cols or (not wrap and n + length > self.num_cols):
            return None

        return [(m, nn % self.num_cols) for nn in xrange(n, n + length)]


    def _left_span(self, (m, n), length, wrap):
        """Return a generator of length indices starting at (m, n) or None.

        The indices go from right to left and can wrap around the grid if wrap
        is True.
        """

        if length > self.num_cols or (not wrap and n - length + 1 < 0):
            return None

        return [(m, nn % self.num_cols) for nn in xrange(n, n - length, -1)]



    def _left_down_span(self, (m, n), length, wrap):
        """Return a generator of length indices starting at (m, n) or None.

        The indices go diagonally from the top right to the bottom left and can
        wrap around the grid if wrap is True.
        """

        if length > self.num_cols or length > self.num_rows or \
           (not wrap and (n - length + 1 < 0 or m + length > self.num_rows)):
            return None

        return [(mm % self.num_rows, nn % self.num_cols) 
                for (mm, nn) in izip(xrange(m, m + length), 
                                     xrange(n, n - length, -1))]


    def _left_up_span(self, (m, n), length, wrap):
        """Return a generator of length indices starting at (m, n) or None.

        The indices go diagonally from the bottom right to the top left and can
        wrap around the grid if wrap is True.
        """

        if length > self.num_cols or length > self.num_rows or \
           (not wrap and (n - length + 1 < 0 or m - length + 1 < 0)):
            return None
        
        return [(mm % self.num_rows, nn % self.num_cols) 
                for (mm, nn) in izip(xrange(m, m - length, -1), 
                                     xrange(n, n - length, -1))]

 
    def _right_up_span(self, (m, n), length, wrap):
        """Return a generator of length indices starting at (m, n) or None.

        The indices go diagonally from the bottom left to the top right and can
        wrap around the grid if wrap is True.
        """

        if length > self.num_cols or length > self.num_rows or \
           (not wrap and (n + length > self.num_cols or m - length + 1 < 0)):
            return None
        
        return [(mm % self.num_rows, nn % self.num_cols) 
                for (mm, nn) in izip(xrange(m, m - length, -1), 
                                     xrange(n, n + length))]
        

    def _right_down_span(self, (m, n), length, wrap):
        """Return a generator of length indices starting at (m, n) or None.

        The indices go diagonally from the top left to bottom right and can
        wrap around the grid if wrap is True.
        """

        if length > self.num_cols or length > self.num_rows or \
           (not wrap and (n + length > self.num_cols or 
                          m + length > self.num_rows)):
            return None
        
        return [(mm % self.num_rows, nn % self.num_cols) 
                for (mm, nn) in izip(xrange(m, m + length), 
                                     xrange(n, n + length))]





class InputParseError(Exception):
    """Raised for malformed input."""

def load_from_str_input(input_str):
    """Load a grid, word list, and +/- wrap from an input string."""
    pat = re.compile(r"""
        \s*
        (?P<rows>\d+)
        [ ]
        (?P<cols>\d+)
        (?P<grid>.*?)
        (?P<wrap>WRAP|NO_WRAP)
        \s+
        (?P<num_words>\d+)
        \s
        (?P<words>.*)
    """, re.VERBOSE|re.DOTALL)

    m = pat.match(input_str)
    if m is None:
        raise InputParseError('Failed to parse input string')

    data = m.groupdict()

    grid = Grid([list(row.strip()) for row in data['grid'].split('\n')
                                   if row.strip()])

    if int(data['rows']) != grid.num_rows or int(data['cols']) != grid.num_cols:
        raise InputParseError("Number of rows or colums doesn't match data")

    words = [line.strip() for line in data['words'].split('\n') if line.strip()]
    if len(words) != int(data['num_words']):
        raise InputParseError("Number of words doesn't match data")

    if data['wrap'] == 'WRAP':
        wrap = True
    elif data['wrap'] == 'NO_WRAP':
        wrap = False
    else:
        raise InputParseError('Wrap instruction must be "WRAP" OR "NO_WRAP"')


    return grid, words, wrap




def main(args):
    """Main function that finds words in input file.

    args[0] is the path to a file containing the grid and the list of words to
    be found.
    """

    if not args:
        msg = 'First argument must be path to file containing instructions'
        print >> sys.stderr, msg

    with open(args[0], 'r') as f:
        text = f.read()

    grid, words, wrap = load_from_str_input(text)
    for position in grid.find_words(words, wrap):
        if position is None:
            print 'NOT FOUND'
        else:
            ((m1, n1), (m2, n2)) = position
            print '(%d,%d) (%d,%d)' % (m1, n1, m2, n2)
        print 

if __name__ == '__main__':
    main(sys.argv[1:])
