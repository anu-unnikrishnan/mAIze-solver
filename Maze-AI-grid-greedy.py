import numpy as np
import random
from random import choices 
import matplotlib.pyplot as plt
import pandas as pd
import time
import os
os.system("clear")

#set values of alpha, gamma parameters 
alpha = 0.1 #or 0.2 works too 
gamma = 0.9

#place (n^2/4 - 1) blocks at random positions in the maze (denoted by '1')
def place_blocks(grid):
    numblocks = 0
    blockrowarr = []
    blockcolarr = []
    while numblocks < n**2/4:
        blockrow = random.randint(0, n-1) #random number between 0 and n-1
        blockcol = random.randint(0, n-1)
        if blockrow != 0 or blockcol != 0: #don't put a block at the starting position
            if blockrow != n-1 or blockcol != n-1: #don't put a block at the ending position 
                if grid[blockrow][blockcol] == 0: #if that cell isn't already occupied 
                    #check if two blocks are blocking the player from leaving the start pos, or getting to the exit
                    canileave = 0
                    for i in range(len(blockrowarr)):
                        if blockrowarr[i] == 0 and blockcolarr[i] == 1 and blockrow == 1 and blockcol == 0: #if [0][1], [1][0]
                            canileave = 1
                        elif blockrowarr[i] == 1 and blockcolarr[i] == 0 and blockrow == 0 and blockcol == 1: #if [1][0], [0][1]
                            canileave = 1
                        elif blockrowarr[i] == n-1 and blockcolarr[i] == n-2 and blockrow == n-2 and blockcol == n-1: #if [n-1][n-2], [n-2][n-1]
                            canileave = 1
                        elif blockrowarr[i] == n-2 and blockcolarr[i] == n-1 and blockrow == n-1 and blockcol == n-2: #if [n-2][n-1], [n-1][n-2]
                            canileave = 1
                    if canileave == 0:
                        numblocks += 1
                        grid[blockrow][blockcol] = '1'
                        blockrowarr.append(blockrow)
                        blockcolarr.append(blockcol)

#place (n-1) prizes at random positions in the maze 
def place_prizes(grid):
    prizerowarr = []
    prizecolarr = []
    numprizes = 0
    while numprizes < n:
        prizerow = random.randint(0, n-1) #random number between 0 and n-1
        prizecol = random.randint(0, n-1)
        if grid[prizerow][prizecol] == 0:
            numprizes += 1
            grid[prizerow][prizecol] = 2
            prizerowarr.append(prizerow)
            prizecolarr.append(prizecol)
    return prizerowarr, prizecolarr

#update the q-table by calculating the value of the Bellman Equation 
def update_qtable(qtable, playerpos, row_in_qtable, choice, reward):
    #that element of the row of qtable += that element of the row of qtable + alpha * (reward + gamma * max element in new row of qtable - that element of row of qtable)
    #go to the row that playerpos tells us (the position before we move)
    #then go to the action corresponding to the choice of which way to move
    if choice == 'u':
        col = 0
        newpos = [playerpos[0]-1, playerpos[1]]
    elif choice == 'r':
        col = 1
        newpos = [playerpos[0], playerpos[1]+1]
    elif choice == 'd':
        col = 2
        newpos = [playerpos[0]+1, playerpos[1]]
    else:
        col = 3
        newpos = [playerpos[0], playerpos[1]-1]

    #find row corresponding to new pos 
    if newpos[0] >= 0 and newpos[0] < n and newpos[1] >=0 and newpos[1] < n: #if newpos is a valid move 
        newrow = str(newpos[0]) + "," + str(newpos[1])
        newqmaxarr = []
        for i in range(4):
            newqmaxarr.append(qtable.loc[newrow][i])
        max_value_in_that_row = max(newqmaxarr)
    else: #if newpos isn't a valid move, then the q-value is just zero of the new position 
        max_value_in_that_row = 0

    #Bellman Equation 
    qtable.loc[row_in_qtable][col] += alpha*(reward + gamma*max_value_in_that_row - qtable.loc[row_in_qtable][col])
    return qtable

