from tkinter import *
import math

# Ширина и длина карты
WEIGHT_MAP = 200
HEIGHT_MAP = 200

# Ширина и длина дисплея
WEIGHT_DISPLAY = 1500
HEIGHT_DISPLAY = 800

# Начальные координаты игрока
X_PLAYER = 50
Y_PLAYER = 50

# Размеры персонажа
PLAYER_SIZE = 4

# Коэффициент чувствительности мыши (количество полных оборотов при перемещении мыши от одного края к другому)
K_MOUSE = 2

# Радиус видимости персонажа
RADIUS_VISION = 150

# Угол сектора видимости
ANGLE_VISION = math.pi / 3

# Расстояние на котором игрок видит барьер во весь экран
FULL_DISTANCE = 10

def dot_detween_segments(coords1, coords2):
    c1_x1, c1_y1, c1_x2, c1_y2 = coords1
    c2_x1, c2_y1, c2_x2, c2_y2 = coords2

    if c1_x1 == c1_x2 or c2_x1 == c2_x2:
        if c1_x1 == c1_x2 and c2_x1 == c2_x2:
            return ["Empty", "Empty"]
        else:
            if c1_x1 == c1_x2 and c2_x1 != c2_x2:
                x = c1_x1
                k = (c2_y2 - c2_y1) / (c2_x2 - c2_x1)
                b = c2_y1 - k * c2_x1
                y = k * x + b
                return [x, y]
            else:
                x = c2_x1
                k = (c1_y2 - c1_y1) / (c1_x2 - c1_x1)
                b = c1_y1 - k * c1_x1
                y = k * x + b
                return [x, y]
    else:
        k1 = (c1_y2 - c1_y1) / (c1_x2 - c1_x1)
        k2 = (c2_y2 - c2_y1) / (c2_x2 - c2_x1)
        if k1 != k2:
            b1 = c1_y1 - k1 * c1_x1
            b2 = c2_y1 - k2 * c2_x1
            x = (b2 - b1) / (k1 - k2)
            y = k1 * x + b1
            return [x, y]
        else:
            return ["Empty", "Empty"]


class Player(object):
    def __init__(self, bariers):
        self.bariers = bariers
        x, y = X_PLAYER, Y_PLAYER
        self.player_coord = c2.create_rectangle(x, y,
                                           x + PLAYER_SIZE, y + PLAYER_SIZE,
                                           fill="black")
        self.lines = []
        for degree in range(int(ANGLE_VISION * 180 / math.pi)):
            self.lines.append(c2.create_line(x + PLAYER_SIZE / 2, y + PLAYER_SIZE / 2, 
                                            x + PLAYER_SIZE / 2 + RADIUS_VISION * math.cos(degree * math.pi / 180), 
                                            y + PLAYER_SIZE / 2 + RADIUS_VISION * math.sin(degree * math.pi / 180)))
        
        self.md = Main_Display(self.lines, self.bariers)

    def move(self, event):
        avg_index = int(len(self.lines) / 2)
        l_x1, l_y1, l_x2, l_y2 = c2.coords(self.lines[avg_index])
        distance = ((l_x1 - l_x2) ** 2 + (l_y1 - l_y2) ** 2) ** (1/2)
        cos_angle = (l_x2 - l_x1) / distance
        sin_angle = (l_y2 - l_y1) / distance

        if distance < PLAYER_SIZE:
            koef = 0
        elif event.char == "w":
            koef = 1
        elif event.char == "s":
            koef = -1
        elif event.char == "d":
            koef = 1
            cos_angle, sin_angle = -sin_angle, cos_angle
        elif event.char == "a":
            koef = 1
            cos_angle, sin_angle = sin_angle, -cos_angle

        x1, y1, x2, y2 = c2.coords(self.player_coord)
        c2.coords(self.player_coord, x1 + PLAYER_SIZE * cos_angle * koef, y1 + PLAYER_SIZE * sin_angle * koef, 
                                    x2 + PLAYER_SIZE * cos_angle * koef, y2 + PLAYER_SIZE * sin_angle * koef)
        
        for index in self.lines:
            x1, y1, x2, y2 = c2.coords(index)
            # Случай, когда радиусы обрезаны
            distance = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** (1/2)
            if abs(distance - RADIUS_VISION) > PLAYER_SIZE:
                sin_line = (y2 - y1) / distance
                cos_line = (x2 - x1) / distance
                x2 = x1 + cos_line * RADIUS_VISION
                y2 = y1 + sin_line * RADIUS_VISION

            c2.coords(index, x1 + PLAYER_SIZE * cos_angle * koef, y1 + PLAYER_SIZE * sin_angle * koef, 
                                x2 + PLAYER_SIZE * cos_angle * koef, y2 + PLAYER_SIZE * sin_angle * koef)
        
        self.md.change_main_display(self.lines)

    def change_direction(self, event):
        global x_early, angle
        x = event.x
        root.title(x)
        angle += (x - x_early) / WEIGHT_DISPLAY * K_MOUSE * 2 * math.pi
        x_early = x

        for index in range(len(self.lines)):
            x1, y1, x2, y2 = c2.coords(self.lines[index])
            c2.coords(self.lines[index], x1, y1, 
                                    x1 + RADIUS_VISION * math.cos(angle + index * math.pi / 180), 
                                    y1 + RADIUS_VISION * math.sin(angle + index * math.pi / 180))

        self.md.change_main_display(self.lines)

    def cut_line(self, index, coords):
        c2.coords(self.lines[index], coords[0], coords[1], coords[2], coords[3])


