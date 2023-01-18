import pygame
import random
from enum import Enum
from collections import namedtuple
from sortedcollections import OrderedSet
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

eating = pygame.image.load('Eating.png')
RE = pygame.transform.scale(eating, (40,40))


BLOCK_SIZE = 40
SPEED = 10

class SnakeGame:
    
    def __init__(self, w=760, h=680):
        self.w = w
        self.h = h
        # init display
        self.display = pygame.display.set_mode((self.w, self.h))

        pygame.display.set_caption('SneK')
        self.clock = pygame.time.Clock()
        self.highscore = 0
        # init game state
        self.reset()

    def findborder(self):
        border = [self.snake[0]]
        for i in self.snake[1:]:
            if i == self.snake[0]:
                break
            border.append(i)
        return border

    def findInner(self,border):
        Inner = []
        minX = min([i.x for i in border])
        maxX = max([i.x for i in border])
        minY = min([i.y for i in border])
        maxY = max([i.y for i in border])

        for row in range(minX,maxX,40):
            count = 0
            for column in range(minY, maxY,40):
                temp = Point(row,column)   
                if count == 1:
                    Inner.append(temp)
                
                if temp in border:
                    count += 1
                    if(count == 2):
                        Inner.pop()
                        continue

        
        for change in Inner:
            print(change.x," ", change.y)
                


    def reset(self):
        self.newgame = True
        self.direction = Direction.RIGHT
        self.currdirect = 0
        
        self.head = Point(160, 320)
        self.snake = [self.head, 
                      Point(self.head.x-BLOCK_SIZE, self.head.y),
                      Point(self.head.x-(2*BLOCK_SIZE), self.head.y)]

        self.directions = [0,0,0]
        
        self.score = 0
        self.food = None
        self._place_food()
        
    def _place_food(self):
        x = random.randint(1, (self.w-(BLOCK_SIZE * 2))//BLOCK_SIZE )*BLOCK_SIZE 
        y = random.randint(1, (self.h-(BLOCK_SIZE * 2))//BLOCK_SIZE )*BLOCK_SIZE
        self.food = Point(x, y)
        if self.food in self.snake:
            self._place_food()
        
    def play_step(self):
        # 1. collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print(self.highscore)
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and self.currdirect != 0:
                    self.currdirect = 2
                    self.direction = Direction.LEFT
                if event.key == pygame.K_RIGHT and self.currdirect != 2:
                    self.currdirect = 0
                    self.direction = Direction.RIGHT
                elif event.key == pygame.K_UP and self.currdirect != 3:
                    self.currdirect = 1
                    self.direction = Direction.UP
                elif event.key == pygame.K_DOWN and self.currdirect != 1:
                    self.currdirect = 3
                    self.direction = Direction.DOWN
        
        # 2. move
        self._move(self.direction) # update the head
        self.snake.insert(0, self.head)
        self.directions.insert(0, self.currdirect)
        
        # 3. check if game over
        game_over = False
        if self.is_collision():      
            # init game state
            if self.highscore < self.score:
                self.highscore = self.score
            
            #self.reset()
            return game_over, self.score

            
        # 4. place new food or just move
        if self.head == self.food:
            self.score += 1
            self._place_food()
        else:
            self.snake.pop()
            self.directions.pop()
        
        # 5. update ui and clock
        self._update_ui()
        self.clock.tick(SPEED)
        if self.newgame == True:
            self.newgame = False
            Pressed = False
            while True:
                pygame.time.wait(10)

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        print(self.highscore)
                        pygame.quit()
                        quit()
                
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RIGHT or event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                            Pressed = True

                        if event.key == pygame.K_RIGHT and self.currdirect != 2:
                            self.currdirect = 0
                            self.direction = Direction.RIGHT
                        elif event.key == pygame.K_UP and self.currdirect != 3:
                            self.currdirect = 1
                            self.direction = Direction.UP
                        elif event.key == pygame.K_DOWN and self.currdirect != 1:
                            self.currdirect = 3
                            self.direction = Direction.DOWN
                if Pressed:
                    break

        # 6. return game over and score
        return game_over, self.score
    
    def is_collision(self, pt = None):
        if pt == None:
            pt = self.head
        # hits boundary
        if pt.x > (self.w - (BLOCK_SIZE * 2)) or pt.x < BLOCK_SIZE or pt.y > (self.h - (BLOCK_SIZE * 2)) or pt.y < BLOCK_SIZE:
            return True
        # hits itself
        if pt in self.snake[1:]:
            self.findInner(self.findborder())
            return True
        
        return False
        
    def _update_ui(self):
        self.display.blit(realbg, (0,0))
        
        for pt in range(0,len(self.snake)):
            if pt == 0:
                if ( ((self.food.x + (BLOCK_SIZE * 2)) > (self.snake[pt]).x) and ((self.food.x - (BLOCK_SIZE * 2)) < (self.snake[pt]).x) and ((self.food.y - (BLOCK_SIZE * 2)) < (self.snake[pt]).y) and ((self.food.y + (BLOCK_SIZE * 2)) > (self.snake[pt]).y)):
                    temp = RE
                else:
                    temp = realhead
                newhead = pygame.transform.rotate(temp, (self.currdirect * 90))
                self.display.blit(newhead, ((self.snake[pt]).x, (self.snake[pt]).y))
            elif pt == len(self.snake) - 1:
                newtail = pygame.transform.rotate(realtail, ((self.directions[pt]) * 90))
                self.display.blit(newtail, ((self.snake[pt]).x, (self.snake[pt]).y))
            else:
                self.display.blit(realbody, ((self.snake[pt]).x, (self.snake[pt]).y))
            
        self.display.blit(RealApple, (self.food.x, self.food.y))

        
        text = font.render("Score: " + str(self.score), True, WHITE)
        text1 = font.render("HighScore: " + str(self.highscore), True, WHITE)
        self.display.blit(RealApple, [10,0])
        self.display.blit(text, [50, 5])
        self.display.blit(realHS, [160,0])
        self.display.blit(text1, [200,5])
        pygame.display.flip()
        
    def _move(self, direction):
        x = self.head.x
        y = self.head.y
        if direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif direction == Direction.UP:
            y -= BLOCK_SIZE
            
        self.head = Point(x, y)

if __name__ == '__main__':
    game = SnakeGame()
    
    # game loop
    while True:
        game_over, score = game.play_step()
        
        if game_over == True:
            break
        
    print('Final Score', score)
        
    