#update the maze to reflect current position of the player 
def update_maze(grid, playerpos, prizerowarr, prizecolarr):
    for i in range(n):
        for j in range(n):
            if i == playerpos[0] and j == playerpos[1]:
                grid[i][j] = 8
            elif grid[i][j] == 1:
                grid[i][j] = 1
            else:
                flag = 0
                for k in range(len(prizerowarr)):
                    if i == prizerowarr[k] and j == prizecolarr[k]:
                        flag = 1
                if flag == 1:
                    grid[i][j] = 2
                else:
                    grid[i][j] = 0

#check if new position is on the grid and is not a block
def check(choice, playerpos):
    if choice == 'l':
        checkpos = [playerpos[0], playerpos[1]-1]
    elif choice == 'r':
        checkpos = [playerpos[0], playerpos[1]+1]
    elif choice == 'u':
        checkpos = [playerpos[0]-1, playerpos[1]]
    elif choice == 'd':
        checkpos = [playerpos[0]+1, playerpos[1]]

    if checkpos[0] >= 0 and checkpos[0] < n and checkpos[1] >= 0 and checkpos[1] < n: #if it's a valid move 
        if grid[checkpos[0]][checkpos[1]] == 1: #if it's a block 
            return 2
        else: #if it's not a block but it's a valid move 
            return 1
    return 0 #if it's not a valid move 

#calculate the reward when player moves to a certain cell of the maze 
def calculate_reward(grid, choice, playerpos, reward, visitedcellsrow, visitedcellscol):

    leave_grid_reward = -50 #if it's trying to go out of the grid
    crash_wall_reward = -50 #if it's crashed into a wall
    collected_prize_reward = +3 #if it's collected a prize
    won_reward = +10 #if won
    already_visited_reward = -4 #if it's already visited that cell
    wandering_reward = 2 #there's a cost for every move to discourage too much wandering

    #calculate new position depending on which direction the player moves 
    if choice == 'l':
        rewpos = [playerpos[0], playerpos[1]-1]
    elif choice == 'r':
        rewpos = [playerpos[0], playerpos[1]+1]
    elif choice == 'u':
        rewpos = [playerpos[0]-1, playerpos[1]]
    elif choice == 'd':
        rewpos = [playerpos[0]+1, playerpos[1]]

    #assign rewards for various actions 
    if rewpos[0] < 0 or rewpos[0] >= n or rewpos[1] < 0 or rewpos[1] >= n: #if it's not a valid move 
        reward = leave_grid_reward
    elif rewpos[0] >= 0 and rewpos[0] < n and rewpos[1] >= 0 and rewpos[1] < n: #if it's a valid move 
        if grid[rewpos[0]][rewpos[1]] == 1: #if it's a block 
            reward = crash_wall_reward
        elif grid[rewpos[0]][rewpos[1]] == 2: #if it's collected a prize
            reward = collected_prize_reward
        elif rewpos[0] == n-1 and rewpos[1] == n-1: #if it's the end 
            reward = won_reward
        #if it's already visited that cell 
        #we do this always, because it needs to stop repeating past mistakes, so no 'else' here 
        for i in range(len(visitedcellsrow)): 
            if rewpos[0] == visitedcellsrow[i] and rewpos[1] == visitedcellscol[i]: 
                reward = already_visited_reward

    reward -= wandering_reward 
    return reward

