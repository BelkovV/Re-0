from random import randrange as rnd, choice
import tkinter as tk
import math
import time

##preferences
#game
WIDTH = 1200
HEIGHT = 800
FPS = 30
MAGICTIME = 5

#targets
R_MIN = 10
R_MAX = 50
V_MAX = 210
NUM_TARGS = 2
mark_colors = ['red', 'white']

#clouds
cloud_colors = ['#ffa', '#faf', '#aff']
dark_cloud_colors = ['#994', '#949', '#499']
cloud_points = 15

#balls
G = 300
LIFETIME = 10
BALL_R = 15
BOMB_R = 10
MAX_BALLS = 5
ball_colors = ['blue', 'green', 'tan', 'brown']

#gun
LEN_TO_SPEED = 30
MIN_POWER = 10
MAX_POWER = 100
POWER_V = 30

#game screen
root = tk.Tk()
fr = tk.Frame(root)
root.geometry(str(WIDTH) + 'x' + str(HEIGHT))
canv = tk.Canvas(root, bg='white')
canv.pack(fill=tk.BOTH, expand=1)

class Sphere(): # Parent class for everything round
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
		self.isInvulnerable = False # If true, an object won't be consumed by bombs and reflected from walls

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
		if not self.isInvulnerable:
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
		if (self.y >= 2*HEIGHT or self.y <= -HEIGHT or self.x >= 2*WIDTH or self.x <= -WIDTH):
			self.delete()

	def delete(self):
		canv.delete(self.id)
		self.live = 0
		return False
	
	def get_score(self):
		return 1
		
	def hit(self, obj):
		"""Функция проверяет сталкивалкивается ли данный обьект с целью, описываемой в обьекте obj.

		Args:
			obj: Обьект, с которым проверяется столкновение.
		Returns:
			Возвращает True в случае столкновения мяча и цели. В противном случае возвращает False.
		"""
		if ((self.x - obj.x)**2+(self.y - obj.y)**2) < (self.r+obj.r)**2:
			return True
		return False
	

class Ball(Sphere):
	def __init__(self, x=40, y=450, vx=10, vy=10):
		""" Конструктор класса ball

		Args:
		x - начальное положение мяча по горизонтали
		y - начальное положение мяча по вертикали
		"""
		color = choice(ball_colors)
		Sphere.__init__(self, x, y, BALL_R, vx, vy, color)
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


class Gun():
	def __init__(self, x = 20, y = 450):
		self.x = x
		self.y = y
		self.r = self.f2_power = MIN_POWER
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
		if event.x - self.x != 0:
			self.an = math.atan((event.y-self.y) / (event.x-self.x))
		elif event.y > self.y:
			self.an = math.pi/2
		else:
			self.an = -math.pi/2

		vx = self.f2_power * math.cos(self.an) * LEN_TO_SPEED
		vy = - self.f2_power * math.sin(self.an) * LEN_TO_SPEED

		new_ball = Ball(self.endx, self.endy, vx, -vy)
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

