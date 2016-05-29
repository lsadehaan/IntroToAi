from __future__ import print_function
import heapq

__author__ = 'adriaan.dehaan'

import string
import os
from random import *

"""
Taken from http://stackoverflow.com/questions/407734/a-generic-priority-queue-for-python
Thanks go out to Eli Bendersky - http://stackoverflow.com/users/8206/eli-bendersky
Modified to use the State variable for the dictionary key and added a replace method and hacked it a bit more...
"""
class PriorityQueueSet(object):

    """
    Combined priority queue and set data structure.

    Acts like a priority queue, except that its items are guaranteed to be
    unique. Provides O(1) membership test, O(log N) insertion and O(log N)
    removal of the smallest item.

    Important: the items of this data structure must be both comparable and
    hashable (i.e. must implement __cmp__ and __hash__). This is true of
    Python's built-in objects, but you should implement those methods if you
    want to use the data structure for custom objects.
    """

    def __init__(self, items=[]):
        """
        Create a new PriorityQueueSet.

        Arguments:
            items (list): An initial item list - it can be unsorted and
                non-unique. The data structure will be created in O(N).
        """
        self.set = dict((item.State, item) for item in items)
        self.heap = list(items)
        heapq.heapify(self.heap)

    def has_item(self, state):
        """Check if ``state`` item exists in the queue."""
        return state in self.set

    def get_item(self, state):
        """return the ``state`` item stored in the set."""
        return self.set[state]

    def pop_smallest(self):
        """Remove and return the smallest item from the queue."""
        smallest = heapq.heappop(self.heap)
        del self.set[smallest.State]
        return smallest

    def add(self, item):
        """Add ``item`` to the queue and the set if doesn't already exist."""
        if item.State not in self.set:
            self.set[item.State] = item
            heapq.heappush(self.heap, item)

    def replace(self, item):
        """Replace ``item`` in the queue and in the set."""
        self.set[item.State] = item
        self.heap = list(self.set.values())
        heapq.heapify(self.heap)

class PathNode(object):
    def __init__(self, parent, state, cost, ffunc):
        self.Parent = parent
        self.State = state
        self.Cost = cost
        self.FFunc = ffunc
        return

    def __cmp__(self, other):
        return cmp(self.FFunc(self), self.FFunc(other))

