from pygame import *
from random import randint

init()
font.init()

class GameSprite(sprite.Sprite):
    def __init__(self, image_path, coord, size=(65, 65)):
        super().__init__()
        self.size = size
        self.image = transform.scale(image.load(image_path), self.size)
        self.rect = self.image.get_rect()
        self.rect.x = coord[0]
        self.rect.y = coord[1]

    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

class Player(GameSprite):
    def __init__(self, filename, key_set: list, coord: list, speed=0, tick=0):
        super().__init__(filename, coord)
        self.key_LEFT = key_set[0]
        self.key_RIGHT = key_set[1]
        self.speed = speed
        self.last_tick = tick
        self.ShootingSpeed = 2.0
        self.buffedTick = tick
        self.lifes: int = 1

    def fire(self):
        new = Bullet('bullet.png', (self.rect.centerx-15, self.rect.y+5), size=(30, 60))
        bullets.add(new)
        fire.play()

    def update(self):
        buttons = key.get_pressed()
        if buttons[self.key_LEFT] and self.rect.x >= 0:
            self.rect.x -= self.speed
        if buttons[self.key_RIGHT] and self.rect.x <= 630:
            self.rect.x += self.speed
        if mouse.get_pressed()[0] and tick-self.last_tick >= 60/self.ShootingSpeed:
            self.last_tick = tick
            self.fire()
        if tick-self.buffedTick>=480:
            self.buffedTick = tick
            self.ShootingSpeed=2.0

class Enemy(GameSprite):
    speed = randint(1, 2)
    def update(self):
        global passed
        if self.rect.y < win_h:
            self.rect.y += self.speed
        else:
            self.rect.y=0
            self.speed = randint(1,2)
            self.rect.x = randint(10, win_w-100)
            passed += 1

class Bullet(GameSprite):
    speed = 5
    def update(self):
        self.rect.y -= self.speed

class Score(font.Font):
    def __init__(self, text, color=(200, 200, 200), coord=(0,0)):
        super().__init__(None, 45)
        self.count = 0
        self.text = text
        self.color = color
        self.img = self.render(f'{self.text}: {self.count}', True, self.color)
        self.coord = coord

    def reset(self, value):
        self.count = value
        self.img = self.render(f'{self.text}: {self.count}', True, self.color)
        window.blit(self.img, self.coord)

class Bonus(GameSprite):
    def __init__(self, image_path, coord, size=(65, 65), speed=1, buffSize=1.3):
        super().__init__(image_path, coord, size)
        self.speed=speed
        self.buffSize = buffSize
    
    def update(self):
        if self.rect.y < win_h:
            self.rect.y += self.speed

class ShootingSpeedBonus(Bonus):
    def __init__(self, image_path, coord, size=(65, 65), speed=1, buffSize=1.3):
        super().__init__(image_path, coord, size, speed, buffSize)
    def update(self):
        global bonuses_got
        super().update()
        if sprite.collide_rect(player, self):
            player.ShootingSpeed *= self.buffSize
            self.rect.x=randint(10, win_h-100)
            self.rect.y=0
            bonuses_got+=1
        if self.rect.y>=win_h:
            self.rect.x=randint(10, win_h-100)
            self.rect.y=0

class LifeBonus(Bonus):
    def __init__(self, image_path, coord, size=(65, 65), speed=1, buffSize=2):
        super().__init__(image_path, coord, size, speed, buffSize)
    def update(self):
        global bonuses_got, lifes_last
        super().update()
        if sprite.collide_rect(player, self):
            player.lifes += int(self.buffSize)
            self.rect.x=randint(10, win_h-100)
            self.rect.y=0
            bonuses_got+=1
            lifes_last+=2
        if self.rect.y>=win_h:
            self.rect.x=randint(10, win_h-100)
            self.rect.y=0

win_w = 700
win_h = 500
window = display.set_mode((win_w, win_h))
display.set_caption('Шутер')
background = transform.scale(image.load('galaxy.jpg'), (win_w, win_h))

tick = 0
bonusSpawnTick=tick
player = Player('rocket.png', [K_a, K_d], [60, win_h-100], 7, tick)
monsters = sprite.Group()
for i in range(1,6):
   monster = Enemy('ufo.png', (randint(10, win_h-100), 0))
   monsters.add(monster)
bullets = sprite.Group()
ShootSpeedBonus = ShootingSpeedBonus('asteroid.png', (randint(10, win_h-100), 0), buffSize=2)
LifesBonus = LifeBonus('asteroid.png', (randint(10, win_h-100), 0), buffSize=2)
mixer.init()
mixer.music.load('space.ogg')
fire = mixer.Sound('fire.ogg')
mixer.music.play()

font = font.Font(None, 70)
win = font.render('You win!', True, (0, 255, 0))
false = font.render('You lose!', True, (255, 0, 0))
count_passed = Score("Пропущенных врагов", coord=(10, 10))
count_killed = Score("Убито", coord=(10, 45))
count_wave = Score("Волна номер", coord=(10, 80))
count_bonuses = Score("Бонусов собрано", coord=(10, 160))
count_lifes = Score("Жизней", coord=(10, 115))

playing = True
finish = False
wave_num = 0
passed = 0
killed = 0
bonuses_got = 0
lifes_last = 1
clock = time.Clock()
enemy_collide = False
FPS = 60 #тут кадры в секунду

while playing:
    if not finish:
        window.blit(background, (0,0))
            
        player.update()
        player.reset()
        ShootSpeedBonus.reset()
        ShootSpeedBonus.update()
        LifesBonus.reset()
        LifesBonus.update()
        monsters.draw(window)
        monsters.update()
        count_passed.reset(passed)
        count_killed.reset(killed)
        count_wave.reset(wave_num+1)
        count_bonuses.reset(bonuses_got)
        count_lifes.reset(lifes_last)
        #проверка столкновения пули и монстров (и монстр, и пуля при касании исчезают)
        collides = sprite.groupcollide(monsters, bullets, True, True)
        for c in collides:
            #этот цикл повторится столько раз, сколько монстров подбито
            killed = killed + 1
            new = Enemy('ufo.png', (randint(10, win_h-100), 0))
            new.speed = randint(1, 2)
            monsters.add(new)
            if killed >= 50:
                window.blit(win, (win_w*0.35, win_h*0.4))
                finish = True
        if killed//10 != wave_num:
            wave_num = killed//10
            new = Enemy('ufo.png', (randint(10, win_h-100), 0))
            new.speed = randint(1, 2)
            monsters.add(new)
        hits = sprite.spritecollide(player, monsters, False)
        if hits or passed >= 15:
            if player.lifes<=1:
                window.blit(false, (win_w*0.35, win_h*0.4))
                finish=True
            else:
                player.lifes-=1
                lifes_last-=1
                passed=0
                for i in hits:
                    i.rect.y=0
                    i.rect.x=randint(10, win_h-100)

        for bullet in bullets:
            bullet.update()
            bullet.reset()

    for e in event.get():
        if e.type == QUIT:
            playing = False
        #     player.rect.x, player.rect.y = 60, win_h-155
        #     wall_collide = False

    display.update()
    clock.tick(FPS)
    if tick>100000:
        tick=0
    tick += 1