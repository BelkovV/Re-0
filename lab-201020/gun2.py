from random import randrange as rnd, choice
import tkinter as tk
import math
import time

# print (dir(math))

WIDTH = 800
HEIGHT = 600

root = tk.Tk()
fr = tk.Frame(root)
root.geometry(str(WIDTH) + 'x' + str(HEIGHT))
canv = tk.Canvas(root, bg='white')
canv.pack(fill=tk.BOTH, expand=1)

badscore = 0

SPF = 0.03
G = 5
LIFETIME = 300
NUM = 5
SPEED = 2


class ball():
	def __init__(self, x=40, y=450, time=LIFETIME):
		""" Конструктор класса ball

		Args:
		x - начальное положение мяча по горизонтали
		y - начальное положение мяча по вертикали
		"""
		self.x = x
		self.y = y
		self.r = 10
		self.vx = 0
		self.vy = 0
		self.color = choice(['blue', 'green', 'red', 'brown'])
		self.id = canv.create_oval(
				self.x - self.r,
				self.y - self.r,
				self.x + self.r,
				self.y + self.r,
				fill=self.color
		)
		self.live = time

	def set_coords(self):
		canv.coords(
				self.id,
				self.x - self.r,
				self.y - self.r,
				self.x + self.r,
				self.y + self.r
		)

	def move(self):
		"""Переместить мяч по прошествии единицы времени.

		Метод описывает перемещение мяча за один кадр перерисовки. То есть, обновляет значения
		self.x и self.y с учетом скоростей self.vx и self.vy, силы гравитации, действующей на мяч,
		и стен по краям окна (размер окна 800х600).
		"""
		self.x += self.vx
		self.y -= self.vy
		self.vy -= SPF*G
		
		if self.x <= self.r or self.x >= WIDTH - self.r:
			self.vx = -self.vx
		if self.y <= self.r or self.y >= HEIGHT - self.r:
			self.vy = -self.vy

		self.live-=1

		self.set_coords()

	def hittest(self, obj):
		"""Функция проверяет сталкивалкивается ли данный обьект с целью, описываемой в обьекте obj.

		Args:
			obj: Обьект, с которым проверяется столкновение.
		Returns:
			Возвращает True в случае столкновения мяча и цели. В противном случае возвращает False.
		"""
		if (self.x - obj.x)**2 + (self.y - obj.y)**2 <= (self.r + obj.r)**2:
			return True
		return False


class gun():
	def __init__(self, xpos = 20, ypos = HEIGHT/2):
		self.f2_power = 10
		self.f2_on = 0
		self.an = 1
		self.xpos = xpos
		self.ypos = ypos
		self.endx = xpos+self.f2_power
		self.endy = ypos
		self.id = canv.create_line(self.xpos, self.ypos, self.endx, self.endy, width=7) #

	def fire2_start(self, event):
		self.f2_on = 1

	def fire2_end(self, event):
		"""Выстрел мячом.

		Происходит при отпускании кнопки мыши.
		Начальные значения компонент скорости мяча vx и vy зависят от положения мыши.
		"""
		global balls, bullet
		bullet += 1
		new_ball = ball(self.endx, self.endy)
		new_ball.r += 5
		self.an = math.atan((event.y-new_ball.y) / (event.x-new_ball.x))
		new_ball.vx = self.f2_power * math.cos(self.an)
		new_ball.vy = - self.f2_power * math.sin(self.an)
		balls += [new_ball]
		self.f2_on = 0
		self.f2_power = 10

	def targetting(self, event=0):
		"""Прицеливание. Зависит от положения мыши."""
		if event:
			self.an = math.atan((event.y-self.ypos) / (event.x-self.xpos))
		if self.f2_on:
			canv.itemconfig(self.id, fill='orange')
		else:
			canv.itemconfig(self.id, fill='black')
		self.endx = self.xpos + max(self.f2_power, 20) * math.cos(self.an)
		self.endy = self.ypos + max(self.f2_power, 20) * math.sin(self.an)
		canv.coords(self.id, self.xpos, self.ypos, self.endx, self.endy)

	def power_up(self):
		if self.f2_on:
			if self.f2_power < 100:
				self.f2_power += 1
			canv.itemconfig(self.id, fill='orange')
		else:
			canv.itemconfig(self.id, fill='black')


class target():
	def __init__(self, vx = -SPEED, vy = 0):
		self.id = canv.create_oval(0,0,0,0)
		self.new_target()
		self.vx = vx
		self.vy = vy

	def set_coords(self):
		canv.coords(
				self.id,
				self.x - self.r,
				self.y - self.r,
				self.x + self.r,
				self.y + self.r
		)

	def move(self):
		self.x += self.vx
		self.y -= self.vy
		self.set_coords()
		if self.x < -self.r:
			self.new_target()
			badscore += 1

	def new_target(self):
		""" Инициализация новой цели. """
		x = self.x = rnd(600, 780)
		y = self.y = rnd(300, 550)
		r = self.r = rnd(5, 50)
		color = self.color = 'red'
		canv.coords(self.id, x-r, y-r, x+r, y+r)
		canv.itemconfig(self.id, fill=color)

	def hit(self, points=1):
		"""Попадание шарика в цель."""
		self.new_target()


screen1 = canv.create_text(400, 300, text='', font=('Times', '24'))
g1 = gun(20, HEIGHT/2)
bullet = 0
balls = []
targets = []


for i in range(0, NUM):
	targets.append(target())


def new_game(event=''):
	global gun, targets, screen1, balls, bullet
	bullet = 0
	balls = []
	canv.bind('<Button-1>', g1.fire2_start)
	canv.bind('<ButtonRelease-1>', g1.fire2_end)
	canv.bind('<Motion>', g1.targetting)

	z = 0.03
	score = 0
	id_points = canv.create_text(30,30,text = str(score), font = ('Helvetica', '28'))

	while targets or balls:
		i = 0
		while i < len(balls):
			b = balls[i]
			b.move()
			if b.live <= 0:
				balls.pop(i)
				canv.delete(b.id)
				bullet -= 1
			else:
				i+=1
			for tg in targets:
				if b.hittest(tg):
					score += int(50/tg.r)
					tg.hit()
					canv.itemconfig(id_points, text=str(score))
		for tg in targets:
			tg.move()

		canv.update()
		time.sleep(SPF)
		g1.targetting()
		g1.power_up()
	canv.itemconfig(screen1, text='')
	canv.delete(gun)
	root.after(750, new_game)


new_game()

#mainloop()