MaxX = 1024
class State(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    # this should be a little faster than normal hashing, just need to make sure MaxX is always creater than x
    def __hash__(self):
        return self.x + self.y*MaxX

    def __eq__(self, other):
        return (self.x == other.x) & (self.y == other.y)

class AStarGraph(object):
    def __init__(self, costMap, startState, endState):
        self.CostMap = costMap
        self.dimX = len(self.CostMap)
        self.dimY = len(self.CostMap[0])
        self.PathStart = PathNode(None, startState, 0, self.f)
        self.End = endState

        self.Frontier = PriorityQueueSet([self.PathStart])
        self.Explored = dict()

    def f(self, path):
        return self.g(path) + self.h(path)

    def g(self, path):
        return path.Cost

    # The sum of the horisontal and vertical distances should be the perfect candidate for the heuristic
    def h(self, path):
        distanceX = abs(path.State.x - self.End.x)
        distanceY = abs(path.State.y - self.End.y)
        return distanceX + distanceY

    def takeNextNode(self):
        return self.Frontier.pop_smallest()

    def expandPathNode(self, path):
        # Success!
        if path.State == self.End:
            return path

        self.Explored[path.State] = path

        # Add all the options
        for option in self.getOptions(path.State):
            optionPath = PathNode(path, option, path.Cost+self.CostMap[option.x][option.y], self.f)

            if self.Frontier.has_item(option):
                if optionPath < self.Frontier.get_item(option):
                    self.Frontier.replace(optionPath)
                continue

            if (option in self.Explored):
                if optionPath < self.Explored[option]:
                    del self.Explored[option]
                    self.Frontier.add(optionPath)
                continue

            self.Frontier.add(optionPath)


    def getOptions(self, state):
        options = list()
        if (state.x+1 < self.dimX) and (self.CostMap[state.x+1][state.y] != 0):
            options.append(State(state.x+1, state.y))
        if (state.x-1 >= 0) and (self.CostMap[state.x-1][state.y] != 0):
            options.append(State(state.x-1, state.y))
        if (state.y+1 < self.dimY) and (self.CostMap[state.x][state.y+1] != 0):
            options.append(State(state.x, state.y+1))
        if (state.y-1 >= 0) and (self.CostMap[state.x][state.y-1] != 0):
            options.append(State(state.x, state.y-1))
        return options

    def iterate(self):
        return self.expandPathNode(self.takeNextNode())

    def draw(self):
        for j in range(self.dimY):
            print()
            for i in range(self.dimX):
                value = (str(self.CostMap[i][j]) + "   ")[:3]
                state = State(i, j)
                if self.PathStart.State == state:
                    print("\033[1;30;47m" + value, end="\033[m ")
                elif self.End == state:
                    print("\033[1;37;41m" + value, end="\033[m ")
                elif self.Frontier.has_item(state):
                    print("\033[1;37;31m" + value, end="\033[m ")
                elif state in self.Explored:
                    print("\033[1;37;32m" + value, end="\033[m ")
                else:
                    print(value, end=" ")

            print("   ||   ", end="")

            for i in range(self.dimX):
                value = (str(self.CostMap[i][j]) + "   ")[:3]
                state = State(i, j)
                if self.PathStart.State == state:
                    print("\033[1;30;47m" + value, end="\033[m ")
                elif self.End == state:
                    print("\033[1;37;41m" + value, end="\033[m ")
                elif self.Frontier.has_item(state):
                    pathNode = self.Frontier.get_item(state)
                    totalCost = pathNode.FFunc(pathNode)
                    value = (str(totalCost)+ "   ")[:3]
                    print("\033[1;37;31m" + value, end="\033[m ")
                elif state in self.Explored:
                    pathNode = self.Explored[state]
                    totalCost = pathNode.FFunc(pathNode)
                    value = (str(totalCost)+ "   ")[:3]
                    print("\033[1;37;32m" + value, end="\033[m ")
                else:
                    print(value, end=" ")

        print()

    def drawPath(self, path):
        pathNodes = dict()

        while (path.Parent is not None):
            pathNodes[path.State] = path
            path = path.Parent
        pathNodes[path.State] = path

        for j in range(self.dimY):
            print()
            for i in range(self.dimX):
                value = (str(self.CostMap[i][j]) + "   ")[:3]
                state = State(i, j)
                if state in pathNodes:
                    print("\033[1;30;47m" + value, end="\033[m ")
                elif self.PathStart.State == state:
                    print("\033[1;30;47m" + value, end="\033[m ")
                elif self.End == state:
                    print("\033[1;37;41m" + value, end="\033[m ")
                elif self.Frontier.has_item(state):
                    print("\033[1;37;31m" + value, end="\033[m ")
                elif state in self.Explored:
                    print("\033[1;37;32m" + value, end="\033[m ")
                else:
                    print(value, end=" ")

            print("   ||   ", end="")

            for i in range(self.dimX):
                value = (str(self.CostMap[i][j]) + "   ")[:3]
                state = State(i, j)
                if state in pathNodes:
                    pathNode = pathNodes[state]
                    totalCost = pathNode.Cost
                    value = (str(totalCost)+ "   ")[:3]
                    print("\033[1;30;47m" + value, end="\033[m ")
                elif self.PathStart.State == state:
                    print("\033[1;30;47m" + value, end="\033[m ")
                elif self.End == state:
                    print("\033[1;37;41m" + value, end="\033[m ")
                elif self.Frontier.has_item(state):
                    pathNode = self.Frontier.get_item(state)
                    totalCost = pathNode.Cost
                    value = (str(totalCost)+ "   ")[:3]
                    print("\033[1;37;31m" + value, end="\033[m ")
                elif state in self.Explored:
                    pathNode = self.Explored[state]
                    totalCost = pathNode.Cost
                    value = (str(totalCost)+ "   ")[:3]
                    print("\033[1;37;32m" + value, end="\033[m ")
                else:
                    print(value, end=" ")

        print()

print("Starting costs map creation")

xLimit = 20
yLimit = 14
rand = Random()

# You can play with the costs table to create interesting terrain for the algorithm to traverse.
# A "boulder" thats in the way:
#costs = [[(500 / (10 + ((10-col)*(10-col) + (7-row)*(7-row) )) ) for col in range(yLimit)] for row in range(xLimit)]
# A vertical gradient:
#costs = [[row for col in range(yLimit)] for row in range(xLimit)]
# A horizontal gradient:
#costs = [[col for col in range(yLimit)] for row in range(xLimit)]
# random: Increasing the range of random values (in relation to size of the distance measure used for the cost function)
costs = [[rand.randint(1, 2) for col in range(yLimit)] for row in range(xLimit)]
# uniform:
#costs = [[1 for col in range(yLimit)] for row in range(xLimit)]

print("Costs map created, creating graphing class")

gr = AStarGraph(costs, State(2, 3), State(18, 12))

print("graph created")
gr.draw()
i = 0

res = gr.iterate()
while (res is None):
    i += 1
    print("Iteration " + str(i))
    gr.draw()
    res = gr.iterate()

gr.drawPath(res)
