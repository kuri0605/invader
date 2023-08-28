import pygame
from pygame.locals import *
import sys
import pygame.mixer
import random

START,PLAY,GAMEOVER,STAGECLEAR = (0,1,2,3)
SCR_RECT = Rect(0,0,640,480) #(x,y,w,h)
#ボス戦シュミレーション用
class Invader:
    def __init__(self):
        self.lives = 5 #残機数
        self.wave = 2 #Wave数
        self.counter = 0 #タイムカウンター（60カウント＝1秒）
        self.score = 0 #スコア（エイリアン10点、UFO　50点にWave数を乗算）
        pygame.init()
        screen = pygame.display.set_mode(SCR_RECT.size)
        #素材のロード
        self.load_images()
        self.load_sounds()
        #ゲームオブジェクトを初期化
        self.init_game()
        #メインループ開始
        clock = pygame.time.Clock()
        while(1):
            clock.tick(60)
            self.update()
            self.draw(screen)
            pygame.display.update()
            self.key_handler()
    def init_game(self):
        """ゲームオブジェクトを初期化"""
        #ゲーム状態
        self.game_state = START
        #スプライトグループを作成して登録
        self.all = pygame.sprite.RenderUpdates()
        self.invisible = pygame.sprite.RenderUpdates()
        self.aliens = pygame.sprite.Group()
        self.aliens2 = pygame.sprite.Group()
        self.aliens3 = pygame.sprite.Group()
        self.shots = pygame.sprite.Group()
        self.beams = pygame.sprite.Group()
        self.walls = pygame.sprite.Group()
        self.ufos = pygame.sprite.Group()
        #デフォルトスプライトグループ
        Player.containers = self.all
        Shot.containers = self.all, self.shots, self.invisible
        Alien.containers = self.all, self.aliens, self.invisible
        Alien2.containers = self.all, self.aliens2, self.invisible
        Alien3.containers = self.all, self.aliens3, self.invisible
        Beam.containers = self.all, self.beams, self.invisible
        Wall.containers = self.all, self.walls, self.invisible
        UFO.containers = self.all, self.ufos, self.invisible
        Explosion.containers = self.all, self.invisible
        ExplosionWall.containers = self.all, self.invisible
        #自機を作成
        self.player = Player()
        #エイリアンを作成
        #一列目
        Alien2((60,20),self.wave)
        Alien2((20+40*9,20),self.wave)
        #二列目
        Alien2((100,60),self.wave)
        Alien2((20+40*8,60),self.wave)
        Alien3((220,60),self.wave) #ボス
        #三列目
        for i in range(0,4):
            x = 60 + (i * 40)
            y = 100
            Alien2((x,y),self.wave)
        Alien((220,100),self.wave)
        for i in range(0,4):
            x = 260 + (i * 40)
            y = 100
            Alien2((x,y),self.wave)
        #四列目
        Alien2((20,140),self.wave)
        Alien2((60,140),self.wave)
        for i in range(0,2):
            x = 140 + (i * 32)
            y = 140
            Alien2((x,y),self.wave)
        Alien((220,140),self.wave)
        for i in range(0,2):
            x = 260 + (i * 32)
            y = 140
            Alien2((x,y),self.wave)
        Alien2((20+40*9,140),self.wave)
        Alien2((20+40*10,140),self.wave)
        #五列目
        Alien2((20,180),self.wave)
        for i in range(0,3):
            x = 100 + (i * 40)
            y = 180
            Alien2((x,y),self.wave)
        Alien((220,180),self.wave)
        for i in range(0,3):
            x = 260 + (i * 40)
            y = 180
            Alien2((x,y),self.wave)
        Alien2((20+40*10,180),self.wave)
        #六列目
        Alien2((20,220),self.wave)
        Alien2((100,220),self.wave)
        Alien2((20+40*8,220),self.wave)
        Alien2((20+40*10,220),self.wave)
        #七列目
        Alien2((140,260),self.wave)
        Alien2((180,260),self.wave)
        Alien2((260,260),self.wave)
        Alien2((300,260),self.wave)
    def update(self):
        """ゲーム状態の更新"""
        if self.game_state == PLAY:
            #UFOの出現（15秒後に出現）
            self.counter += 1
            if self.counter % 900 == 0:
                UFO((20,30),self.wave)
            self.all.update()
            #エイリアンの方向判定
            turn_flag = False
            for alien2 in self.aliens2:
                if (alien2.rect.center[0] < 15 and alien2.speed < 0) or \
                        (alien2.rect.center[0] > SCR_RECT.width-15 and alien2.speed > 0):
                    turn_flag = True
                    break
            if turn_flag:
                for alien in self.aliens:
                    alien.speed *= -1
                for alien2 in self.aliens2:
                    alien2.speed *= -1
                for alien3 in self.aliens3:
                    alien3.speed *= -1
            #エイリアンの追撃ビーム
            for alien in self.aliens:
                alien.shoot_extra_beam(self.player.rect.center[0],32,2)
            for alien3 in self.aliens3:
                alien3.shoot_extra_beam(self.player.rect.center[0],32,2)
            #ミサイルとエイリアンの衝突判定
            self.collision_detection()
            #エイリアンをすべて倒したらステージクリア
            if len(self.aliens3.sprites()) == 0:
                self.game_state = STAGECLEAR
    def draw(self,screen):
        """描画"""
        screen.fill((0,0,0))
        if self.game_state == START: #スタート画面
            #タイトルを描画
            title_font = pygame.font.SysFont(None,80)
            title = title_font.render("INVADER GAME",False,(255,0,0))
            screen.blit(title,((SCR_RECT.width-title.get_width())/2,100))
            #エイリアンを描画
            alien_image = Alien.images[0]
            screen.blit(alien_image,((SCR_RECT.width-alien_image.get_width())/2,300))
            #PUSH STARTを描画
            push_font = pygame.font.SysFont(None,40)
            push_space = push_font.render("PUSH SPACE KEY",False,(255,255,255))
            screen.blit(push_space,((SCR_RECT.width-push_space.get_width())/2,380))
        elif self.game_state == PLAY: #ゲームプレイ画面
            #無敵時間中は点滅
            if self.player.invisible % 10 > 4:
                self.invisible.draw(screen)
            else:
                self.all.draw(screen)
            #wave数と残機数を描画
            stat_font = pygame.font.SysFont(None, 20)
            #{インデックス番号：書式指定}2dは最小幅二けた、整数、05dは空白に0を入れる
            stat = stat_font.render("STAGE:{:2d} Lives:{:2d} Score:{:05d}".format(
                self.wave,self.lives,self.score), False, (255,255,255))
            screen.blit(stat,((SCR_RECT.width-stat.get_width())/2,10))
            #壁の耐久画像
            shield_font = pygame.font.SysFont(None,30)
            for wall in self.walls:
                shield = shield_font.render(str(wall.shield),False,(0,0,0))
                text_size = shield_font.size(str(wall.shield))
                screen.blit(shield,(wall.rect.center[0]-text_size[0]/2,wall.rect.center[1]-text_size[1]/2))
        elif self.game_state == GAMEOVER: #ゲームオーバー画面
            #ゲームオーバーを描画
            gameover_font = pygame.font.SysFont(None,80)
            gameover = gameover_font.render("GAME OVER",False,(255,0,0))
            screen.blit(gameover,((SCR_RECT.width-gameover.get_width())/2,100))
            #エイリアンを描画
            alien_image = Alien.images[0]
            screen.blit(alien_image,((SCR_RECT.width-alien_image.get_width())/2,300))
            #PUSH STARTを描画
            push_font = pygame.font.SysFont(None,40)
            push_space = push_font.render("PUSH SPACE KEY",False,(255,255,255))
            screen.blit(push_space,((SCR_RECT.width-push_space.get_width())/2,380))
        elif self.game_state == STAGECLEAR: #ステージクリア画面
            #wave数と残機数を描画
            stat_font = pygame.font.SysFont(None, 20)
            #{インデックス番号：書式指定}2dは最小幅二けた、整数、05dは空白に0を入れる
            stat = stat_font.render("STAGE:{:2d} Lives:{:2d} Score:{:05d}".format(
                self.wave,self.lives,self.score), False, (255,255,255))
            screen.blit(stat,((SCR_RECT.width-stat.get_width())/2,10))
            #ステージクリアを描画
            clear_font = pygame.font.SysFont(None,80)
            clear = clear_font.render("STAGE CLEAR",False,(255,0,0))
            screen.blit(clear,((SCR_RECT.width-clear.get_width())/2,100))
            #エイリアンを描画
            alien_image = Alien.images[1]
            screen.blit(alien_image,((SCR_RECT.width-alien_image.get_width())/2,300))
            #PUSH SPACEを描画
            push_font = pygame.font.SysFont(None,40)
            push_space = push_font.render("PUSH SPACE KEY",False,(255,255,255))
            screen.blit(push_space,((SCR_RECT.width-push_space.get_width())/2,380))
    def key_handler(self):
        """キーハンドラー"""
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN and event.key == K_SPACE:
                if self.game_state == START: #スタート画面でスペース
                    self.game_state = PLAY
                elif self.game_state == GAMEOVER: #ゲームオーバー画面でスペース
                    self.score = 0 #スコア初期化
                    self.wave = 1
                    self.lives = 5
                    self.init_game() #ゲームを初期化
                    self.game_state = PLAY
                elif self.game_state == STAGECLEAR:
                    self.wave += 1
                    self.lives += 1
                    self.init_game() #ゲームを初期化して再開
                    self.game_state = PLAY
    def collision_detection(self):
        """衝突判定"""
        #エイリアンとミサイル
        alien_collided = pygame.sprite.groupcollide(self.aliens,self.shots,True,True)
        for alien in alien_collided.keys():
            Alien.kill_sound.play()
            self.score += 10 * self.wave
            Explosion(alien.rect.center) #エイリアンの中心で爆発
        #エイリアンとミサイル
        alien_collided2 = pygame.sprite.groupcollide(self.aliens2,self.shots,False,True)
        for alien2 in alien_collided2.keys():
            Alien.kill_sound.play()
            Explosion(alien2.rect.center) #エイリアンの中心で爆発
        #エイリアンとミサイル
        alien_collided3 = pygame.sprite.groupcollide(self.aliens3,self.shots,True,True)
        for alien3 in alien_collided3.keys():
            for alien2 in self.aliens2:
                alien2.kill()
                Explosion(alien2.rect.center)
            Alien.kill_sound.play()
            self.score += 200 * self.wave
            Explosion(alien3.rect.center) #エイリアンの中心で爆発
        #UFOとミサイル
        ufo_collided = pygame.sprite.groupcollide(self.ufos,self.shots,True,True)
        for ufo in ufo_collided.keys():
            Alien.kill_sound.play()
            self.score += 50 * self.wave
            Explosion(ufo.rect.center) #エイリアンの中心で爆発
            self.lives += 1
        #プレイヤーとビーム
        #無敵時間中なら判定せずに無敵時間を１減らす
        if self.player.invisible > 0:
            beam_collided = False
            self.player.invisible -= 1
        else:
            beam_collided = pygame.sprite.spritecollide(self.player,self.beams,True)
        if beam_collided: #プレイヤーと衝突したビームがあれば
            Player.bomb_sound.play()
            Explosion(self.player.rect.center)
            self.lives -= 1
            self.player.invisible = 180 #無敵時間は三秒
            if self.lives < 0:
                self.game_state = GAMEOVER #ゲームオーバー
        #トーチカとミサイルかビーム
        wall_collided = pygame.sprite.groupcollide(self.walls,self.shots,False,True)
        wall_collided.update(pygame.sprite.groupcollide(self.walls,self.beams,False,True))
        #トーチカ消滅判定
        for wall in wall_collided:
            wall.shield -= len(wall_collided[wall])
            for hit_beam in wall_collided[wall]:
                Explosion(hit_beam.rect.center) #当たった場所で爆発
            if wall.shield <= 0:
                wall.kill()
                Player.bomb_sound.play()
                ExplosionWall(wall.rect.center)
    def load_images(self):
        """イメージのロード"""
        #スプライトの画像を登録
        Player.image = load_image("player.png")
        Shot.image = load_image("shot.png")
        Alien.images = split_image(load_image("alien.png"),2)
        Alien2.images = split_image(load_image("alien4.png"),2)
        Alien3.images = split_image(load_image("alienboss.png"),2)
        Beam.image = load_image("beam.png")
        Wall.image = load_image("wall.png")
        Explosion.images = split_image(load_image("explosion.png"),16)
        ExplosionWall.images = split_image(load_image("explosion2.png"),16)
        UFO.images = split_image(load_image("ufo.png"),2)
    def load_sounds(self):
        """サウンドのロード"""
        Alien.kill_sound = load_sound("kill.wav")
        Player.shot_sound = load_sound("shot.wav")
        Player.bomb_sound = load_sound("bomb.wav")

