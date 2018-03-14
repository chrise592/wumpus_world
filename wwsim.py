"""Implement a system to populate valid random wumpus worlds
and simulate an agent's interacton.

Provides a graphical user interface (GUI) using Tkinter to
show the current state of the simulated environment, including
the relevant status of pits, wumpus, gold, and agent in iconic
form.

Imports the wwagent module where the basic loop of this program
is to obtain the current precept sequence and pass it to the agent
as a tuple in a function call. Then it calls the agent action function
to get the next action.

# Written for: ECE 4524 - Spring 2018
# Author: Chris Evers
# Last updated: 23 February 2018
"""

# import the wwagent
import wwagent

import os
import sys
import random
import Tkinter as tk


class EnvGUI(tk.Tk, object):
    def __init__(self, env, title = 'Wumpus World', cellwidth=200, n=4):
        # Initialize window
        self.root = super(EnvGUI, self).__init__()
        self.title(title)
        self.cellwidth = cellwidth
        self.n = n

        # Create components
        self.canvas = EnvCanvas(self, env, cellwidth, n)
        self.toolbar = EnvToolbar(self, env, self.canvas)
        for w in [self.canvas, self.toolbar]:
            w.pack(side="bottom", fill="x", padx="3", pady="3")

        self.wumpus = tk.PhotoImage(file='wumpus.gif')
        self.gold = tk.PhotoImage(file='gold.gif')
        self.pit = tk.PhotoImage(file='pit.gif')
        self.explorer = tk.PhotoImage(file='explorer.gif')
        '''
        # Draw icons
        self.canvas.create_image(1*cellwidth-36, 2*cellwidth-36, image=self.wumpus, anchor=tk.SE)
        self.canvas.create_image(2*cellwidth-36, 2*cellwidth-36, image=self.gold, anchor=tk.SE)
        self.canvas.create_image(1*cellwidth-36, 4*cellwidth-36, image=self.explorer, anchor=tk.SE)
        self.canvas.create_image(3*cellwidth-36, 2*cellwidth-36, image=self.pit, anchor=tk.SE)
        self.canvas.create_image(3*cellwidth-36, 4*cellwidth-36, image=self.pit, anchor=tk.SE)
        '''
    def thing_added(self, thing, loc):
        y_loc = {1:4, 2:3, 3:2, 4:1}
        if isinstance(thing, Wumpus):
            self.canvas.create_image(loc[0]*self.cellwidth-36, y_loc[loc[1]]*self.cellwidth-36, image=self.wumpus, anchor=tk.SE)
        if isinstance(thing, Gold):
            self.canvas.create_image(loc[0]*self.cellwidth-36, y_loc[loc[1]]*self.cellwidth-36, image=self.gold, anchor=tk.SE)
        if isinstance(thing, Explorer):
            self.canvas.create_image(loc[0]*self.cellwidth-36, y_loc[loc[1]]*self.cellwidth-36, image=self.explorer, anchor=tk.SE)
        if isinstance(thing, Pit):
            self.canvas.create_image(loc[0]*self.cellwidth-36, y_loc[loc[1]]*self.cellwidth-36, image=self.pit, anchor=tk.SE)

        #tk.mainloop()

class EnvToolbar(tk.Frame, object):
    def __init__(self, parent, env, canvas):
        super(EnvToolbar, self).__init__(parent, relief='raised', bd=2)

        # Initialize instance variables
        self.env = env
        self.canvas = canvas
        self.running = False
        self.speed = 1.0

        # Create buttons and other controls
        for txt, cmd in [('New Simulation', self.new),
                         ('Time-Step >', self.step)]:
            tk.Button(self, text=txt, command=cmd).pack(side='left')

    def new(self):
        print 'new simulation'
        self.canvas.delete("all")
        self.canvas.draw_cells()
        self.env.clear_world()
        self.env.init_world(self.env.agent_program)

    def step(self):
        print 'step'


class EnvCanvas(tk.Canvas, object):

    def __init__(self, parent, env, cellwidth, n):
        # Initialize canvas
        super(EnvCanvas, self).__init__(parent, bg="white", height=n*cellwidth, width=n*cellwidth)
        self.env = env
        self.cellwidth = cellwidth
        self.n = n
        self.draw_cells()

    def draw_cells(self):
        # Draw cell borders 6x6
        for x in range(self.n):
            self.create_line(x*self.cellwidth, 0, x*self.cellwidth, self.n*self.cellwidth)
        for y in range(self.n):
            self.create_line(0, y*self.cellwidth, self.n*self.cellwidth, y*self.cellwidth)


#_________________________________________________________________________
# The Wumpus World


class Thing:
    """This represents any physical object that can appear in the Wumpus World.
    Each thing cn have a .__name__ slot (used for output only)."""
    def __repr__(self):
        return '<%s>' % getattr(self, '__name__', self.__class__.__name__)

