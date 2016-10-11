"""Final project: Random Writer than can save it's model in various
forms.

NOTE: This is a long file, however I strongly recommend you read the
whole thing. There is also 20 pts of extra credit if you want to
improve your grade or just do some extra coding.

In this project you will write a "random writer": a program that
builds a statistical model of some data and then outputs a stream of
data that is similar to the original but randomly generated. Here is
how we will do it: [The idea for this assignment is from an assignment
that Dr Calvin Lin uses for CS314H. He was nice enough to let me use
his text as a starting point to explain it.]

Imagine taking a book, such as Tom Sawyer, and determining the
probability with which each character occurs. You'd probably find that
spaces are the most common character, followed by the character "e",
etc. Given these probabilities, which we will call a Level 0 analysis,
you could randomly produce text that, while not resembling English,
would have the property that the characters would likely occur in the
same proportions as they do in Tom Sawyer. For example, here's what
you might produce:

  rla bsht eS ststofo hhfosdsdewno oe wee h .mr ae irii ela iad o r te
  ut mnyto onmalysnce, ifu en c fDwn oee

Now imagine doing a slightly more sophisticated analysis, a Level 1
analysis, that determines the probability with which each character
follows every other character. You would probably discover that "h"
follows "t" more frequently than "x" does, and you would probably
discover that a space follows a period more frequently than a comma
does.  With this new analysis, you could use the probabilities from
Tom Sawyer to randomly pick an initial character and then repeatedly
choose the next character based on the previous character and the
probabilities provided by the analysis. Your new text might look like
the following, which looks a bit more like English than the previous
example:

  "Shand tucthiney m?" le ollds mind Theybooue He, he s whit Pereg
  lenigabo Jodind alllld ashanthe ainofevids tre lin-p asto oun
  theanthadomoere

We can generalize these ideas to a Level k analysis that determines
the probability with which each character follows every possible
sequence of k characters. For example, a Level 5 analysis of Tom
Sawyer would show that "r" follows "Sawye" more frequently than any
other character. After a Level k analysis, you'd be able to produce
random text by always choosing the next character based on the
previous k characters -- which we will call the state -- and based on
the probabilities produced by your analysis.

For relatively small values of k (5-7), the randomly generated text
begins to take on many of the characteristics of the source text.
While it still will not produce legal English, you will be able to
tell that it was derived from Tom Sawyer instead of Harry Potter. As
the value of k increases, the text looks increasingly like English.
Here are some more examples:

Level 2:
  "Yess been." for gothin, Tome oso; ing, in to weliss of an'te cle -
  armit.  Paper a comeasione, and smomenty, fropech hinticer, sid, a
  was Tom, be such tied. He sis tred a youck to themen

Level 4:
  en themself, Mr. Welshman, but him awoke, the balmy shore.  I'll
  give him that he couple overy because in the slated snuffindeed
  structure's kind was rath.  She said that the wound the door a fever
  eyes that WITH him.

Level 6:
  people had eaten, leaving. Come - didn't stand it better judgment;
  His hands and bury it again, tramped herself! She'd never would
  be. He found her spite of anything the one was a prime feature
  sunset, and hit upon that of the forever.

Level 8:
  look-a-here - I told you before, Joe.  I've heard a pin drop.  The
  stillness was complete, how-ever, this is awful crime, beyond the
  village was sufficient.  He would be a good enough to get that
  night, Tom and Becky.

Level 10:
  you understanding that they don't come around in the cave should get
  the word "beauteous" was over-fondled, and that together" and
  decided that he might as we used to do - it's nobby fun. I'll learn
  you."

We can also generalize this idea to use words in place of characters
as the "tokens" of the model. In fact we can generalize this process
to work over any sequence of values of any type. The states are then
short sequences of values.

Formally, the model we are building here is called a Markov Chain. A
Markov chain is a directed graph where every node is a state and every
outgoing edge from a node is a possible token to find while in that
state. The edges have probabilities that define how likely it is to
follow that edge. The probability of all the edges leaving a node
should sum to 1.

With this graph we can generate output by picking a random starting
node and then picking an outgoing edge based on the probabilities,
outputting it's associated token, and repeating the process based on
the node at the other end of the edge.

More concretely you can think of being in a state represented by a
string "th". We would then look at the probability that each other
letter would follow "th". "e" is likely to be very common; "x" not so
much. If we generate the "e", we are in state "he" and we check
probabilities based on that state.

Feel free to discuss the Markov chain with one another or look it
up. However you should not discuss how to implement it or copy an
existing implementation.

"""