class Main_Display(object):
    def __init__(self, lines, bariers):
        self.bariers = bariers
        self.upper_rect = []
        self.lower_rect = []
        self.display_barier = []

        for index in range(len(lines)):
            # Верхняя часть дисплея
            self.upper_rect.append(c1.create_rectangle(index * WEIGHT_DISPLAY / len(lines), 0,
                                                        (index + 1) * WEIGHT_DISPLAY / len(lines), HEIGHT_DISPLAY / 2,
                                                        fill="gray70", outline="gray70"))
            # Нижняя часть дисплея
            self.lower_rect.append(c1.create_rectangle(index * WEIGHT_DISPLAY / len(lines), HEIGHT_DISPLAY / 2,
                                                        (index + 1) * WEIGHT_DISPLAY / len(lines), HEIGHT_DISPLAY,
                                                        fill="gray35", outline="gray35"))

            # Часть дисплея для препятствий
            self.display_barier.append(c1.create_rectangle(index * WEIGHT_DISPLAY / len(lines), HEIGHT_DISPLAY / 2,
                                                        (index + 1) * WEIGHT_DISPLAY / len(lines), HEIGHT_DISPLAY / 2,
                                                        fill="gray20", outline="gray20"))

    def change_main_display(self, lines_now):
        for index in range(len(lines_now)):
            distance = []
            end_coord = []
            for barier in self.bariers:
                b_x1, b_y1, b_x2, b_y2 = c2.coords(barier)
                l_x1, l_y1, l_x2, l_y2 = c2.coords(lines_now[index])
                if lines_now[index] in c2.find_overlapping(b_x1, b_y1, b_x2, b_y2):
                    segments = [[b_x1, b_y1, b_x1, b_y2], [b_x1, b_y1, b_x2, b_y1], 
                                [b_x1, b_y2, b_x2, b_y2], [b_x2, b_y1, b_x2, b_y2]]

                    for segment in segments:
                        s_x1, s_y1, s_x2, s_y2 = segment
                        x, y = dot_detween_segments(segment, [l_x1, l_y1, l_x2, l_y2])
                        if x != "Empty" and y != "Empty":
                            if (s_x1 <= x <= s_x2 or s_x2 <= x <= s_x1) and (s_y1 <= y <= s_y2 or s_y2 <= y <= s_y1):
                                # Определяем расстояние от игрока до барьера
                                end_coord.append([x, y])
                                distance.append(((l_x1 - x) ** 2 + (l_y1 - y) ** 2) ** (1/2))
            
            if len(distance) != 0:
                d_min = min(distance)
                ind_d_min = distance.index(d_min)
                # Определяем высоту барьера в пикселях
                h = HEIGHT_DISPLAY / 2 * FULL_DISTANCE / d_min
                x, y = end_coord[ind_d_min]
                s.cut_line(index, [l_x1, l_y1, x, y])
                # Верхняя часть дисплея
                c1.coords(self.display_barier[index], index * WEIGHT_DISPLAY / len(lines_now), HEIGHT_DISPLAY / 2 - h,
                                                    (index + 1) * WEIGHT_DISPLAY / len(lines_now), HEIGHT_DISPLAY / 2 + h)
            else:
                c1.coords(self.display_barier[index], index * WEIGHT_DISPLAY / len(lines_now), HEIGHT_DISPLAY / 2,
                                                    (index + 1) * WEIGHT_DISPLAY / len(lines_now), HEIGHT_DISPLAY / 2)
                                

def create_barier():
    # Первые 4 фигуры - границы мира
    bariers = [c2.create_rectangle(0, PLAYER_SIZE, PLAYER_SIZE, HEIGHT_MAP, fill="black"),
                c2.create_rectangle(0, 0, WEIGHT_MAP, PLAYER_SIZE, fill="black"),
                c2.create_rectangle(PLAYER_SIZE, HEIGHT_MAP - PLAYER_SIZE, WEIGHT_MAP, HEIGHT_MAP, fill="black"),
                c2.create_rectangle(WEIGHT_MAP - PLAYER_SIZE, PLAYER_SIZE, WEIGHT_MAP, HEIGHT_MAP - PLAYER_SIZE, fill="black"),
                c2.create_rectangle(100, 100, 150, 150, fill="black")]
    return bariers


def start_game():
    global s, x_early, angle, bariers
    angle = -math.pi * 3 / 2
    x_early = 0
    bariers = create_barier()
    s = Player(bariers)

    root.bind("<Key>", s.move)
    root.bind('<Motion>', s.change_direction)

root = Tk()
root.minsize(width=WEIGHT_DISPLAY, height=HEIGHT_DISPLAY)
root.title("Игра")

c1 = Canvas(root, width=WEIGHT_DISPLAY, height=HEIGHT_DISPLAY, bg='white', highlightbackground = "black")
c1.place(x=0, y=0)
c1.focus_set()

c2 = Canvas(root, width=WEIGHT_MAP, height=HEIGHT_MAP, bg='white', highlightbackground = "black")
c2.place(x=0, y=0)
c2.focus_set()

start_game()

root.mainloop()