class Player(pygame.sprite.Sprite):
    """自機"""
    speed = 5 #移動速度
    reload_time = 15 #リロード時間
    invisible = 0 #無敵時間
    def __init__(self):
        super().__init__(self.containers)
        self.rect = self.image.get_rect()
        self.rect.bottom = SCR_RECT.bottom #プレイヤーが画面の一番下
        self.reload_timer = 0
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
        #リロードの時間が０になるまでは打てない
        if self.reload_timer > 0:
            #リロード
            self.reload_timer -= 1
        if pressed_keys[K_SPACE]:
            if self.reload_timer == 0:
                #発射！
                Player.shot_sound.play()
                Shot(self.rect.center) #作成すると同時にallに追加
                self.reload_timer = self.reload_time

class Shot(pygame.sprite.Sprite):
    """プレイヤーが発射するミサイル"""
    speed = 12 #移動速度
    def __init__(self,pos):
        super().__init__(self.containers)
        self.rect = self.image.get_rect()
        self.rect.center = pos #中心座標をposに
    def update(self):
        self.rect.move_ip(0,-self.speed) #上へ移動
        if self.rect.top < 0: #上端に達したら除去
            self.kill()

class Alien(pygame.sprite.Sprite):
    """エイリアン"""
    #コメントは前の設定
    animcycle = 18 #アニメーション速度
    frame = 0
    #move_width = 230 #横方向の移動範囲
    def __init__(self,pos,wave):
        super().__init__(self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.speed = 1 + wave #移動速度
        self.prob_beam = (1.5 + wave) * 0.002 #ビームを発射する確率
        """
        self.left = pos[0] #移動できる左端
        self.right = self.left + self.move_width #移動できる右端
        """
    def shoot_extra_beam(self,target_x_pos,border_dist,rate):
        if random.random() < self.prob_beam*rate and \
                abs(self.rect.center[0] - target_x_pos) < border_dist:
            Beam(self.rect.center)
    def update(self):
        #横方向への移動
        self.rect.move_ip(self.speed,0)
        """
        if self.rect.center[0] < self.left or self.rect.center[0] > self.right:
            self.speed = -self.speed
        """
        #ビームを発射
        if random.random() < self.prob_beam:
            Beam(self.rect.center)
        #キャラクターアニメーション
        self.frame += 1
        self.image = self.images[(self.frame//self.animcycle)%2]

class Alien2(pygame.sprite.Sprite):
    """エイリアン2"""
    #コメントは前の設定
    animcycle = 18 #アニメーション速度
    frame = 0
    #move_width = 230 #横方向の移動範囲
    def __init__(self,pos,wave):
        super().__init__(self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.speed = 1 + wave #移動速度
        self.prob_beam = (1.5 + wave) * 0.002 #ビームを発射する確率
        """
        self.left = pos[0] #移動できる左端
        self.right = self.left + self.move_width #移動できる右端
        """
    def shoot_extra_beam(self,target_x_pos,border_dist,rate):
        if random.random() < self.prob_beam*rate and \
                abs(self.rect.center[0] - target_x_pos) < border_dist:
            Beam(self.rect.center)
    def update(self):
        #横方向への移動
        self.rect.move_ip(self.speed,0)
        """
        if self.rect.center[0] < self.left or self.rect.center[0] > self.right:
            self.speed = -self.speed
        """
        #ビームを発射
        if random.random() < self.prob_beam:
            Beam(self.rect.center)
        #キャラクターアニメーション
        self.frame += 1
        self.image = self.images[(self.frame//self.animcycle)%2]

class Alien3(pygame.sprite.Sprite):
    """エイリアン3"""
    #コメントは前の設定
    animcycle = 18 #アニメーション速度
    frame = 0
    #move_width = 230 #横方向の移動範囲
    def __init__(self,pos,wave):
        super().__init__(self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.speed = 1 + wave #移動速度
        self.prob_beam = (1.5 + wave) * 0.002 #ビームを発射する確率
        """
        self.left = pos[0] #移動できる左端
        self.right = self.left + self.move_width #移動できる右端
        """
    def shoot_extra_beam(self,target_x_pos,border_dist,rate):
        if random.random() < self.prob_beam*rate and \
                abs(self.rect.center[0] - target_x_pos) < border_dist:
            Beam(self.rect.center)
    def update(self):
        #横方向への移動
        self.rect.move_ip(self.speed,0)
        """
        if self.rect.center[0] < self.left or self.rect.center[0] > self.right:
            self.speed = -self.speed
        """
        #ビームを発射
        if random.random() < self.prob_beam:
            Beam(self.rect.center)
        #キャラクターアニメーション
        self.frame += 1
        self.image = self.images[(self.frame//self.animcycle)%2]

class Beam(pygame.sprite.Sprite):
    """エイリアンのビーム"""
    speed = 5 #速度
    def __init__(self,pos):
        super().__init__(self.containers)
        self.rect = self.image.get_rect()
        self.rect.center = pos
    def update(self):
        self.rect.move_ip(0,self.speed) #下へ移動
        if self.rect.bottom > SCR_RECT.height: #下端に達したら消去
            self.kill()

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

class ExplosionWall(Explosion):
    pass

class Wall(pygame.sprite.Sprite):
    """トーチカ"""
    shield = 0 #耐久力
    def __init__(self,pos):
        super().__init__(self.containers)
        self.rect = self.image.get_rect()
        self.rect.center = pos
    def update(self):
        pass #何もしない

class UFO(pygame.sprite.Sprite):
    """UFO"""
    def __init__(self,pos,wave):
        self.speed = 1 + wave//2 #移動速度
        # side => 0:left, 1:right
        side = 0 if random.random() < 0.5 else 1
        if side:
            self.speed *= -1 #右からの出現では速度を反転
        self.animcycle = 18 #アニメーション速度
        self.frame = 0
        super().__init__(self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.center = (SCR_RECT.width - pos[0] if side else pos[0], pos[1]) #開始位置（x）
        self.pos_kill = pos[0] if side else SCR_RECT.width - pos[0] #消滅位置（x）
    def update(self):
        #横方向への移動
        self.rect.move_ip(self.speed,0)
        #指定位置まで来たら消滅
        if (self.rect.center[0] > self.pos_kill and self.speed > 0) or \
            (self.rect.center[0] < self.pos_kill and self.speed < 0):
            self.kill()
        #キャラクターアニメーション
        self.frame += 1
        self.image = self.images[(self.frame//self.animcycle)%2]

def load_image(filename, colorkey=None):
    """画像をロードして画像と矩形を返す"""
    try:
        image = pygame.image.load(filename)
    except pygame.error as message:
        print ("Cannot load image:", filename)
        raise SystemExit(message)
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image

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

def load_sound(filename):
    return pygame.mixer.Sound(filename)

Invader()
