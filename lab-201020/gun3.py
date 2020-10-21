from random import randrange as rnd, choice
import tkinter as tk
import math
import time

WIDTH = 800
HEIGHT = 600

root = tk.Tk()
fr = tk.Frame(root)
root.geometry(str(WIDTH) + 'x' + str(HEIGHT))
canv = tk.Canvas(root, bg='black')
canv.pack(fill=tk.BOTH, expand=1)

FPS = 40
G = 150 #Gravity, px/sec^2
LIFETIME = 10 #Bullet lifetime, sec
NUM = 5 #Number of targets
SPEED = 160 #Maximum target start speed, px/sec
MAX_BULLETS = 5 #Maximum number of bullets allowed
MAX_MISSES = 3 #Targets to miss until gameover
DoGravityAffectTargets = 0.1

RED = '#cc0000'
GREEN = '#00cc00'
FONT = ('Helvetica', '28')
END_LINE = ['Game Over', 'Press F to continue']

def rgb_to_string(rgb):
	d = {10: 'a', 11: 'b', 12: 'c', 13: 'd', 14: 'e', 15: 'f'}
	for i in range(10):
		d[i] = str(i)
	res = '#'
	for num in rgb:
		res += d[num//16]
		res += d[num%16]
	return res


class Ball():
	def __init__(self, x=40, y=450, time=LIFETIME*FPS):
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
		self.vy -= G/FPS
		
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


class Gun():
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

	def fire2_end(self, event, bullet):
		"""Выстрел мячом.

		Происходит при отпускании кнопки мыши.
		Начальные значения компонент скорости мяча vx и vy зависят от положения мыши.
		"""
		self.f2_on = 0
		if bullet < MAX_BULLETS:
			new_ball = Ball(self.endx, self.endy)
			new_ball.r += 5
			self.targetting(event)
			new_ball.vx = self.f2_power * FPS * math.cos(self.an)
			new_ball.vy = - self.f2_power * FPS * math.sin(self.an)
			self.f2_power = 10
			return new_ball
		self.f2_power = 10
		return None

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


class Target():
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
		self.vy -= G*DoGravityAffectTargets/FPS
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

class Game():
	def __init__(self, gun_coords, num_targets = NUM):
		self.gun = Gun(gun_coords[0], gun_coords[1])
		self.balls = []
		self.targets = []
		for i in range(0, NUM):
			self.targets.append(Target())
		self.score = 0
		self.badscore = 0
		self.num_bullets = 0
		self.finished = False
		self.just_finished = False
	
	def update_gun(self, event):
		self.gun.targetting(event)
	
	def fire_start(self, event):
		canv.focus_set()
		self.gun.fire2_start(event)
		
	def shoot(self, event):
		new_ball = self.gun.fire2_end(event, self.num_bullets)
		if new_ball != None:
			self.balls.append(new_ball)
			self.num_bullets+=1
		
	def tick(self):
		i = 0
		while i < len(self.balls):
			b = self.balls[i]
			b.move()
			
			if b.live <= 0: # Ball is Dead
				self.balls.pop(i)
				canv.delete(b.id)
				self.num_bullets -= 1
			else:
				i+=1
			
			for tg in self.targets: # Detect Collision
				if b.hittest(tg):
					self.score += int(50/tg.r)
					tg.hit()
					
		for tg in self.targets:
			self.badscore += tg.move()
			
		self.gun.power_up()

	def restart(self, event):
		self.badscore = 0
		for b in self.balls:
			canv.delete(b.id)
		self.balls = []
		self.num_bullets = 0
		for tg in self.targets:
			tg.new_target()
	
	def close(self, event=0):
		self.finished = True
	
	def close_on_x(self, event):
		if event.char == 'x':
			self.close()
		
	def key_detect(self, event):
		if event.char == 'f':
			self.restart(event)
			canv.bind("<Key>", self.close_on_x)
			self.just_finished = False
		else:
			self.close()
		
def key(event):
    print ("pressed", repr(event.char))

def new_game(event=''):
	g = Game((20, HEIGHT/2), NUM)

	canv.bind('<Button-1>', g.fire_start)
	canv.bind('<ButtonRelease-1>', g.shoot)
	canv.bind('<Motion>', g.update_gun)
	canv.bind('<Key>', g.close_on_x)

	text_left = canv.create_text(30,30,text = str(g.score), font = FONT, fill='white')
	text_right = canv.create_text(WIDTH-30,30,text = str(g.badscore), font = FONT, fill='red')
	text_center = [canv.create_text(WIDTH/2,30,text = str(g.num_bullets), font = FONT, fill=GREEN)]
	
	just_finished = False

	while not g.finished:
		if not MAX_MISSES or g.badscore < MAX_MISSES:
			g.tick()
			canv.itemconfig(text_left, text=str(g.score)) #Updating scores
			canv.itemconfig(text_right, text=str(g.badscore))

			center_color = GREEN
			if g.num_bullets >= MAX_BULLETS:
				center_color = RED
			
			canv.itemconfig(text_center[0], text=str(g.num_bullets), fill=center_color)
			for line in text_center[1:]:
				canv.itemconfig(line, text='')
			
			g.gun.targetting()
		else:
			if not g.just_finished:
				canv.bind("<Key>", g.key_detect)
				g.just_finished = True
				
				i = 0
				for line in END_LINE: # Printing end lines
					if i < len(text_center):
						canv.itemconfig(text_center[i], text=line, fill=RED)
					else:
						new_line = canv.create_text(WIDTH/2, (i+1)*30, text = line, font = FONT, fill=RED)
						text_center.append(new_line)
					i+=1
					
		canv.update()
		time.sleep(1/FPS)
	
	canv.delete(g.gun)
	print(g.score)

new_game()