"""You will be turning in this assignment as a ZIP file, since you
will need to turn in 2 different modules.
"""
from graph import Graph
from enum import Enum
from urllib.request import urlopen
import pickle
import argparse
import sys
import tweepy
class Tokenization (Enum):
    word = "word"
    character = "character"
    byte = "byte"
    none = "none"

"""TODO: Create a Tokenization enum with values: word, character, byte,
none. Use the enumeration support in the standard library. The
tokenization modes have the following meanings:



word: Interpret the input as UTF-8 and split the input at any
  white-space characters and use the strings between the white-space
  as tokens. So "a b" would be ["a", "b"] as would "a\n b".

character: Interpret the input as UTF-8 and use the characters as
  tokens.

byte: Read the input as raw bytes and use individual bytes as the
  tokens.

none: Do not tokenize. The input must be an iterable.
"""

"""TODO: Create a module called graph that contains class(es) and code that
are used to represent and manipulate the Markov chain graph.

The API of that module is up to you, but call it graph so I can easily
find and view it.

"""

"""In implementing the algorithms required for this project you should
not focus too much on performance however you should make sure your
code can train on a large data set in a reasonable time. For instance,
a 6MB input file on level 4 should not take more than 10
seconds. Similarly you should be able to generate output quickly;
5,000 tokens per second or better. These should be easy to meet.

You can get some test input from http://www.gutenberg.org/ . You may
want to use the complete works of Shakespeare:
http://www.gutenberg.org/cache/epub/100/pg100.txt

"""

