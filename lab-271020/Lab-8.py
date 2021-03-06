from random import randrange as rnd, choice
import tkinter as tk
import math
import time

WIDTH = 800
HEIGHT = 600
FPS = 30

#targets
R_MIN = 10
R_MAX = 50
V_MAX = 210

NUM_TARGS = 4
NUM_BLACK = 2

#balls
G = 300
LIFETIME = 10

#gun
LEN_TO_SPEED = 30
MIN_POWER = 10
MAX_POWER = 100
POWER_V = 30

root = tk.Tk()
fr = tk.Frame(root)
root.geometry(str(WIDTH) + 'x' + str(HEIGHT))
canv = tk.Canvas(root, bg='white')
canv.pack(fill=tk.BOTH, expand=1)

class Sphere():
	def __init__(self, x=0, y=0, r=0, vx=0, vy=0, color='red'):
		self.x = x
		self.y = y
		self.r = r
		self.vx = vx
		self.vy = vy
		self.color = color
		self.id = canv.create_oval(
				self.x - self.r,
				self.y - self.r,
				self.x + self.r,
				self.y + self.r,
				fill=self.color
		)
		self.locked_x = 0
		self.locked_y = 0
		self.live = 1

	def set_coords(self):
		canv.coords(
				self.id,
				self.x - self.r,
				self.y - self.r,
				self.x + self.r,
				self.y + self.r
		)
	
	def move(self):
		self.x += self.vx/FPS
		self.y += self.vy/FPS
		self.set_coords()

	def check_walls(self):
		if not self.locked_y and (self.y + self.r >= HEIGHT or self.y <= self.r): 
			self.vy *= -1
			self.locked_y = 5
		if not self.locked_x and (self.x + self.r >= WIDTH or self.x <= self.r): 
			self.vx *= -1
			self.locked_x = 5
		if self.locked_y:
			self.locked_y -= 1
		if self.locked_x:
			self.locked_x -= 1

	def delete(self):
		canv.delete(self.id)
		return False
	

class Ball(Sphere):
	def __init__(self, x=40, y=450, vx=10, vy=10):
		""" Конструктор класса ball

		Args:
		x - начальное положение мяча по горизонтали
		y - начальное положение мяча по вертикали
		"""
		color = choice(['blue', 'green', 'red', 'brown'])
		Sphere.__init__(self, x, y, 10, vx, vy, color)
		self.live = LIFETIME * FPS
		self.g = G

	def move(self):
		"""Переместить мяч по прошествии единицы времени.

		Метод описывает перемещение мяча за один кадр перерисовки. То есть, обновляет значения
		self.x и self.y с учетом скоростей self.vx и self.vy, силы гравитации, действующей на мяч,
		и стен по краям окна (размер окна 800х600).
		"""
		Sphere.move(self)
		Sphere.check_walls(self)
		self.vy += self.g/FPS
		self.live -= 1
		if self.live <= 0:
			self.delete()


	def hittest(self, obj):
		"""Функция проверяет сталкивалкивается ли данный обьект с целью, описываемой в обьекте obj.

		Args:
			obj: Обьект, с которым проверяется столкновение.
		Returns:
			Возвращает True в случае столкновения мяча и цели. В противном случае возвращает False.
		"""
		if ((self.x - obj.x)**2+(self.y - obj.y)**2) < (self.r+obj.r)**2:
			return True
		return False


