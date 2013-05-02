# Python Maze Generator
# Joseph Vaughan
# joe@vghn.net

import pygame, sys, random
from pygame.locals import *
from collections import deque

# Sizes of things!
ROWS, COLS = 20, 25
CELL_SIZE = 20
SCRN_OFFSET = 50
SCRN_SIZE = WIDTH, HEIGHT = (2*SCRN_OFFSET)+(COLS*CELL_SIZE), (2*SCRN_OFFSET)+(ROWS*CELL_SIZE)

# Active walls stored as an integer.
# Allows easy byte-math to toggle walls on and off.
# All walls on 0000 1111
# North and south walls on 0000 0101
NORTH = 1   # 0000 0001
EAST = 2    # 0000 0010 
SOUTH = 4   # 0000 0100
WEST = 8    # 0000 1000

# Colours in Hexadecimal.
WHITE = 0xFFFFFF
BLACK = 0x202020
RED = 0xFF0000
PALE_GREEN = 0x98FB98
GREEN = 0x00FF00
BLUE = 0x0000FF
ORANGE = 0xEE4400

clock = pygame.time.Clock()

class Node:
    """ 
    A Node in the Graph or a Cell in the maze.
    Contains which walls are up and a visited flag.
    """
    
    def __init__(self, y, x):
        self.walls = NORTH | SOUTH | EAST | WEST
        # Remove walls if on edge of maze grid.
        if x == 0:          self.walls = self.walls ^ WEST
        if x == COLS - 1:   self.walls = self.walls ^ EAST
        if y == 0:          self.walls = self.walls ^ NORTH
        if y == ROWS - 1:   self.walls = self.walls ^ SOUTH
        self.visited = False
        self.colour = WHITE
    
    def hasWall(self, wall):
        """ Returns True if the wall is up. """
        return self.walls & wall

def handleEvents():
    for event in pygame.event.get():
        if event.type == QUIT: 
            pygame.quit()
            sys.exit()

def drawScreen(scrn, nodes, maze_start=(0, 0), maze_end=(ROWS-1, COLS-1)):
    handleEvents()
    scrn.fill(WHITE)
    border = (SCRN_OFFSET, SCRN_OFFSET, COLS*CELL_SIZE+1, ROWS*CELL_SIZE+1)
    pygame.draw.rect(scrn, BLACK, border, 2)

    for i in range(ROWS):
        for j in range(COLS):
            ox = SCRN_OFFSET + j * CELL_SIZE
            oy = SCRN_OFFSET + i * CELL_SIZE

            node = nodes[i][j]

            # Representation of the cells on the screen only needs the left and
            # top walls. Prevents having to worry about cells sharing walls in
            # a visual manner.
            if node.hasWall(NORTH):
                pygame.draw.line(scrn, BLACK, (ox, oy), (ox+CELL_SIZE, oy), 2)
            if node.hasWall(WEST):
                pygame.draw.line(scrn, BLACK, (ox, oy), (ox, oy+CELL_SIZE), 2)

            # Fill in the cells depending on the current state.
            # 'Visited' cells will be shown in a pale green and will be changed
            # to a pure white cell when removed from the stack.
            # The 'current' cell will be shown in a pale orange colour.
            # The 'start' of the maze will be shown in a green colour.
            # The 'end' of the maze will be shown in a red colour.
            rect = (ox+2, oy+2, CELL_SIZE-2, CELL_SIZE-2)
            color = WHITE
            if node.visited:
                pygame.draw.rect(scrn, node.colour, rect)
            if (i, j) == maze_start:
                pygame.draw.rect(scrn, GREEN, rect)
            if (i, j) == maze_end:
                pygame.draw.rect(scrn, RED, rect)

    pygame.display.flip()
    clock.tick(30)

def DFSGenerator(screen, nodes):
    stack = deque()
    start = (0, 0)
    end = (ROWS-1, COLS-1)
    v = (0, 1)
    screen_info = (screen, start, end)
    l = 0
    depthFirstSearch(screen_info, nodes, v, l)
    drawScreen(screen, nodes, start, end)

def depthFirstSearch(screen_info, nodes, v, l):
    """ Recursive implementation of Depth-First-Search. """
    # Add the new node to the stack
    #stack.append(v)
    l += 1
    print "Entering recursion level %d" % l
    screen, start, end = screen_info
    
    # Handle the maze-specific node stuff.
    x, y = v
    node = nodes[y][x]
    print "At node X: %d, Y: %d" % v
    node.visited = True
    node.colour = ORANGE
    drawScreen(screen, nodes, start, end)
    node.colour = PALE_GREEN

    w = None
    directions = [0, 1, 2, 3]
    random.shuffle(directions)

    # Edge handling
    # Directions are randomised, iterate through each direction and check it's 
    # validity.
    # Valid directions are those which have a wall to knock down still and the 
    # next cell in that direction has not been visited.
    # Once a valid direction has been found, recurse through that direction.
    for direction in directions:
        print "Direction: %d" % direction
        if direction == 0 and node.hasWall(NORTH) and not nodes[y-1][x].visited:
            node.walls ^= NORTH
            nodes[y-1][x].walls ^= SOUTH
            w = (x, y-1)
        elif direction == 1 and node.hasWall(EAST) and not nodes[y][x+1].visited:
            node.walls ^= EAST
            nodes[y][x+1].walls ^= WEST
            w = (x+1, y)
        elif direction == 2 and node.hasWall(SOUTH) and not nodes[y+1][x].visited:
            node.walls ^= SOUTH
            nodes[y+1][x].walls ^= NORTH
            w = (x, y+1)
        elif direction == 3 and node.hasWall(WEST) and not nodes[y][x-1].visited:
            node.walls ^= WEST
            nodes[y][x-1].walls ^= EAST
            w = (x-1, y)

        if w is not None:
            depthFirstSearch(screen_info, nodes, w, l)
        else:
            # Dead end found
            # Could elimate dead-ends for more interesting mazes by knocking
            # down a random wall.
            #deadEndCount += 1
            pass


    # Backtrace colouring
    #node.colour = ORANGE
    #drawScreen(screen, nodes, start, end)
    node.colour = WHITE
    print "Exiting recursion level %d" % l

def main():
    # Basic setup
    pygame.init()
    scrn = pygame.display.set_mode(SCRN_SIZE)

    # Setup nodes. Remember X and Y reversed.
    nodes = [None] * ROWS
    for i in range(ROWS):
        nodes[i] = [None] * COLS
    for i in range(ROWS):
        for j in range(COLS):
            nodes[i][j] = Node(i, j)
    
    drawScreen(scrn, nodes)
    DFSGenerator(scrn, nodes)

    while True:
        handleEvents()
        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main()