class RandomWriter(object):
    """A Markov chain based random data generator.
    """

    def __init__(self, level, tokenization=None):
        """Initialize a random writer.

        Args:
          level: The context length or "level" of model to build.
          tokenization: A value from Tokenization. This specifies how
            the data should be tokenized.

        The value given for tokenization will affect what types of
        data are supported.

        """
        self.g = Graph()
        self.level = level
        self.token = tokenization

    def generate(self):
        """Generate tokens using the model.

        Yield random tokens using the model. The generator should
        continue generating output indefinitely.

        It is possible for generation to get to a state that does not
        have any outgoing edges. You should handle this by selecting a
        new starting node at random and continuing.

        """
        prev = self.g.pickRandom()
        for l in list(prev):
            yield l
        while(True):
            token = self.g.getNextToken(prev)
            if token:
                yield token
                prev = tuple((list(prev))[1:]) + (token,)
            else:
                prev = self.g.pickRandom()
                for l in list(prev):
                    yield l


    def generate_file(self, filename, amount):
        """Write a file using the model.

        Args:
          filename: The name of the file to write output to.
          amount: The number of tokens to write.

        For character or byte tokens this should just output the
        tokens one after another. For any other type of token a space
        should be added between tokens. Use str to convert values to
        strings for printing.

        Do not duplicate any code from generate.

        Make sure to open the file in the appropriate mode.
        """
        #check if filename is actually a fileobject
        if hasattr(filename, "write"):
            target = filename
        else:
            target = open(filename, 'w')
        g = self.generate()
        for x in range(amount):
            target.write(str(next(g)))
            if self.token == Tokenization.word or self.token == Tokenization.none:
                target.write(" ")

        target.close()

    def save_pickle(self, filename_or_file_object):
        """Write this model out as a Python pickle.

        Args:
          filename_or_file_object: A filename or file object to write
            to. You need to support both.

        If the argument is a file object you can assume it is opened
        in binary mode.

        """
        if hasattr(filename_or_file_object, "write"):
            pickle.dump(self, filename_or_file_object)
        else:
            text_file = open(filename_or_file_object, "wb")
            pickle.dump(self, text_file)
            text_file.close()


    @classmethod
    def load_pickle(cls, filename_or_file_object):
        """Load a Python pickle and make sure it is in fact a model.

        Args:
          filename_or_file_object: A filename or file object to load
            from. You need to support both.
        Return:
          A new instance of RandomWriter which contains the loaded
          data.

        If the argument is a file object you can assume it is opened
        in binary mode.

        """


        if hasattr(filename_or_file_object, "read"):
            a = pickle.load(filename_or_file_object)
        else:
            some_file = open(filename_or_file_object, 'rb')
            a = pickle.load(some_file)
            some_file.close()
        """After getting the object from file, must check if it is in fact a RandomWriter"""
        if isinstance(a, RandomWriter):
            return RandomWriter(a.level, a.token)
        else:
            print("ERROR: Pickle is not a model of RandomWriter", file=sys.stderr)


    def train_url(self, url):
        """Compute the probabilities based on the data downloaded from url.

        Args:
          url: The URL to download. Support any URL supported by
            urllib.

        This method is only supported if the tokenization mode is not
        none.

        Do not duplicate any code from train_iterable.

        """
        if not hasattr(url, "read"):
            url = urlopen(url)
        s = url.read().decode('utf-8')
        if self.token == Tokenization.byte:
            s = bytes(s, 'utf-8')
        self.train_iterable(s)

    def train_iterable(self, data):
        """Compute the probabilities based on the data given.

        If the tokenization mode is none, data must be an iterable. If
        the tokenization mode is character or word, then data must be
        a string. Finally, if the tokenization mode is byte, then data
        must be a bytes. If the type is wrong raise TypeError.

        """
        if self.token == Tokenization.character:
            a = list(data)
        elif self.token == Tokenization.byte:
            if type(data) is not bytes:
                raise TypeError("Type of data must be bytes")
            a = list(data)
        elif self.token == Tokenization.word:
            a = data.split()
        else:
            try:
                iter(data)
            except TypeError:
                raise TypeError("Data is not iterable")
            else:
                a = list(data)

        prev = a[:self.level]
        for l in a[self.level:]:
            s = tuple(prev)
            self.g.insertEdge(s, l)
            prev.append(l)
            if prev:
                prev.pop(0)

    def generate_tweet(self, amount):
        """ Tweets tokens to twitter handle @dilan_tests

        :param amount: amount of tokens to be tweeted

        """
        auth = tweepy.OAuthHandler("wiGJHih11M67AievYJJQi1xyf", "64YaAr2pt0nHlut2fwZXff0mSqANznj"
                                                            "oLwGvVssrOfQpOFd38l")
        auth.set_access_token("712320668822478849-LcOQNGZkknaczubR005BurDKloUyVth", "0kTGo8Nsz89XCPcGpjP4kfNF5bznDYrI8N"
                                                                                "h86DYrTcdjO")
        api = tweepy.API(auth)
        g = self.generate()
        tweet = ""
        for x in range(0, amount):
            tweet += str(next(g))
            if self.token == Tokenization.word or self.token == Tokenization.none:
                tweet += " "
        api.update_status(tweet)
