
GUIDE TO BUILDING AN AI FOR SOLVING A MAZE.
-------------------------------------------

This repository contains Python code for building an AI that can solve a maze, using q-learning (a type of reinforcement learning).

1) Maze-AI-grid.py - train the agent using q-learning to get through a maze. 
2) Maze-AI-grid-greedy.py - same as above, but with prizes scattered through the maze, and implementation of epsilon-greedy strategy.

The maze is a grid of cells, with blocks (blue), prizes (purple), and an end cell (pink). The agent starts off in the top left corner of the grid, and moves through the maze (shown by the white cell) until it has reached the end, or has gotten lost.

The agent gets rewards upon reaching each type of cell. For example, hitting a block or trying to move out of the maze result in negative rewards, while reaching a prize or the end of the maze result in positive rewards. 

We make a q-table which stores the q-value of each state-action pair. The states are the cells of the maze grid, and the actions are 'up', 'down', 'left', 'right'. The q-value is calculated using the Bellman Equation, which takes into account current and future rewards. 

The agent, upon reaching any cell, makes the decision of which direction to go in. The values of the q-table are updated as the agent explores its environment. We let the agent explore for a number of episodes (here, 300). After this, it has a good approximation of the elements of its environment as reflected in its q-table. It should then be able to solve the maze (reach the end cell) in the most efficient way!

The epsilon-greedy strategy is used to switch between exploration of the environment, and exploitation of the knowledge the agent has. By starting off with a high epsilon, the agent explores more of the environment at the beginning, rather than taking the known best path. Later, as it has gathered a lot of knowledge, it starts to take the optimal path. 