#print maze as a coloured grid 
def show(maze, playerpos, visitedcellsrow, visitedcellscol, prizerowarr, prizecolarr):
    plt.grid('on')
    nrows = n
    ncols = n
    ax = plt.gca()
    ax.set_xticks(np.arange(0.5, nrows, 1)) #setting gridlines for x-axis
    ax.set_yticks(np.arange(0.5, ncols, 1)) #setting gridlines for y-axis
    ax.xaxis.set_ticks_position('none') #removing xticks
    ax.yaxis.set_ticks_position('none') #removing yticks
    ax.set_xticklabels([]) #no x-axis label
    ax.set_yticklabels([]) #no y-axis label

    prettymaze = np.copy(maze)
    for i in range(n):
        for j in range(n):
            if prettymaze[i][j] == 1.0: 
                prettymaze[i][j] = 0.1 #block position 
            elif i == playerpos[0] and j == playerpos[1]:
                prettymaze[i][j] = 0.7 #player position 
            elif i == n-1 and j == n-1:
                prettymaze[i][j] = 0.6 #end position 
            else:
                for l in range(len(prizerowarr)):
                    if i == prizerowarr[l] and j == prizecolarr[l]:
                        prettymaze[i][j] = 0.3 #prize position 
                for k in range(len(visitedcellsrow)):
                    if i == visitedcellsrow[k] and j == visitedcellscol[k]:
                        prettymaze[i][j] = 0.4 #visited cell 

    plt.imshow(prettymaze, cmap = 'Pastel1') 
    #cbar = plt.colorbar(ticks = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7]) #for colorbar 
    #cbar.ax.set_yticklabels(['empty', 'block', '', 'prize', 'visited', '', 'end', 'player'])  
    plt.pause(0.1) #pause output 
    plt.clf() #clear figure 
    if playerpos[0] == n-1 and playerpos[1] == n-1: #if it's reached the end, wait for user to click on screen to close maze  
        plt.waitforbuttonpress()
    #plt.savefig('Documents/RC/Maze/maze.png')

#move player through maze 
def move_player(grid, playerpos, totalreward, qtable, visitedcellsrow, visitedcellscol, prizerowarr, prizecolarr, epsilon):
    flag = 0
    while flag == 0:
        reward = 0
        #print("\nWhere do you want to move? Enter l (left), r (right), u (up), d (down) : ")

        #before deciding where to move, check the values in the row of the q-table corresponding to playerpos
        qflag = 0
        qmaxarr = []
        row_in_qtable = str(playerpos[0]) + "," + str(playerpos[1]) #tells us which row to look up in the q-table 
        for i in range(4):
            qmaxarr.append(qtable.loc[row_in_qtable][i]) #stores all q-values in that row so we can find the maximum 
            if qtable.loc[row_in_qtable][i] != 0:
                qflag = 1 #if all q-values are zero 
        bestmove = qmaxarr.index(max(qmaxarr)) #find the action corresponding to the highest q-value in that row i.e. best action for that state

        #epsilon-greedy approach 
        #with probability epsilon, move randomly 
        population = [1, 2] #1 means random move (exploration), 2 means best move (exploitation)
        weights = [epsilon, 1-epsilon]
        draw = choices(population, weights)[0]

        #if all values are zero in that row, or epsilon-greedy approach chooses 1, move randomly
        if qflag == 0 or draw == 1:
            choice = random.randint(0, 3) #random number between 0 and 3
            if choice == 0:
                choice = 'l'
            elif choice == 1:
                choice = 'r'
            elif choice == 2:
                choice = 'u'
            else:
                choice = 'd'
        
        #otherwise, choose the best move (the one with the highest q-value in that row)
        else:
            #print("i know what the best move is!")
            if bestmove == 0:
                choice = 'u'
            elif bestmove == 1:
                choice = 'r'
            elif bestmove == 2:
                choice = 'd'
            else:
                choice = 'l'

        reward = calculate_reward(grid, choice, playerpos, reward, visitedcellsrow, visitedcellscol)
        totalreward += reward 
        qtable = update_qtable(qtable, playerpos, row_in_qtable, choice, reward)

        if check(choice, playerpos) == 1: #this means it's a valid move, so we move there 
            if choice == 'l':
                playerpos[1] -= 1
            elif choice == 'r':
                playerpos[1] += 1
            elif choice == 'u':
                playerpos[0] -= 1
            elif choice == 'd':
                playerpos[0] += 1
            flag = 1
            grid[playerpos[0]][playerpos[1]] = 2
            visitedcellsrow.append(playerpos[0])
            visitedcellscol.append(playerpos[1])
            update_maze(grid, playerpos, prizerowarr, prizecolarr)
        
        #if that action isn't allowed, don't actually move (don't modify playerpos), but count it as a move 
        elif check(choice, playerpos) == 2: #this means we hit a wall
            flag = 1
        elif check(choice, playerpos) == 0: #this means it's not a valid move
            flag = 1

    return totalreward