class Percept:
    """This represents any physical object that can appear in the Wumpus World.
    Each thing cn have a .__name__ slot (used for output only)."""
    def __repr__(self):
        return '<%s>' % getattr(self, '__name__', self.__class__.__name__)

class Explorer(Thing):
    def __init__(self, program):
        self.is_alive = True
        self.holding = []
        self.performance = 0
        self.direction = 'right'
        self.program = program

    def can_grab(self, thing):
        """Explorer can only grab gold"""
        return thing.__class__ == Gold

    def display(self, canvas, x, y):
        self.explorer = tk.PhotoImage(file='explorer.gif')
        canvas.create_image(x, y, image=self.explorer, anchor=tk.SE)

class Gold(Thing):
    """This is gold"""
    pass

class Wumpus(Thing):
    """This is a wumpus"""
    pass

class Pit(Thing):
    """This is a pit"""
    pass

class Arrow(Thing):
    """This is an arrow"""
    pass

class Stench(Percept):
    """This is a stench percept"""
    pass

class Breeze(Percept):
    """This is a breeze percept"""
    pass

class Glitter(Percept):
    """This is a glitter percept"""
    pass

class Bump(Percept):
    """This is a bump percept"""
    pass

class Scream(Percept):
    """This is a scream percept"""
    pass


class WumpusEnvironment:
    """This class represents the Wumpus environment"""
    width = 4
    height = 4
    pit_probability = 0.2  # Probability to spawn a pit in a location. (From Chapter 7.2)

    def __init__(self, agent_program):
        """Room should be 4x4 grid of rooms."""
        self.things = []
        self.agents = []
        self.observer = None
        self.agent_program = agent_program
        self.x_start, self.y_start = (1, 1)
        self.x_end, self.y_end = (self.width, self.height)

    def init_world(self, program):
        """Spawn items in the world based on probabilities from the book"""

        # Pits
        for x in range(self.x_start+1, self.x_end+1):
            for y in range(self.y_start+1, self.y_end+1):
                if random.random() < self.pit_probability:
                    self.add_thing(Pit(), (x, y))
                    self.add_thing(Breeze(), (x-1, y))
                    self.add_thing(Breeze(), (x, y-1))
                    self.add_thing(Breeze(), (x+1, y))
                    self.add_thing(Breeze(), (x, y+1))

        # Wumpus
        w_x, w_y = self.random_location()
        self.add_thing(Wumpus(), (w_x, w_y))
        self.add_thing(Stench(), (w_x-1, w_y))
        self.add_thing(Stench(), (w_x+1, w_y))
        self.add_thing(Stench(), (w_x, w_y-1))
        self.add_thing(Stench(), (w_x, w_y+1))

        # Gold
        g_x, g_y = self.random_location()
        self.add_thing(Gold(), (g_x, g_y))
        self.add_thing(Glitter(), (g_x, g_y))

        # Agent
        self.add_thing(Explorer(program), (1, 1))

    def add_thing(self, thing, location):
        """Add a thing to the Wumpus World, setting its location."""
        thing.location = location
        self.things.append(thing)
        print thing, ' added to ', location
        self.observer.thing_added(thing, location)

    def clear_world(self):
        for x in range(self.x_start, self.x_end+1):
            for y in range(self.y_start, self.y_end+1):
                things = self.list_things_at((x, y))
                for thing in things:
                    self.things.remove(thing)

    def get_world(self):
        """Returns the items in the world"""
        result = []
        for y in range(self.y_start, self.y_end+1):
            row = []
            for x in range(self.x_start, self.x_end+1):
                row.append(self.list_things_at((x, y)))
            result.append(row)
        return result

    def random_location(self):
        """Returns a random location within the walls, excluding position (1, 1)
        and positions that already contain a thing."""
        location = (random.randint(self.x_start, self.x_end),
                    random.randint(self.y_start, self.y_end))
        while location == (1, 1) or self.list_things_at(location) != []:
            location = (random.randint(self.x_start, self.x_end),
                        random.randint(self.y_start, self.y_end))
        return location

    def list_things_at(self, location):
        """Return all things exactly at a given location."""
        return [thing for thing in self.things
                if thing.location == location]


def agent_program(percepts):
    """This function takes in a list of percepts and return an action.
    It uses the update(percepts) and action() functions from the
    wwagent module."""
    wwagent.update(percepts)
    return wwagent.action()

def main():
    while(True):
        # in your inner loop use it thus (just an example, I would probably use a named tuple)
        percept = (None, None, None, None, None)
        wwagent.update(percept) # update the agent with the current percept
        action = wwagent.action() # get the next action to take from the agent

env = WumpusEnvironment(agent_program)
env.observer = EnvGUI(env)
