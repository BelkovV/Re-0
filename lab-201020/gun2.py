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
canv = tk.Canvas(root, bg='black')
canv.pack(fill=tk.BOTH, expand=1)

FPS = 30
G = 5
LIFETIME = 300
NUM = 5
SPEED = 160
MAX_BULLETS = 5
MAX_MISSES = 1
DoGravityAffectTargets = 0.1

def rgb_to_string(rgb):
	d = {10: 'a', 11: 'b', 12: 'c', 13: 'd', 14: 'e', 15: 'f'}
	for i in range(10):
		d[i] = str(i)
	res = '#'
	for num in rgb:
		res += d[num//16]
		res += d[num%16]
	return res


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
		self.color = choice(['blue', 'green', 'random', 'brown'])
		if self.color == 'random':
			self.color = rgb_to_string((rnd(0, 255), rnd(0, 255), rnd(0, 255)))
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
		self.x += self.vx/FPS
		self.y -= self.vy/FPS
		self.vy -= G
		
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
		if bullet < MAX_BULLETS:
			bullet += 1
			new_ball = ball(self.endx, self.endy)
			new_ball.r += 5
			self.targetting(event)
			new_ball.vx = self.f2_power * FPS * math.cos(self.an)
			new_ball.vy = - self.f2_power * FPS * math.sin(self.an)
			balls += [new_ball]
		self.f2_on = 0
		self.f2_power = 10

	def targetting(self, event=0):
		"""Прицеливание. Зависит от положения мыши."""
		if event:
			if event.x!=self.xpos:
				self.an = math.atan((event.y-self.ypos) / (event.x-self.xpos))
				if event.x < self.xpos:
					self.an = math.pi + self.an
			elif event.y > self.ypos:
				self.an = math.pi/2
			else:
				self.an = -math.pi/2
		if self.f2_on:
			canv.itemconfig(self.id, fill='orange')
		else:
			canv.itemconfig(self.id, fill='white')
		
		self.endx = self.xpos + max(self.f2_power, 20) * math.cos(self.an)
		self.endy = self.ypos + max(self.f2_power, 20) * math.sin(self.an)
		
		canv.coords(self.id, self.xpos, self.ypos, self.endx, self.endy)

	def power_up(self):
		if self.f2_on:
			if self.f2_power < 100:
				self.f2_power += 1
			canv.itemconfig(self.id, fill='orange')
		else:
			canv.itemconfig(self.id, fill='white')


class target():
	def __init__(self, vx = -SPEED, vy = 0):
		self.id = canv.create_oval(0,0,0,0)
		self.vx = vx
		self.vy = vy
		self.new_target()

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
		self.y -= self.vy/FPS
		self.vy -= G*DoGravityAffectTargets
		self.set_coords()
		
		if self.x >= WIDTH - self.r:
			self.vx = -self.vx
		if self.y <= self.r or self.y >= HEIGHT - self.r:
			self.vy = -self.vy
		
		if self.x < -self.r:
			self.new_target()
			return 1
		return 0

	def new_target(self):
		""" Инициализация новой цели. """
		x = self.x = rnd(600, 780)
		y = self.y = rnd(300, 550)
		r = self.r = rnd(5, 50)
		
		self.vx = rnd(-SPEED, SPEED)
		self.vy = rnd(-SPEED, SPEED)
		
		color = self.color = 'red'
		canv.coords(self.id, x-r, y-r, x+r, y+r)
		canv.itemconfig(self.id, fill=color)

	def hit(self, points=1):
		"""Попадание шарика в цель."""
		self.new_target()


bullet = 0
badscore = 0
balls = []

def restart(event=0):
	global badscore, balls
	if badscore > -MAX_MISSES:
		badscore = 0
		for b in balls:
			canv.delete(b.id)
		balls = []
		new_game()
	print(event.keycode)
		

def new_game(event=''):
	global balls, bullet, badscore
	g1 = gun(20, HEIGHT/2)
	bullet = 0
	balls = []
	targets = []
	for i in range(0, NUM):
		targets.append(target())
	canv.bind('<Button-1>', g1.fire2_start)
	canv.bind('<ButtonRelease-1>', g1.fire2_end)
	canv.bind('<Motion>', g1.targetting)
	canv.bind('<KeyPress>', restart)

	z = 0.03
	score = 0
	text_left = canv.create_text(30,30,text = str(score), font = ('Helvetica', '28'), fill='white')
	text_right = canv.create_text(WIDTH-30,30,text = str(score), font = ('Helvetica', '28'), fill='red')
	text_center = canv.create_text(WIDTH/2,30,text = str(bullet), font = ('Times', '28'), fill='#00cc00')

	while not MAX_MISSES or badscore < MAX_MISSES:
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
					canv.itemconfig(text_left, text=str(score))
		for tg in targets:
			badscore += tg.move()
			canv.itemconfig(text_right, text=str(badscore))

		center_color = '#00cc00'
		if bullet >= 5:
			center_color = '#cc0000'
		canv.itemconfig(text_center, text=str(bullet), fill=center_color)
		
		
		canv.update()
		time.sleep(1/FPS)
		g1.targetting()
		g1.power_up()
		
	canv.itemconfig(text_center, text='Game Over', fill='#cc0000')
	canv.update()
	time.sleep(10)
	
	canv.delete(gun)
	print(score)
	#root.after(750, new_game)


new_game()

#mainloop()
