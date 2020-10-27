from random import randrange as rnd, choice
import tkinter as tk
import math
import time

WIDTH = 800
HEIGHT = 600
NUM_TARGS = 2
FPS = 30
R_MIN = 10
R_MAX = 50
V_MAX = 210

root = tk.Tk()
fr = tk.Frame(root)
root.geometry(str(WIDTH) + 'x' + str(HEIGHT))
canv = tk.Canvas(root, bg='white')
canv.pack(fill=tk.BOTH, expand=1)

class Sphere():
	def __init__(self, x=0, y=0, r=0, vx=0, vy=0, color='black'):
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
		if self.y + self.r >= HEIGHT or self.y <= self.r: 
			self.vy *= -1
		if self.x + self.r >= WIDTH or self.x <= self.r: 
			self.vx *= -1

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
		self.live = 30

	def move(self, g = 3):
		"""Переместить мяч по прошествии единицы времени.

		Метод описывает перемещение мяча за один кадр перерисовки. То есть, обновляет значения
		self.x и self.y с учетом скоростей self.vx и self.vy, силы гравитации, действующей на мяч,
		и стен по краям окна (размер окна 800х600).
		"""
		Sphere.move(self)
		Sphere.check_walls(self)
		self.vy += g


	def hittest(self, obj):
		"""Функция проверяет сталкивалкивается ли данный обьект с целью, описываемой в обьекте obj.

		Args:
			obj: Обьект, с которым проверяется столкновение.
		Returns:
			Возвращает True в случае столкновения мяча и цели. В противном случае возвращает False.
		"""
		if ((self.x - obj.x)**2+(self.y - obj.y)**2) < (self.r+obj.r)**2:  
			self.vx *= -1		 
			self.vy *= -1  
			return True
		return False


class Gun():
	def __init__(self, power = 10, on = 0, an = 1):
		self.x = 20
		self.y = 450
		self.f2_power = 10
		self.f2_on = 0
		self.an = 1
		self.endx = self.x + self.f2_power
		self.endy = self.y
		self.id = canv.create_line(self.x, self.y, self.endx, self.endy, width=7)

	def fire2_start(self, event):
		self.f2_on = 1

	def fire2_end(self, event):
		"""Выстрел мячом.

		Происходит при отпускании кнопки мыши.
		Начальные значения компонент скорости мяча vx и vy зависят от положения мыши.
		"""
		global balls, bullet
		bullet += 1
		self.an = math.atan((event.y-450) / (event.x-40))

		vx = self.f2_power * math.cos(self.an) * 30
		vy = - self.f2_power * math.sin(self.an) * 30

		new_ball = Ball(self.endx, self.endy, vx, -vy)
		new_ball.r += 5
		balls += [new_ball]
		self.f2_on = 0
		self.f2_power = 10

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
			if self.f2_power < 100:
				self.f2_power += 1
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
		color = self.color = 'black'
		canv.itemconfig(self.id, fill=color)

	def hit(self, points=1):
		"""Попадание шарика в цель."""
		canv.coords(self.id, -10, -10, -10, -10)
		self.points += points


g1 = Gun()
bullet = 0
balls = []
targets = [Target() for i in range(NUM_TARGS)]


def new_game(event=''):
	global gun, targets, balls, bullet
	for t in targets:
		t.new_target()
		t.live = 1
	bullet = 0
	balls = []
	canv.bind('<Button-1>', g1.fire2_start)
	canv.bind('<ButtonRelease-1>', g1.fire2_end)
	canv.bind('<Motion>', g1.targetting)
	
	id_points = canv.create_text(30,30, text = '0', font = ('Times', '28'))
	
	while True:
		score = 0
		for t in targets:
			score += t.points
			t.move()
		for b in balls:
			b.move()
			for t in targets:
				if b.hittest(t):
					t.hit()
					t.new_target()
		canv.itemconfig(id_points, text = str(score))
		canv.update()
		time.sleep(1/FPS)
		g1.targetting()
		g1.power_up()
	canv.itemconfig(screen1, text='')
	canv.delete(gun)
	root.after(750, new_game)


new_game()
tk.mainloop()
