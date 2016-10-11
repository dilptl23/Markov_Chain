import random
"""will hold all nodes in the graph"""
class Graph(object):
    def __init__(self):
        self.g = {}

    def insertEdge(self, prevWord, word):
        if prevWord is None:
            if word in self.g.keys():
                return
            self.g[word] = {}
            return

        if prevWord in self.g.keys():
            if word in self.g[prevWord].keys():
                self.g[prevWord][word] += 1
            else:
                self.g[prevWord].update({word: 1})
        else:
            self.g[prevWord] = {word: 1}


    """looks at edge weight coming from prevWord and randomlly chooses word according to probabilities"""
    def getNextToken(self, prevWord):
        sum = 0
        if prevWord in self.g.keys():
            for key in self.g[prevWord]:
                sum += self.g[prevWord][key]
            #has no edges
            if sum == 0:
                return self.pickRandom()
            rand = random.randint(1, sum)
            for key in self.g[prevWord]:
                rand -= self.g[prevWord][key]
                if rand <= 0:
                    return key
        else:
            """if node has no edges going out from it"""
            return None

    def pickRandom(self):
        #return random.choice(self.tokens)
        return random.choice(list(self.g.keys()))


"""Decided not to have a node class and just create a huge dictionary in graph class"""
"""will hold value of node, all adjacent nodes and their edge weights
class Node(object):"""