print("\nHello! We are building a maze solver.")
n = eval(input("\nEnter the dimensions of the maze grid : "))
print("\nThe dimensions of our maze are", n, "by", n)

#q-table is of size (no. of states) X (no. of actions for each state) = (n*n) X (4)
qvalues = np.zeros(shape=(n*n,4))
qvalues[[-1],:] = +10 #set the q-value for the last row (corresponding to end cell of the maze, [n-1][n-1], to be +10 i.e. max reward)
#print("qvalues = \n", qvalues)
qrows = [] #rows of q-table should correspond to all possible states (cells) in the maze eg. 1,2 is the element in the 1st row and 2nd column
for i in range(n):
    for j in range(n):
        qrows.append(str(i) + "," + str(j))
qcols = ['u', 'r', 'd', 'l'] #columns of q-table correspond to the actions the player can take at any state 
qtable = pd.DataFrame(qvalues, index = qrows, columns = qcols)

ismazeok = 'n'
while ismazeok == 'n':

    #create maze grid as 2d array (empty space denoted by '0')
    grid = np.zeros(shape = (n, n)) #initialise maze grid as array of 0s

    #set blocks 
    place_blocks(grid)

    #set prizes
    prizerowarr = []
    prizecolarr = []
    prizerowarr, prizecolarr = place_prizes(grid)

    #initialise positions 
    playerpos = [0, 0]
    visitedcellsrow = [0]
    visitedcellscol = [0]
    show(grid, playerpos, visitedcellsrow, visitedcellscol, prizerowarr, prizecolarr)
    ismazeok = input("\nIs this maze ok? (y/n) \n")

#set number of episodes we want to train for 
episodes = 1
max_episodes = 300 

#start the training 
print("\nTraining...\n")

#train for [max_episodes] episodes, use same qtable throughout episodes to get best approximation for values, but set everything else to zero 
while episodes <= max_episodes: 

    #start the player at (0,0)
    playerpos = [0, 0]
    update_maze(grid, playerpos, prizerowarr, prizecolarr)
        
    #move player until it escapes from the maze
    keepmoving = 'y'
    movecounter = 0
    totalreward = 0
    unsolved = 0

    #keep track of which cells have been visited 
    visitedcellsrow = [0]
    visitedcellscol = [0]

    #move through maze until solved/gave up 
    while keepmoving == 'y':
        if episodes <= max_episodes/10:
            epsilon = 0.8 #exploration 
        else:
            epsilon = 0 #exploitation 
        totalreward = move_player(grid, playerpos, totalreward, qtable, visitedcellsrow, visitedcellscol, prizerowarr, prizecolarr, epsilon) #move player 
        if episodes == max_episodes: #show the grid once we're at the final episode 
            os.system("clear")
            print("EPISODE", episodes, "\n")
            show(grid, playerpos, visitedcellsrow, visitedcellscol, prizerowarr, prizecolarr) 
        movecounter += 1
        if playerpos[0] == n-1 and playerpos[1] == n-1: #if reached the end, we're done!
            keepmoving = 'n'
        if totalreward <= -100*(n**2): #if moving around for too long - make this depend on size of maze 
            unsolved = 1
            break

    if unsolved == 0 and episodes != max_episodes:
        print("EPISODE", episodes, "... solved in", movecounter, "steps.")
    elif unsolved == 1 and episodes != max_episodes:
        print("EPISODE", episodes, "... gave up.")
    if episodes == max_episodes:
        print("... solved in", movecounter, "steps.\n")

    episodes += 1







