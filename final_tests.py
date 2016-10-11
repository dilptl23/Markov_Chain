from contextlib import contextmanager
import tempfile
import os
import unittest
import itertools
import re
import sys
from pathlib import Path

import final

# You may find some of the functions or code here useful in either
# your tests or your implementation. Feel free to use it.

@contextmanager
def nonexistant_filename(suffix=""):
    with tempfile.NamedTemporaryFile(mode="w", suffix=suffix, delete=False) as fi:
        filename = fi.name
    os.remove(filename)
    try:
        yield filename
    finally:
        try:
            os.remove(filename)
        except FileNotFoundError:
            pass

@contextmanager
def filled_filename(content, suffix=""):
    with tempfile.NamedTemporaryFile(mode="w", suffix=suffix, delete=False) as fi:
        fi.write(content)
        filename = fi.name
    try:
        yield filename
    finally:
        os.remove(filename)

def windowed(iterable, size):
    window = list()
    for v in iterable:
        if len(window) < size:
            window.append(v)
        else:
            window.pop(0)
            window.append(v)
        if len(window) == size:
            yield window

def contains_sequence(iteratable, sequence, length=10000, require_length=True, times=1):
    sequence = list(sequence)
    count = 0
    found = 0
    for window in itertools.islice(windowed(iteratable, len(sequence)), length):
        #print(window, count, sequence)
        count += 1
        if window == sequence:
            found += 1
            if found >= times:
                return True
    #if count < length-1 and require_length:
    #    raise AssertionError("Iterable did not contain enought values for check. Ran out at {}; needed {}.".format(count, length))
    return False


