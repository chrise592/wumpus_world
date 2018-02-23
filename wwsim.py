# implement your simulator here

# import the wwagent
import wwagent

# in your inner loop use it thus (just an example, I would probably use a named tuple)
percept = [None, None, None, None, None]
wwagent.update(percept) # update the agent with the current percept
action = wwagent.action() # get the next action to take from the agent


