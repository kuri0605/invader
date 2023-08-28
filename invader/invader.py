import pygame
from pygame.locals import *
import sys
import pygame.mixer
import random

SCR_RECT = Rect(0,0,620,480) #(x,y,w,h)

def split_image(image,n):
    """横に長いキャラクターイメージをn枚のイメージに分割
    分割したイメージを格納したリストを返す"""
    imageList = []
    w = image.get_width()
    h = image.get_height()
    w1 = w//n
    for i in range(0,w,w1): #（開始値、終了値、ステップ値）
        surface = pygame.Surface((w1,h))
        surface.blit(image,(0,0),(i,0,w1,h)) #画像、左上、画像の幅
        surface.set_colorkey(surface.get_at((0,0)),RLEACCEL)
        surface.convert()
        imageList.append(surface)
    return imageList


class Player(pygame.sprite.Sprite):
    """自機"""
    speed = 5 #移動速度
    reload_time = 15 #リロード時間
    def __init__(self,aliens,shots):
        super().__init__(self.containers)
        self.rect = self.image.get_rect()
        self.rect.bottom = SCR_RECT.bottom #プレイヤーが画面の一番下
        self.reload_timer = 0
        self.aliens = aliens
        self.shots = shots
    def update(self):
        #押されているキーをチェック
        pressed_keys = pygame.key.get_pressed()
        #押されているキーに応じてプレイヤーを移動
        if pressed_keys[K_LEFT]:
            self.rect.move_ip(-self.speed,0)
        elif pressed_keys[K_RIGHT]:
            self.rect.move_ip(self.speed,0)
        self.rect.clamp_ip(SCR_RECT) #敵前逃亡は許さん
        #ミサイルの発射
        if pressed_keys[K_SPACE]:
            #リロードの時間が０になるまでは打てない
            if self.reload_timer > 0:
                #リロード
                self.reload_timer -= 1
            else:
                #発射！
                Player.shot_sound.play()
                Shot(self.rect.center,self.aliens,self.shots) #作成すると同時にallに追加
                self.reload_timer = self.reload_time

class Shot(pygame.sprite.Sprite):
    """プレイヤーが発射するミサイル"""
    speed = 9 #移動速度
    def __init__(self,pos,aliens,shots):
        super().__init__(self.containers)
        self.rect = self.image.get_rect()
        self.rect.center = pos #中心座標をposに
        self.aliens = aliens
        self.shots = shots
    def update(self):
        self.rect.move_ip(0,-self.speed) #上へ移動
        if self.rect.top < 0: #上端に達したら除去
            self.kill()
        alien_collided = pygame.sprite.groupcollide(self.aliens,self.shots,True,True)
        for alien in alien_collided.keys():
            Alien.kill_sound.play()
            Explosion(alien.rect.center) #エイリアンの中心で爆発

class Alien(pygame.sprite.Sprite):
    """エイリアン"""
    speed = 2 #移動速度
    animcycle = 18 #アニメーション速度
    frame = 0
    move_width = 230 #横方向の移動範囲
    prob_beam = 0.005 #ビームを発射する確率
    def __init__(self,pos,player,beams):
        super().__init__(self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.left = pos[0] #移動できる左端
        self.right = self.left + self.move_width #移動できる右端
        self.player = player
        self.beams = beams
    def update(self):
        #横方向への移動
        self.rect.move_ip(self.speed,0)
        if self.rect.center[0] < self.left or self.rect.center[0] > self.right:
            self.speed = -self.speed
        #ビームを発射
        if random.random() < self.prob_beam:
            Beam(self.rect.center,self.player,self.beams)
        #キャラクターアニメーション
        self.frame += 1
        self.image = self.images[(self.frame//self.animcycle)%2]

class Beam(pygame.sprite.Sprite):
    """エイリアンのビーム"""
    speed = 5 #速度
    def __init__(self,pos,player,beams):
        super().__init__(self.containers)
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.player = player
        self.beams = beams
    def update(self):
        self.rect.move_ip(0,self.speed) #下へ移動
        if self.rect.bottom > SCR_RECT.height: #下端に達したら消去
            self.kill()
        beam_collided = pygame.sprite.spritecollide(self.player,self.beams,True)
        if beam_collided: #プレイヤーと衝突したビームがあれば
            Player.bomb_sound.play()
            #TODO:ゲームオーバー処理

class Explosion(pygame.sprite.Sprite):
    """爆発エフェクト"""
    animcycle = 2 #アニメーション速度
    frame = 0
    def __init__(self,pos):
        super().__init__(self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.max_frame = len(self.images) * self.animcycle #消滅するフレーム
    def update(self):
        self.image = self.images[self.frame//self.animcycle]
        self.frame += 1
        if self.frame == self.max_frame:
            self.kill()

def main():
    pygame.init()
    screen = pygame.display.set_mode(SCR_RECT.size)

    #スプライトグループを作成して登録
    all = pygame.sprite.RenderUpdates()
    Player.containers = all
    shots = pygame.sprite.Group()
    Shot.containers = all, shots
    aliens = pygame.sprite.Group()
    Alien.containers = all, aliens
    beams = pygame.sprite.Group()
    Beam.containers = all,beams
    Explosion.containers = all
    #スプライトの画像を登録
    Player.image = pygame.image.load("player.png").convert()
    Shot.image = pygame.image.load("shot.png").convert()
    Beam.image = pygame.image.load("beam.png").convert()
    #エイリアンの画像を分割してロード
    Alien.images = split_image(pygame.image.load("alien.png"),2)
    #エイリアンの断末魔
    Alien.kill_sound = pygame.mixer.Sound("kill.wav")
    #爆発
    Explosion.images = split_image(pygame.image.load("explosion.png"),16)
    #自機を作成
    Player.shot_sound = pygame.mixer.Sound("shot.wav")
    Player.bomb_sound = pygame.mixer.Sound("bomb.wav")
    Player(aliens,shots)
    player = Player(aliens,shots)
    #エイリアンを作成
    for i in range(0,50):
        x = 20 + (i % 10) * 40
        y = 20 + (i // 10) * 40
        Alien((x,y),player,beams)

    clock = pygame.time.Clock()
    while(1):
        clock.tick(60)
        screen.fill((0,0,0))
        all.update()
        all.draw(screen)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()

if __name__ ==  "__main__":
    main()
