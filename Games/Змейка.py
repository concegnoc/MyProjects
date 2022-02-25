from tkinter import *
import random

WEIGHT = 700
HEIGHT = 700
SIZE_SNAKE = 10
X_START = 100
Y_START = 100
IN_GAME = True

class Score(object):
    def __init__(self):
        self.score = 0
        c.create_text(60, 20,
                  text=f"Score: {self.score}", 
                  font=("Arial Bold", 20), tag="score")
    
    def add_point(self):
        c.delete("score")
        self.score += 10
        c.create_text(60, 20,
                  text=f"Score: {self.score}", 
                  font=("Arial Bold", 20), tag="score")


def snake_food():
    global FOOD
    pos_x = SIZE_SNAKE * random.randint(1, (WEIGHT - SIZE_SNAKE)/SIZE_SNAKE)
    pos_y = SIZE_SNAKE * random.randint(1, (HEIGHT - SIZE_SNAKE)/SIZE_SNAKE)
    FOOD = c.create_oval(pos_x, pos_y, pos_x + SIZE_SNAKE, pos_y + SIZE_SNAKE, fill='green')

def main():
    global IN_GAME
    if IN_GAME == True:
        s.move()

        # Координаты головы змейки
        head_coords = c.coords(s.segments[-1].instance)
        x1, y1, x2, y2 = head_coords

        if x1 < 0 or x1 > WEIGHT or y1 < 0 or y1 > HEIGHT:
            IN_GAME = False
        elif head_coords == c.coords(FOOD):
            c.delete(FOOD)
            score.add_point()
            s.add_segment()
            snake_food();
        else:
            for index in range(len(s.segments) - 1):
                if head_coords == c.coords(s.segments[index].instance):
                    IN_GAME = False 

        root.after(100, main)
    else:
        c.create_text(350, 350,
                  text="Game over", 
                  font=("Arial Bold", 30))
        

class Create_Snake(object):
    def __init__(self, x, y):
        self.instance = c.create_rectangle(x, y,
                                           x + SIZE_SNAKE, y + SIZE_SNAKE,
                                           fill="black")

class Snake(object):
    def __init__(self, segments):
        self.segments = segments

        self.direction = {"Up":(0,-1), "Down":(0,1),
                        "Right":(1,0), "Left":(-1,0)}

        self.now_direction = self.direction["Down"]
    
    def move(self):
        for index in range(len(self.segments) - 1):
            segment = self.segments[index].instance
            x1, y1, x2, y2 = c.coords(self.segments[index + 1].instance)
            c.coords(segment, x1, y1, x2, y2)

        x1, y1, x2, y2 = c.coords(self.segments[-1].instance)
        c.coords(self.segments[-1].instance, x1 + self.now_direction[0] * SIZE_SNAKE, y1 + self.now_direction[1] * SIZE_SNAKE, 
                                            x2 + self.now_direction[0] * SIZE_SNAKE, y2 + self.now_direction[1] * SIZE_SNAKE)
    
    def change_direction(self, event):
        if event.char == "w":
            side = "Up"
        elif event.char == "s":
            side = "Down"
        elif event.char == "a":
            side = "Left"
        elif event.char == "d":
            side = "Right"

        if side in self.direction:
            self.now_direction = self.direction[side]

    def add_segment(self):
        x1, y1, x2, y2 = c.coords(self.segments[0].instance)
        self.segments.insert(0, Create_Snake(x1, y1))


def crate_snake():
    segments = [Create_Snake(X_START, Y_START),
                Create_Snake(X_START, Y_START + SIZE_SNAKE),
                Create_Snake(X_START, Y_START + 2 * SIZE_SNAKE)]
    return Snake(segments)

def start_game():
    global s
    snake_food()
    s = crate_snake()

    root.bind("<Key>", s.change_direction)
    main()

root = Tk()
root.minsize(width=WEIGHT, height=HEIGHT)
root.title("Игра")

c = Canvas(root, width=WEIGHT, height=HEIGHT)
c.grid()
c.focus_set()

score = Score()

start_game()

root.mainloop()

