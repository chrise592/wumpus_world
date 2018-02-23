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

def init_world():
    """Create instance of a wumpus world enviroment and provide the GUI"""
    x = 0

def populate_world():
    """Populate the wumpus world with a wumpus, gold, and pits"""
    x = 0

def main():
    init_world()
    populate_world()
    while(True):
        # in your inner loop use it thus (just an example, I would probably use a named tuple)
        percept = [None, None, None, None, None]
        wwagent.update(percept) # update the agent with the current percept
        action = wwagent.action() # get the next action to take from the agent

main()
