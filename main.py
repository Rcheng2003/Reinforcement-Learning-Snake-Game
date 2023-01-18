
import pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np

pygame.init()
font = pygame.font.Font('arial.ttf', 25)

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4
    
Point = namedtuple('Point', 'x, y')

# rgb colors
WHITE = (255, 255, 255)
RED = (200,0,0)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
BLACK = (0,0,0)

APPLE = pygame.image.load('snake_apple.png')
RealApple = pygame.transform.scale(APPLE, (40,40))

bg = pygame.image.load("Board.png")
realbg = pygame.transform.scale(bg, (760,680))

HS = pygame.image.load('HighScore.png')
realHS = pygame.transform.scale(HS, (40,40))

head = pygame.image.load('Head.png')
realhead = pygame.transform.scale(head, (40,40))
body = pygame.image.load('Body.png')
realbody = pygame.transform.scale(body, (40,40))
tail = pygame.image.load('Tail.png')
realtail = pygame.transform.scale(tail, (40,40))


BLOCK_SIZE = 40
SPEED = 50

class SnakeGameAI:
    
    def __init__(self, w=760, h=680):
        self.w = w
        self.h = h
        # init display
        self.display = pygame.display.set_mode((self.w, self.h))
        self.Speeed = True

        pygame.display.set_caption('SneK')
        self.clock = pygame.time.Clock()
        self.highscore = 0
        # init game state
        self.reset()

    def findInner(self,head):
        border = [head]
        for i in self.snake:
            if i == head:
                break
            border.append(i)

        self.Inner = []
        minX = min([i.x for i in border])
        maxX = max([i.x for i in border])
        minY = min([i.y for i in border])
        maxY = max([i.y for i in border])

        for row in range(minX,maxX,40):
            count = 0
            for column in range(minY, maxY,40):
                temp = Point(row,column)   
                if count == 1:
                    self.Inner.append(temp)
                
                if temp in border:
                    count += 1
                    if(count == 2):
                        self.Inner.pop()
                        continue

    def reset(self):
        self.direction = Direction.RIGHT
        self.currdirect = 0

        self.head = Point(160, 320)
        self.snake = [self.head, 
                      Point(self.head.x-BLOCK_SIZE, self.head.y),
                      Point(self.head.x-(2*BLOCK_SIZE), self.head.y)]

        self.directions = [0,0,0]
        self.Inner = []
        
        self.score = 0
        self.food = None
        self._place_food()
        self.frame_iteration = 0
        
    def _place_food(self):
        x = random.randint(1, (self.w-(BLOCK_SIZE * 2))//BLOCK_SIZE )*BLOCK_SIZE 
        y = random.randint(1, (self.h-(BLOCK_SIZE * 2))//BLOCK_SIZE )*BLOCK_SIZE
        self.food = Point(x, y)
        if self.food in self.snake:
            self._place_food()
        
    def play_step(self, action):
        self.frame_iteration += 1
        # 1. collect user input
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                print(self.highscore)
                pygame.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.Speeed = not(self.Speeed)

        if self.Speeed:
            SPEED = 500
        else:
            SPEED = 10
        
        # 2. move
        self._move(action) # update the head
        self.snake.insert(0, self.head)
        self.directions.insert(0, self.currdirect)
        
        # 3. check if game over
        reward = 0
        game_over = False
        if self.is_collision() or self.frame_iteration > 100 * len(self.snake) or self.head in self.Inner:
            reward -= 10 
            # init game state
            if self.highscore < self.score:
                self.highscore = self.score
            game_over = True
            return reward, game_over, self.score

        self.Inner = []
        # 4. place new food or just move
        if self.head == self.food:
            reward = 10
            self.score += 1
            self._place_food()
        else:
            self.snake.pop()
            self.directions.pop()
        
        # 5. update ui and clock
        self._update_ui()
        self.clock.tick(SPEED)
        if self.clock.get_time() > 10000:
            reward -= 10
            game_over = True
        # 6. return game over and score
        return reward, game_over, self.score
    
    def is_collision(self, pt = None):
        if pt is None:
            pt = self.head
        # hits boundary
        if pt.x > (self.w - (BLOCK_SIZE * 2)) or pt.x < BLOCK_SIZE or pt.y > (self.h - (BLOCK_SIZE * 2)) or pt.y < BLOCK_SIZE:
            return True
        # hits itself
        if pt in self.snake[1:]:
            return True
        
        return False
        
    def _update_ui(self):

        self.display.blit(realbg, (0,0))
        
        for pt in range(0,len(self.snake)):
            if pt == 0:
                newhead = pygame.transform.rotate(realhead, ((self.currdirect) * 90))
                self.display.blit(newhead, ((self.snake[pt]).x, (self.snake[pt]).y))
            elif pt == len(self.snake) - 1:
                newtail = pygame.transform.rotate(realtail, ((self.directions[pt]) * 90))
                self.display.blit(newtail, ((self.snake[pt]).x, (self.snake[pt]).y))
            else:
                self.display.blit(realbody, ((self.snake[pt]).x, (self.snake[pt]).y))
            
        self.display.blit(RealApple, (self.food.x, self.food.y))

        for change in self.Inner:
            pygame.draw.rect(self.display, RED, pygame.Rect(change.x, change.y, BLOCK_SIZE, BLOCK_SIZE))

        
        text = font.render("Score: " + str(self.score), True, WHITE)
        text1 = font.render("HighScore: " + str(self.highscore), True, WHITE)
        self.display.blit(RealApple, [10,0])
        self.display.blit(text, [50, 5])
        self.display.blit(realHS, [160,0])
        self.display.blit(text1, [200,5])
        pygame.display.flip()
        
    def _move(self, action):
        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        index = clock_wise.index(self.direction)

        if np.array_equal(action, [1,0,0]):
            newdirection = clock_wise[index]
        elif np.array_equal(action, [0,1,0]):
            nextindex = (index + 1) % 4
            newdirection = clock_wise[nextindex]
        elif np.array_equal(action, [0,0,1]):
            nextindex = (index - 1) % 4
            newdirection = clock_wise[nextindex]
        self.direction = newdirection
        self.currdirect = clock_wise.index(self.direction)
        if self.currdirect == 1:
            self.currdirect = 3
        elif self.currdirect == 3:
            self.currdirect = 1

        x = self.head.x
        y = self.head.y
        if self.direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif self.direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif self.direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif self.direction == Direction.UP:
            y -= BLOCK_SIZE
            
        self.head = Point(x, y)

    


            