class RandomWriterTests(unittest.TestCase):
    """Some simple tests for RandomWriter.

    This is not an exhaustive test suite. You should write more.

    The entire set of tests should not take more than 2-3 seconds to
    run. My implementation takes 1.1s.
    """
    DEFAULT_LENGTH = 10090

    def assertContainsSequence(self, iteratable, sequence, length=None, times=1):
        length = length or self.DEFAULT_LENGTH
        lst = list(itertools.islice(iteratable, length + len(sequence)*2))
        if not contains_sequence(lst, sequence, length, times=times):
            self.fail("The given iterable must contain the sequence: {} at least {} times "
                      "(in the first {} elements)\nSample: {}".format(list(sequence), times, length, ", ".join(repr(x) for x in lst[:1000])))

    def assertNotContainsSequence(self, iteratable, sequence, length=None):
        length = length or self.DEFAULT_LENGTH
        lst = list(itertools.islice(iteratable, length + len(sequence)*2))
        if contains_sequence(lst, sequence, length):
            self.fail("The given iterable must NOT contain the sequence: {} "
                      "(in the first {} elements)\nSample: {}".format(list(sequence), length, ", ".join(repr(x) for x in lst[:1000])))

    def test_numeric_sequence(self):
        rw = final.RandomWriter(2)
        rw.train_iterable((1,2,3,4,5,5,4,3,2,1))
        self.assertContainsSequence(rw.generate(), [3,4,5,5,4,3,2], times=10)
        self.assertNotContainsSequence(rw.generate(), [5,5,3])
        self.assertNotContainsSequence(rw.generate(), [1,2,5])

    def test_words(self):
        rw = final.RandomWriter(1, final.Tokenization.word)
        rw.train_iterable("the given iterable must contain the sequence the")
        #print(rw.g.g)
        self.assertContainsSequence(rw.generate(), "iterable must contain".split(" "), times=10)
        self.assertContainsSequence(rw.generate(), "the sequence".split(" "), times=200)
        self.assertNotContainsSequence(rw.generate(), "the the".split(" "))
        self.assertNotContainsSequence(rw.generate(), "the iterable".split(" "))

    def test_save_load_pickle(self):
        rw = final.RandomWriter(1, final.Tokenization.character)
        rw.train_iterable("abcaea")
        with nonexistant_filename() as fn:
            rw.save_pickle(fn)
            rw2 = final.RandomWriter.load_pickle(fn)
            self.assertContainsSequence(rw.generate(), "abc", times=100)
            self.assertContainsSequence(rw.generate(), "aeaeab", times=100)
            self.assertNotContainsSequence(rw.generate(), "ac")
            self.assertNotContainsSequence(rw.generate(), "aa")
            self.assertNotContainsSequence(rw.generate(), "ce")

    def test_generate_file1(self):
        rw = final.RandomWriter(1, final.Tokenization.character)
        rw.train_iterable("abcaea")
        with nonexistant_filename() as fn:
            rw.generate_file(fn, self.DEFAULT_LENGTH)
            with open(fn, "rt") as fi:
                content = fi.read()
            self.assertContainsSequence(content, "abc", times=100)
            self.assertContainsSequence(content, "aeaeab", times=100)
            self.assertNotContainsSequence(content, "ac")
            self.assertNotContainsSequence(content, "aa")
            self.assertNotContainsSequence(content, "ce")

    def test_generate_file_size(self):
        rw = final.RandomWriter(1, final.Tokenization.character)
        rw.train_iterable("abcaea")
        with nonexistant_filename() as fn:
            rw.generate_file(fn, self.DEFAULT_LENGTH)
            with open(fn, "rt") as fi:
                content = fi.read()
            self.assertGreaterEqual(len(content), self.DEFAULT_LENGTH)
            self.assertLessEqual(len(content), self.DEFAULT_LENGTH+2)

    def test_generate_file2(self):
        rw = final.RandomWriter(1, final.Tokenization.word)
        rw.train_iterable("a the word the")
        with nonexistant_filename() as fn:
            rw.generate_file(fn, self.DEFAULT_LENGTH)
            with open(fn, "rt") as fi:
                content = fi.read()
            self.assertContainsSequence(content, "the word", times=100)
            self.assertNotContainsSequence(content, "the a")

    def test_generate_file3(self):
        rw = final.RandomWriter(2, final.Tokenization.none)
        rw.train_iterable((1,2,3,4,5,5,4,3,2,1))
        with nonexistant_filename() as fn:
            rw.generate_file(fn, self.DEFAULT_LENGTH)
            with open(fn, "rt") as fi:
                content = fi.read()
            self.assertContainsSequence(content, "3 4 5 5 4 3 2", times=100)
            self.assertNotContainsSequence(content, "5 5 3")
            self.assertNotContainsSequence(content, "1 2 5")


    def test_numeric_sequence_in(self):
        rw = final.RandomWriter(2)
        rw.train_iterable((1,2,3,4,5,5,5,4,3,2,1,2,4,5))
        self.assertIsInstance(next(iter(rw.generate())), int)
        self.assertContainsSequence(rw.generate(), [3,4,5,5,4,3,2], times=10)
        self.assertContainsSequence(rw.generate(), [3,4,5,5,5,5,4,3,2])
        self.assertContainsSequence(rw.generate(), [5,5,5,5,5])
        self.assertContainsSequence(rw.generate(), [3,2,1,2,4,5,5,4])
        self.assertContainsSequence(rw.generate(), [3,2,1,2,3,4,5,5,4])

    def test_numeric_sequence_notin(self):
        rw = final.RandomWriter(2)
        rw.train_iterable((1,2,3,4,5,5,5,4,3,2,1,2,4,5))
        self.assertNotContainsSequence(rw.generate(), [5,5,3])
        self.assertNotContainsSequence(rw.generate(), [1,2,5])
        self.assertNotContainsSequence(rw.generate(), [4,2])
        self.assertNotContainsSequence(rw.generate(), ["5"])

    def test_generate_count(self):
        rw = final.RandomWriter(2, final.Tokenization.character)
        rw.train_iterable("What a piece of work is man! how noble in reason! how infinite in faculty! in form and moving how express and admirable! "
                          "in action how like an angel! in apprehension how like a god! the beauty of the world, the paragon of animals!")
        generated = len(list(itertools.islice(rw.generate(), 10000)))
        self.assertEqual(generated, 10000)

    def test_characters(self):
        rw = final.RandomWriter(2, final.Tokenization.character)
        #print("Test Characters Dictionairy")
        rw.train_iterable("What a piece of work is man! how noble in reason! how infinite in faculty! in form and moving how express and admirable! "
                          "in action how like an angel! in apprehension how like a god! the beauty of the world, the paragon of animals!")
        #print(rw.g.g)
        self.assertIsInstance(next(iter(rw.generate())), str)
        self.assertContainsSequence(rw.generate(), "worm")
        self.assertNotContainsSequence(rw.generate(), "mals ")

    def test_characters_level3(self):
        rw = final.RandomWriter(3, final.Tokenization.character)
        rw.train_iterable("What a piece of work is man! how noble in reason! how infinite in faculty! in form and moving how express and admirable! "
                          "in action how like an angel! in apprehension how like a god! the beauty of the world, the paragon of animals!")
        self.assertIsInstance(next(iter(rw.generate())), str)
        self.assertContainsSequence(rw.generate(), "n how n")
        self.assertNotContainsSequence(rw.generate(), "worm")
        self.assertNotContainsSequence(rw.generate(), "mals ")

    def test_bytes(self):
        rw = final.RandomWriter(2, final.Tokenization.byte)
        rw.train_iterable(b"What a piece of work is man! how noble in reason! how infinite in faculty! in form and moving how express and admirable! "
                          b"in action how like an angel! in apprehension how like a god! the beauty of the world, the paragon of animals!")
        self.assertTrue(isinstance(next(iter(rw.generate())), (int, bytes)))
        self.assertContainsSequence(rw.generate(), b"worm")
        self.assertNotContainsSequence(rw.generate(), b"mals ")


    def test_words2(self):
        rw = final.RandomWriter(2, final.Tokenization.word)
        rw.train_iterable("What a piece of work is man! how noble in reason! how infinite in faculty! in form and moving how express and admirable! "
                          "in action how like an angel! in apprehension how like a god! the beauty of the world, the paragon of animals!")
        self.assertIsInstance(next(iter(rw.generate())), str)
        self.assertContainsSequence(rw.generate(), "action how like a god!".split(" "), length=50000)
        self.assertContainsSequence(rw.generate(), "infinite in faculty!".split(" "), length=50000)
        self.assertNotContainsSequence(rw.generate(), "man angel".split(" "), length=50000)
        self.assertNotContainsSequence(rw.generate(), "infinite in reason".split(" "), length=50000)
        self.assertNotContainsSequence(rw.generate(), ("worm",))

    def test_train_url_characters(self):
        rw = final.RandomWriter(3, final.Tokenization.character)
        rw.train_url("http://www.singingwizard.org/stuff/pg24132.txt")
        self.assertContainsSequence(rw.generate(), "ad di", length=200000)

    def test_train_url_bytes(self):
        rw = final.RandomWriter(4, final.Tokenization.byte)
        rw.train_url("http://www.singingwizard.org/stuff/pg24132.txt")
        #print(rw.g.g)
        self.assertContainsSequence(rw.generate(), b"ad di", length=300000)

    def test_train_url_word(self):
        rw = final.RandomWriter(1, final.Tokenization.word)
        rw.train_url("http://www.singingwizard.org/stuff/pg24132.txt")
        self.assertContainsSequence(rw.generate(), "she had".split(), length=100000)

    def test_train_url_utf8(self):
        rw = final.RandomWriter(5, final.Tokenization.character)
        rw.train_url("http://www.singingwizard.org/stuff/utf8test.txt")
        self.assertContainsSequence(rw.generate(), "ajtób", length=100000)


if __name__ == "__main__":
    unittest.main()