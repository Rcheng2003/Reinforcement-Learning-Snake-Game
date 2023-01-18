import torch
import random
import numpy as np
from collections import deque
from main import SnakeGameAI, Direction, Point
from model import Linear_QNet, QTrainer
from helper import plot

MEMORY = 100_000
BATCH = 1000
LearnRate = 0.005

class Agent:
    def __init__(self):
        self.n_games = 0
        self.epsilon = 0
        self.gamma = 0.9
        self.memory = deque(maxlen = MEMORY)
        self.model = Linear_QNet(13,512,3)
        self.trainer = QTrainer(self.model, lr=LearnRate, gamma= self.gamma)

    def getDanger(self, game, turn):
        head = game.snake[0]
        Threat = 0
        count = 0
        while(True):
            pointL = Point(head.x - (count * 40), head.y)
            pointR = Point(head.x + (count * 40), head.y)
            pointU = Point(head.x, head.y - (count * 40))
            pointD = Point(head.x, head.y + (count * 40))
            if game.direction == Direction.LEFT:
                if turn == 's':
                    Tpoint = pointL
                elif turn == 'r':
                    Tpoint = pointU
                elif turn == 'l':
                    Tpoint = pointD


            elif game.direction == Direction.RIGHT:
                if turn == 's':
                    Tpoint = pointR
                elif turn == 'r':
                    Tpoint = pointD
                elif turn == 'l':
                    Tpoint = pointU

            elif game.direction == Direction.UP:
                if turn == 's':
                    Tpoint = pointU
                elif turn == 'r':
                    Tpoint = pointR
                elif turn == 'l':
                    Tpoint = pointL

            elif game.direction == Direction.DOWN:
                if turn == 's':
                    Tpoint = pointD
                elif turn == 'r':
                    Tpoint = pointL
                elif turn == 'l':
                    Tpoint = pointR

            if Tpoint in game.snake:
                Threat = count
            if game.is_collision(Tpoint):
                break
            count += 1
            
        return Threat

    def futureDanger(self, game, Direction1):
        head = game.snake[0]
        total = 0

        pointLD = Point(head.x - 40, head.y + 40)
        pointLU = Point(head.x - 40, head.y - 40)
        pointRU = Point(head.x + 40, head.y - 40)
        pointRD = Point(head.x + 40, head.y + 40)
        if Direction1 == Direction.LEFT:
            total = game.is_collision(pointLD) + game.is_collision(pointLU)
        elif Direction1 == Direction.RIGHT:
            total = game.is_collision(pointRU) + game.is_collision(pointRD)
        elif Direction1 == Direction.UP:
            total = game.is_collision(pointLU) + game.is_collision(pointRU)
        elif Direction1 == Direction.DOWN:
            total = game.is_collision(pointLD) + game.is_collision(pointRD)

        return total


    def getstate(self, game):
        dir_l = game.direction == Direction.LEFT
        dir_r = game.direction == Direction.RIGHT
        dir_u = game.direction == Direction.UP
        dir_d = game.direction == Direction.DOWN

        head = game.snake[0]
        pointL = Point(head.x - 40, head.y)
        pointR = Point(head.x + 40, head.y)
        pointU = Point(head.x, head.y - 40)
        pointD = Point(head.x, head.y + 40)

        pointLD = Point(head.x - 40, head.y + 40)
        pointLU = Point(head.x - 40, head.y - 40)
        pointRU = Point(head.x + 40, head.y - 40)
        pointRD = Point(head.x + 40, head.y + 40)

        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        index = clock_wise.index(game.direction)
        left = clock_wise[(index - 1) % 4]
        right = clock_wise[(index + 1) % 4]

        dict = {Direction.RIGHT: Point(head.x + 40, head.y), Direction.DOWN: Point(head.x, head.y + 40), Direction.LEFT: Point(head.x - 40, head.y),Direction.UP: Point(head.x, head.y - 40)}        

        if (dir_r and (pointR in game.snake)):
            game.findInner(pointR)
        elif (dir_l and (pointL in game.snake)):
            game.findInner(pointL)
        elif (dir_u and (pointU in game.snake)):
            game.findInner(pointU)
        elif (dir_d and (pointD in game.snake)):
            game.findInner(pointD)

        enclosedLeft = dict[left] in game.Inner
        enclosedRight = dict[right] in game.Inner

        state = [
            (dir_r and game.is_collision(pointR)) or 
            (dir_l and game.is_collision(pointL)) or 
            (dir_u and game.is_collision(pointU)) or 
            (dir_d and game.is_collision(pointD)),

            # Danger right
            (dir_u and game.is_collision(pointR)) or 
            (dir_d and game.is_collision(pointL)) or 
            (dir_l and game.is_collision(pointU)) or 
            (dir_r and game.is_collision(pointD)),

            # Danger left
            (dir_d and game.is_collision(pointR)) or 
            (dir_u and game.is_collision(pointL)) or 
            (dir_r and game.is_collision(pointU)) or 
            (dir_l and game.is_collision(pointD)),
            # Danger straight
            enclosedLeft,
            enclosedRight,
            
            dir_l,
            dir_r,
            dir_u,
            dir_d,
            
            # Food location 
            game.food.x < game.head.x,  # food left
            game.food.x > game.head.x,  # food right
            game.food.y < game.head.y,  # food up
            game.food.y > game.head.y  # food down
            ]

        return np.array(state, dtype = int)

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def train_long_memory(self):
        if len(self.memory) > BATCH:
            mini_sample = random.sample(self.memory, BATCH)
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)


    def train_short_memory(self,state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self,state):
        self.epsilon = 80 - self.n_games
        finalMove = [0,0,0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0,2)
            finalMove[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            finalMove[move] = 1
        
        return finalMove

def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    game =SnakeGameAI()
    while True:
        state_old = agent.getstate(game)

        final_move = agent.get_action(state_old)

        reward, done, score = game.play_step(final_move)

        state_new = agent.getstate(game)

        agent.train_short_memory(state_old, final_move, reward, state_new, done) 

        agent.remember(state_old, final_move, reward, state_new, done)

        if done:
            game.reset()
            agent.n_games += 1
            agent.train_long_memory()

            if score > record:
                record = score
                agent.model.save()

            print("Game", agent.n_games, "Score", score, "High Score", record)

            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)


if __name__ == '__main__':
    train()