class Gun():
	def __init__(self, x = 20, y = 450):
		self.x = x
		self.y = y
		self.f2_power = MIN_POWER
		self.f2_on = 0
		self.an = 1
		self.endx = self.x + self.f2_power
		self.endy = self.y
		self.id = canv.create_line(self.x, self.y, self.endx, self.endy, width=7)

	def fire2_start(self, event):
		canv.focus_set()
		self.f2_on = 1

	def fire2_end(self, event):
		"""Выстрел мячом.

		Происходит при отпускании кнопки мыши.
		Начальные значения компонент скорости мяча vx и vy зависят от положения мыши.
		"""
		self.an = math.atan((event.y-450) / (event.x-40))

		vx = self.f2_power * math.cos(self.an) * LEN_TO_SPEED
		vy = - self.f2_power * math.sin(self.an) * LEN_TO_SPEED

		new_ball = Ball(self.endx, self.endy, vx, -vy)
		new_ball.r += 5
		self.f2_on = 0
		self.f2_power = MIN_POWER
		return new_ball

	def targetting(self, event=0):
		"""Прицеливание. Зависит от положения мыши."""
		if event:
			self.an = math.atan((event.y-self.y) / (event.x-self.x))
		if self.f2_on:
			canv.itemconfig(self.id, fill='orange')
		else:
			canv.itemconfig(self.id, fill='black')
		self.endx = self.x + max(self.f2_power, 20) * math.cos(self.an)
		self.endy = self.y + max(self.f2_power, 20) * math.sin(self.an)
		canv.coords(self.id, self.x, self.y, self.endx, self.endy)

	def power_up(self):
		if self.f2_on:
			if self.f2_power < MAX_POWER:
				self.f2_power += POWER_V/FPS
			canv.itemconfig(self.id, fill='orange')
		else:
			canv.itemconfig(self.id, fill='black')


class Target(Sphere):
	def __init__(self):
		Sphere.__init__(self)
		self.points = 0
		self.new_target()
		
	def move(self):
		Sphere.move(self)
		Sphere.check_walls(self)

	def new_target(self):
		""" Инициализация новой цели. """
		self.x = rnd(WIDTH//2, WIDTH - R_MAX)
		self.y = rnd(HEIGHT//2, HEIGHT - R_MAX)
		self.r = rnd(R_MIN, R_MAX)
		self.set_coords()
		self.vx = rnd(-V_MAX, V_MAX)
		self.vy = rnd(-V_MAX, V_MAX)

	def hit(self, obj, points=-1):
		"""Попадание шарика в цель."""
		if points == -1:
			points = R_MAX//self.r
		self.points += points
		self.new_target()
		return points
		

class BlackTarget(Target):
	def __init__(self):
		Sphere.__init__(self)
		self.points = 0
		self.mark_configure()
		self.mark_id = canv.create_polygon(self.point_list, fill = '#f11')
		self.new_target()
	
	def new_target(self):
		Target.new_target(self)
		color = self.color = 'black'
		canv.itemconfig(self.id, fill=color)
		
	def mark_configure(self):
		x = self.x
		y = self.y
		r = self.r/2
		self.point_list = [x-r, y, x, y-r, x+r, y, x, y+r]
		
	def set_coords(self):
		Target.set_coords(self)
		self.mark_configure()
		canv.coords(self.mark_id, *self.point_list)
	
	def hit(self, obj):
		Target.hit(self, obj)
		obj.vx *= -1
		obj.vy *= -1
		self.live = 0
		
	def delete(self):
		Sphere.delete(self)
		canv.delete(self.mark_id)


class Game():
	def __init__(self):
		self.gun = Gun()
		self.bullet = 0
		self.balls = []
		self.targets = [BlackTarget() for i in range(NUM_BLACK)]
		self.targets += [Target() for i in range(NUM_TARGS)]
		self.id_points = canv.create_text(30, 30, text = '0', font = ('Times', '28'))
		self.live = True

	def shoot(self, event):
		new_ball = self.gun.fire2_end(event)
		self.balls.append(new_ball)
		self.bullet += 1
		
	def tick(self):
		score = 0
		i = 0
		while i < len(self.balls):
			b = self.balls[i]
			b.move()
			if b.live <= 0:
				self.balls.pop(i)
			else:
				for t in self.targets:
					if b.hittest(t):
						t.hit(b)
				i+=1
		i = 0
		while i < len(self.targets):
			t = self.targets[i]
			score += t.points
			if t.live == 0:
				self.targets.pop(i)
				t.delete()
			else:
				i += 1
				t.move()
		canv.itemconfig(self.id_points, text = str(score))
		canv.update()
		self.gun.targetting()
		self.gun.power_up()
	
	def keypress(self, event):
		if event.char == 'x':
			self.end()
	
	def end(self):
		self.live = False

def new_game():
	game = Game()
	canv.bind('<Button-1>', game.gun.fire2_start)
	canv.bind('<ButtonRelease-1>', game.shoot)
	canv.bind('<Motion>', game.gun.targetting)
	canv.bind('<Key>', game.keypress)

	while game.live:
		game.tick()
		time.sleep(1/FPS)

new_game()