#Targets
class Target(Sphere): #Classic target, randomly changes itself when hit, so there is always NUM_TARGS of them
	def __init__(self):
		Sphere.__init__(self)
		self.new_target()
		
	def move(self):
		Sphere.move(self)
		Sphere.check_walls(self)

	def new_target(self):
		""" Инициализация новой цели. """
		self.x = rnd(WIDTH//2, WIDTH - R_MAX)
		self.y = rnd(R_MAX, HEIGHT - R_MAX)
		self.r = rnd(R_MIN, R_MAX)
		self.set_coords()
		self.vx = rnd(-V_MAX, V_MAX)
		self.vy = rnd(-V_MAX, V_MAX)

	def get_score(self):
		return R_MAX//self.r

	def hit(self, obj):
		"""Попадание шарика в цель."""
		if Sphere.hit(self, obj):
			self.new_target()
			return self.get_score()
		

class BlackTarget(Target): #Olya's Target, the ball reflects from it
	def __init__(self):
		Sphere.__init__(self)
		self.mark_configure()
		self.set_color()
		self.mark_id = canv.create_polygon(self.point_list, fill = self.mark_color)
		self.new_target()
		self.modifier = 3
	
	def set_color(self):
		self.mark_color = choice(mark_colors + ball_colors + cloud_colors)
	
	def new_target(self):
		Target.new_target(self)
		self.color = 'black'
		canv.itemconfig(self.id, fill=self.color)
		
	def mark_configure(self):
		x = self.x
		y = self.y
		r = self.r/2
		self.point_list = [x-r, y, x, y-r, x+r, y, x, y+r]
		
	def set_coords(self):
		Target.set_coords(self)
		self.mark_configure()
		canv.coords(self.mark_id, *self.point_list)
	
	def get_score(self):
		return self.modifier*Target.get_score(self)
	
	def hit(self, obj):
		if Target.hit(self, obj):
			obj.vx *= -1
			obj.vy *= -1
			self.live = 0
			if obj.color == self.color:
				self.modifier *= 15
			return self.get_score()
		
	def delete(self):
		Sphere.delete(self)
		canv.delete(self.mark_id)


def draw_cloud(x, y, r, color):
	res = []
	res.append(canv.create_oval(x - 8*r, y - 2*r, x - 3*r, y + 3*r, fill = color, outline = color))
	res.append(canv.create_oval(x - 5*r, y - 4*r, x - r, y, fill = color, outline = color))
	res.append(canv.create_oval(x - 3*r, y - 6*r, x + 5*r, y + 2*r, fill = color, outline = color))
	res.append(canv.create_oval(x + 2*r, y - 2*r, x + 7*r, y + 3*r, fill = color, outline = color))
	res.append(canv.create_oval(x - 5*r, y - 2*r, x + 4*r, y + 3*r, fill = color, outline = color))
	return res
		
class Cloud(): #A cloud that will grant reverse gravity to balls it hits. Gives the most points
	def __init__(self):
		self.x = WIDTH
		self.y = rnd(HEIGHT//6, HEIGHT//3)
		self.vx = rnd(-V_MAX, -V_MAX//3)
		self.vy = 0
		self.r = rnd(16, 48)
		self.set_color()
		self.id = draw_cloud(self.x, self.y, self.r/8, self.color)
		self.live = 1
		self.isInvulnerable = False
		
	def set_color(self):
		self.color = choice(cloud_colors)
	
	def move(self):
		for item in self.id:
			itemcoords = canv.coords(item)
			for i in range(len(itemcoords)):
				if i%2 == 0:
					itemcoords[i] += self.vx/FPS
				else:
					itemcoords[i] += self.vy/FPS
			canv.coords(item, *itemcoords)
		
		self.x += self.vx/FPS
		self.y += self.vy/FPS
		if self.x < -self.r:
			self.delete()
			self.live = 0
		self.drop()
	
	def drop(self):
		pass
	
	def delete(self):
		for item in self.id:
			canv.delete(item)
	
	def get_score(self):
		return int(cloud_points*(1 + (48 - self.r)/8))
	
	def hit(self, obj):
		if Sphere.hit(self, obj):
			obj.g *= -2
			self.live = 0
			obj.color = self.color
			canv.itemconfig(obj.id, fill = obj.color)
			return self.get_score()
		return 0

class Bomb(Ball): #These will destroy objects they land on
	def __init__(self, parent):
		Ball.__init__(self, parent.x, parent.y)
		self.parent = parent
		self.r = 10
		self.isInvulnerable = True
		
	def set_color(self, color):
		self.color = color
		canv.itemconfig(self.id, fill = self.color)
	
	def blow_up(self):
		self.delete()
		self.parent.game.score -= cloud_points
	
	def get_score(self):
		return -1
		
	def hit(self, obj):
		if Sphere.hit(self, obj):
			obj.delete()
			return -1
			
	def move(self):
		Ball.move(self)
		for t in self.parent.game.targets:
			if (t.id != self.id) and (t.id != self.parent.id) and not t.isInvulnerable:
				t.hit(self)
		if (self.x <= self.parent.game.gun.x) and (self.y <= self.parent.game.gun.y):
			self.blow_up()


class DarkCloud(Cloud): # These will bomb the playing field
	def __init__(self, game):
		Cloud.__init__(self)
		self.game = game
		
	def set_color(self):
		self.color = choice(dark_cloud_colors)
	
	def get_score(self):
		return -1
	
	def hit(self, obj):
		res = Cloud.hit(self, obj)
		if res:
			obj.g *= -1
			return -1
	
	def drop(self):
		if (self.x <= self.game.gun.x) or (self.game.time % FPS == 0):
			bomb = Bomb(self)
			bomb.set_color(self.color)
			self.game.targets.append(bomb)
	

def gravitate(obj1, obj2):
	r = ((obj2.x - obj1.x)**2 + (obj2.y - obj1.y)**2)**0.5
	k = 2*obj1.r*obj2.r*obj2.g/(r**3)
	obj1.vx += k*(obj2.x - obj1.x)
	obj1.vy += k*(obj2.y - obj1.y)

class Enemy(Target): # This object eats the playing field habitants
	def __init__(self, game):
		self.game = game
		Target.__init__(self)
		self.g = G/3
		self.color = 'black'
		canv.itemconfig(self.id, fill = self.color)
		self.score = 1
		self.vx = 0
		self.vy = 0
		self.isInvulnerable = True
	
	def move(self):
		for t in self.game.targets:
			if t.id != self.id:
				if self.hittest(t) and self.g > 0:
					t.hit(self)
					self.eat(t)
				else:
					gravitate(t, self)
		self.set_coords()
		self.r -= 50/(FPS*self.r)
		if self.r <= 0:
			self.delete()
			
		if self.g < 0 and self.r > 5:
			if not rnd(0, FPS):
				self.spit()
	
	def spit(self): # And also spits them out if feeded a cloud
		magic_id = rnd(0, 4)
		if magic_id == 0:
			spiff = Ball()
		elif magic_id == 1:
			spiff = Target()
		elif magic_id == 2:
			spiff = BlackTarget()
		elif magic_id == 3:
			spiff = Bomb(self)
			spiff.set_color(self.color)
		spiff.x = rnd(int(self.x - self.r), int(self.x + self.r))
		spiff.y = rnd(int(self.y - self.r), int(self.y + self.r))
		spiff.vx = 0
		spiff.vy = 0
		spiff.isInvulnerable = True
		self.game.targets.append(spiff)
	
	def hittest(self, obj):
		if ((self.x - obj.x)**2+(self.y - obj.y)**2) < (self.r/2 + obj.r)**2:
			return True
		return False
	
	def eat(self, obj):
		self.r = (self.r**2 + obj.r**2)**0.5
		self.score += obj.get_score()
	
	def get_score(self):
		return self.score
	
	def hit(self, obj):
		dice = rnd(0, 3)
		if self.hittest(obj):
			if not dice:
				self.delete()
				self.live = 0
				return self.get_score()
			self.eat(obj)
			obj.delete()
		gravitate(obj, self)


class Game():
	def __init__(self, x = 20, y = 3*HEIGHT/4):
		self.gun = Gun(x, y)
		self.bullet = 0
		self.balls = []
		self.targets = []
		self.targets += [Target() for i in range(NUM_TARGS)]
		self.id_points = canv.create_text(30, 30, text = '0', font = ('Times', '28'))
		self.id_balls_num = canv.create_text(WIDTH/2, 30, text = '0', font = ('Times', '28'))
		self.live = True
		self.score = 0
		self.time = 0
		
	def get_ready(self, event):
		canv.focus_set()
		if self.bullet < MAX_BALLS:
			self.gun.fire2_start(event)

	def shoot(self, event):
		if self.bullet < MAX_BALLS:
			new_ball = self.gun.fire2_end(event)
			self.balls.append(new_ball)
			self.bullet += 1
			
	def count_update(self):
		color = 'black'
		if self.bullet == MAX_BALLS:
			color = 'red'
		canv.itemconfig(self.id_balls_num, text = str(self.bullet), fill = color)
		canv.itemconfig(self.id_points, text = str(int(self.score)))
		canv.update()
		
	def tick(self):
		i = 0
		while i < len(self.balls):
			b = self.balls[i]
			b.move()
			if b.live <= 0:
				self.balls.pop(i)
				self.bullet -= 1
			else:
				for t in self.targets:
					if t.hit(b):
						self.score += t.get_score()
				i+=1
		i = 0
		while i < len(self.targets):
			t = self.targets[i]
			if t.live == 0:
				self.targets.pop(i)
				t.delete()
			else:
				i += 1
				t.move()
				
		if self.time % int(MAGICTIME * FPS) == 0:
			self.magic()
		
		self.count_update()
		self.gun.targetting()
		self.gun.power_up()
		self.time += 1
		
	def magic(self, magic_id = -1):
		if magic_id < 0:
			magic_id = rnd(0, 60)
		if magic_id < 30:
			missile = BlackTarget()
		elif magic_id < 45:
			missile = Cloud()
		elif magic_id < 55:
			missile = DarkCloud(self)
		elif magic_id < 60:
			missile = Enemy(self)
		self.targets.append(missile)
		return missile
	
	def delete_all_balls(self):
		for b in self.balls:
			b.delete()
		balls = []
	
	def keypress(self, event):
		if event.char == 'x':
			self.end()
		if event.char == 'd':
			self.delete_all_balls()
		if event.char == 'e':
			self.targets = [Enemy(self)] + self.targets
			self.targets[0].x = WIDTH/2
			self.targets[0].y = HEIGHT/2
			self.targets[0].set_coords()
			self.targets[0].g *= -1
	
	def end(self):
		self.live = False

def new_game():
	game = Game()
	canv.bind('<Button-1>', game.get_ready)
	canv.bind('<ButtonRelease-1>', game.shoot)
	canv.bind('<Motion>', game.gun.targetting)
	canv.bind('<Key>', game.keypress)
	
	while game.live:
		game.tick()
		time.sleep(1/FPS)

new_game()