def main():
    #example of extra credit
    rw = RandomWriter(2, Tokenization.word)
    rw.train_iterable("Leicester City are Champions of England")
    #rw.generate_tweet(10)

    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--train", help="Used to parse data", action="store_true")
    group.add_argument("--generate", help="Generate an output file", action="store_true")

    parser.add_argument("--input", help="Url for training file or Pickle file to load model", type=str)
    parser.add_argument("--output", help="Output file to save model or to write random data to", type=str)

    parser.add_argument("--word", help="Use word Tokenization", action="store_true")
    parser.add_argument("--character", help="Use character Tokenization", action="store_true")
    parser.add_argument("--byte", help="Use byte Tokenization", action="store_true")
    parser.add_argument("--level", help="Specifies train level", type=int, default=1)
    parser.add_argument("--amount", help="Specifies number of tokens to output", type=int)



    args = parser.parse_args()

    if args.train:
        #word is default token and 1 is default level
        if args.level < 0:
            print("ERROR: Invalid argument or level. Level must be greater than or equal to 0", file=sys.stderr)
        if args.character:
            rw = RandomWriter(args.level, Tokenization.character)
        elif args.byte:
            rw = RandomWriter(args.level, Tokenization.byte)
        else:
            rw = RandomWriter(args.level, Tokenization.word)

        rw.train_url(args.input)
        if args.output:
            rw.save_pickle(args.output)
        else:
            sys.stdout.buffer.write(pickle.dumps(rw))
    elif args.generate:
        if args.word or args.character or args.byte or args.level != 1:
            print("ERROR: Invalid Command. word, character, byte, and level options cannot be used with generate",
                  file=sys.stderr)
        if args.amount:
            if args.input:
                rw = pickle.load(open(args.input, "rb"))
            else:
                rw = pickle.load(sys.stdin.buffer)
            #rw = pickle.load(args.input)
            if args.output:
                rw.generate_file(args.output, args.amount)
            else:
                rw.generate_file(sys.stdout, args.amount)
        else:
            print("ERROR: --amount option must be given to generate", file=sys.stderr)
    else:
        print("ERROR: Invalid Option", file=sys.stderr)

if __name__ == '__main__':
    main()

"""def main():
    rw = RandomWriter(3, Tokenization.word)
    rw.train_iterable("Leicester City are top of the league. Chat Shit get Banged.")
    rw.generate_file(sys.stdout.buffer, 20)
main()"""


"""Make this file into a script that can be called using the
following command-line arguments:

final.py [command] [options]
  Commands:
    --train       Train a model using the given input and save it to a pickle output file.
      --input url_for_training_file     The input file to train on (Default standard input)
      --output text_output_file         The output file to save the model to (Default standard output)
      --word                            Use word tokenization (Default)
      --character                       Use character tokenization
      --byte                            Use byte tokenization
      --level n                         Train for level n (Default 1)
   --generate     Generate an output file
      --input pickle_input_file           The input file to load the model from (Default standard input)
      --output generated_file           The output file to write the random data to (Default standard output)
      --amount n                        Generate n tokens of output (Required)

For example, I should be able to do the following on a Linux command line:
python3 final.py --train --input http://www.google.com --output google.model --word
python3 final.py --generate --input google.model --amount 100
[100 words generated like the google HTML]
python3 final.py --train --character --input file://input.file | python3 final.py --generate --amount 1024 --output output.file

Do not implement the command-line parsing by hand! Look up the
argparse and getopt and use one of them. Your choice.

Make sure that an error message is printed if invalid options or
commands are given.

Make sure this module can still be imported without executing like
this.

"""

"""EXTRA CREDIT: I will give 20 points extra credit (more than 1/2
letter grade in the class) to anyone who integrates this with twitter
and sets up a twitter bot which posts twitter messages ever so often
based on models derived from recent news stories (pick your favorite
news data source) at the time of the post. The text you scrap from the
news source should be just Unicode text without any random HTML
embedded in it. So you will need to extract it carefully or pick your
source carefully. Make sure the text is generated with a high enough
level to produce text that looks like English. Also try word mode and
see if it makes the output more fun. It should generate text that at
first glance could be confused for a news tag line.

This is not a joke, however it is pretty complicated. Mainly I think it
would be cool and very educational.

I will also give 6 points each for just having your script post to
Twitter or train from a news source. So if you get started and want to
bail you will still get something.

There are no requirements on the interface for these. Just make sure
you document it in the submission so I can try it. And if you do setup
posting please send me the Twitter handle of the bot so I can check
out what it has said (or better yet is still occationally saying).

"""

"""
Modules you will want to look at:
* re
* urllib
* argparse
* pickle
* http.client
* requests

You may use the requests if you like. I will make sure it is installed
on the testing machine.
"""

#  LocalWords:  tokenization google iterable
