import pygame
import random
import json
import os
import math
from enum import Enum
from typing import List, Optional, Tuple

# 初期化
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

# 日本語フォントを取得する関数
def get_japanese_font(size, bold=False):
    """日本語対応フォントを取得"""
    # Windowsで利用可能な日本語フォントを順に試す
    font_names = ['meiryo', 'msgothic', 'ms pgothic', 'yugothic', 'yu gothic']
    for font_name in font_names:
        try:
            font = pygame.font.SysFont(font_name, size, bold=bold)
            # テスト用の文字列で日本語が表示できるか確認
            test_surface = font.render('あ', True, (255, 255, 255))
            if test_surface.get_width() > 0:
                return font
        except:
            continue
    # フォールバック: デフォルトフォント
    return pygame.font.Font(None, size)

# 定数
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

# 色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 100, 255)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (64, 64, 64)

# UI用の色（参考コードから）
BG_DARK = (2, 6, 23)  # #020617
BG_DARKER = (5, 8, 20)  # #050814
BG_DARKEST = (0, 0, 0)
TEXT_LIGHT = (229, 231, 235)  # #e5e7eb
TEXT_GRAY = (156, 163, 175)  # #9ca3af
BORDER_COLOR = (148, 163, 184)  # #94a3b8
BUTTON_BLUE_START = (29, 78, 216)  # #1d4ed8
BUTTON_BLUE_END = (15, 23, 42)  # #0f172a
BUTTON_HOVER_START = (37, 99, 235)  # #2563eb
BUTTON_HOVER_END = (17, 24, 39)  # #111827

# ゲーム説明テキスト（定数）
INSTRUCTIONS_TEXT = [
    "【ルール】",
    "とにかくよけ続けろ！",
    "移動は上下のみ！アイテムとってパワーアップだ！",
    "ハイスコアをねらえ！！！",
    "",
    "【アイテム】",
    "・青アイテム：移動速度が上がる",
    "・赤アイテム：プレイヤーが小さくなる",
    "・緑アイテム：障害物が小さくなる",
    "・黄アイテム：障害物の速度が遅くなる",
    "",
]

# テキストレンダラークラス（かっこいいUI用）
class TextRenderer:
    @staticmethod
    def draw_title(screen, text, x, y, size=80, color=TEXT_LIGHT, center=True):
        """タイトル用テキスト（グロー効果、影付き）"""
        font = get_japanese_font(size, bold=True)
        
        # グロー効果（複数層の影で表現）
        glow_color = (96, 165, 250)  # 青系のグロー
        for i in range(8):
            offset = i * 1.5
            alpha = int(200 * (1 - i / 8))
            # 透明度は色の明度で表現
            glow_rgb = tuple(int(c * (alpha / 255)) for c in glow_color[:3])
            glow_surf = font.render(text, True, glow_rgb)
            glow_rect = glow_surf.get_rect()
            if center:
                glow_rect.center = (x + offset, y + offset)
            else:
                glow_rect.topleft = (x + offset, y + offset)
            screen.blit(glow_surf, glow_rect)
        
        # 影（黒）
        shadow = font.render(text, True, (0, 0, 0))
        shadow_rect = shadow.get_rect()
        if center:
            shadow_rect.center = (x + 3, y + 3)
        else:
            shadow_rect.topleft = (x + 3, y + 3)
        screen.blit(shadow, shadow_rect)
        
        # メインテキスト
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if center:
            text_rect.center = (x, y)
        else:
            text_rect.topleft = (x, y)
        screen.blit(text_surface, text_rect)
        
        return text_rect
    
    @staticmethod
    def draw_effect(screen, text, x, y, size=60, color=YELLOW, center=True):
        """演出用テキスト（派手なグロー効果）"""
        font = get_japanese_font(size, bold=True)
        
        # 強いグロー効果
        for i in range(10):
            offset = i * 2
            alpha = int(150 * (1 - i / 10))
            glow_color = tuple(min(255, c + i * 15) for c in color[:3])
            # 透明度は色の明度で表現
            glow_rgb = tuple(int(c * (alpha / 255)) for c in glow_color[:3])
            glow_surf = font.render(text, True, glow_rgb)
            glow_rect = glow_surf.get_rect()
            if center:
                glow_rect.center = (x + offset, y + offset)
            else:
                glow_rect.topleft = (x + offset, y + offset)
            screen.blit(glow_surf, glow_rect)
        
        # 影
        shadow = font.render(text, True, (0, 0, 0))
        shadow_rect = shadow.get_rect()
        if center:
            shadow_rect.center = (x + 4, y + 4)
        else:
            shadow_rect.topleft = (x + 4, y + 4)
        screen.blit(shadow, shadow_rect)
        
        # メインテキスト
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if center:
            text_rect.center = (x, y)
        else:
            text_rect.topleft = (x, y)
        screen.blit(text_surface, text_rect)
        
        return text_rect
    
    @staticmethod
    def draw_normal(screen, text, x, y, size=32, color=TEXT_LIGHT, center=False):
        """通常テキスト（見やすく、シンプルな影）"""
        font = get_japanese_font(size)
        
        # シンプルな影（見やすさ重視）
        shadow = font.render(text, True, (0, 0, 0))
        shadow_rect = shadow.get_rect()
        if center:
            shadow_rect.center = (x + 2, y + 2)
        else:
            shadow_rect.topleft = (x + 2, y + 2)
        screen.blit(shadow, shadow_rect)
        
        # メインテキスト
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if center:
            text_rect.center = (x, y)
        else:
            text_rect.topleft = (x, y)
        screen.blit(text_surface, text_rect)
        
        return text_rect
    
    @staticmethod
    def draw_subtitle(screen, text, x, y, size=16, color=TEXT_GRAY, center=True):
        """サブタイトル用テキスト（控えめ）"""
        font = get_japanese_font(size)
        
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if center:
            text_rect.center = (x, y)
        else:
            text_rect.topleft = (x, y)
        screen.blit(text_surface, text_rect)
        
        return text_rect

# ゲーム状態
class GameState(Enum):
    START = 1
    PLAYING = 2
    PAUSED = 3
    RESULT = 4

# プレイヤークラス
class Player:
    def __init__(self):
        self.width = 40
        self.height = 60
        self.x = 50
        self.y = SCREEN_HEIGHT // 2 - self.height // 2
        self.speed = 7
        self.base_speed = 7
        self.base_width = 40
        self.base_height = 60
        self.color = BLUE
        
    def update(self, keys):
        # 滑らかな移動（キーが押されている間、毎フレーム移動）
        # 画面の上下の壁をなくし、端で反対側にワープ
        if keys[pygame.K_UP]:
            self.y -= self.speed
            # 上端を超えたら下端から上に移動
            if self.y < 0:
                self.y = SCREEN_HEIGHT - self.height
                
        if keys[pygame.K_DOWN]:
            self.y += self.speed
            # 下端を超えたら上端から下に移動
            if self.y > SCREEN_HEIGHT - self.height:
                self.y = 0
            
    def draw(self, screen):
        # グラデーション効果（簡易版）
        for i in range(self.height):
            ratio = i / self.height
            r = int(self.color[0] * (1 - ratio) + (self.color[0] * 0.7) * ratio)
            g = int(self.color[1] * (1 - ratio) + (self.color[1] * 0.7) * ratio)
            b = int(self.color[2] * (1 - ratio) + (self.color[2] * 0.7) * ratio)
            pygame.draw.line(screen, (r, g, b), 
                           (self.x, self.y + i), 
                           (self.x + self.width, self.y + i))
        # ハイライト
        highlight_surf = pygame.Surface((self.width, self.height // 3))
        highlight_surf.set_alpha(50)
        highlight_surf.fill(WHITE)
        screen.blit(highlight_surf, (self.x, self.y))
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
        
    def apply_speed_boost(self, multiplier):
        self.speed = self.base_speed * multiplier
        
    def apply_size_reduction(self, multiplier):
        self.width = int(self.base_width * multiplier)
        self.height = int(self.base_height * multiplier)
        
    def reset_effects(self):
        self.speed = self.base_speed
        self.width = self.base_width
        self.height = self.base_height

# 障害物クラス
class Obstacle:
    def __init__(self, x, y, width, height, speed):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.base_width = width
        self.base_height = height
        self.speed = speed
        self.base_speed = speed
        self.color = WHITE
        
    def update(self):
        self.x -= self.speed
        
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
        
    def apply_size_reduction(self, multiplier):
        self.width = int(self.base_width * multiplier)
        self.height = int(self.base_height * multiplier)
        
    def apply_speed_reduction(self, multiplier):
        self.speed = self.base_speed * multiplier

# アイテムクラス
class Item:
    def __init__(self, x, y, item_type):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 30
        self.type = item_type  # 'speed', 'shrink', 'obstacle_shrink', 'slow'
        self.speed = 3
        self.collected = False
        
        # アイテムタイプに応じた色
        self.colors = {
            'speed': BLUE,
            'shrink': RED,
            'obstacle_shrink': GREEN,
            'slow': YELLOW
        }
        self.color = self.colors.get(item_type, WHITE)
        
    def update(self):
        self.x -= self.speed
        
    def draw(self, screen):
        if not self.collected:
            pygame.draw.circle(screen, self.color, 
                             (self.x + self.width // 2, self.y + self.height // 2), 
                             self.width // 2)
            # アイテムタイプを示す記号を描画
            font = get_japanese_font(20)
            symbols = {
                'speed': '↑',
                'shrink': '↓',
                'obstacle_shrink': '●',
                'slow': '←'
            }
            text = font.render(symbols.get(self.type, '?'), True, WHITE)
            text_rect = text.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
            screen.blit(text, text_rect)
            
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

# スコアマネージャー
class ScoreManager:
    def __init__(self):
        self.score_file = 'scores.json'
        self.scores = self.load_scores()
        
    def load_scores(self):
        if os.path.exists(self.score_file):
            try:
                with open(self.score_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
        
    def save_score(self, score):
        self.scores.append(score)
        self.scores.sort(reverse=True)
        self.scores = self.scores[:10]  # トップ10のみ保持
        
        with open(self.score_file, 'w', encoding='utf-8') as f:
            json.dump(self.scores, f, ensure_ascii=False, indent=2)
            
    def get_high_score(self):
        if self.scores:
            return max(self.scores)
        return 0
        
    def is_new_high_score(self, score):
        return score > self.get_high_score()

# パーティクルクラス
class Particle:
    def __init__(self, x, y, color, velocity_x=0, velocity_y=0, size=3, lifetime=30, gravity=0.1):
        self.x = x
        self.y = y
        self.color = color
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.size = size
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.gravity = gravity
        self.active = True
        
    def update(self):
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.velocity_y += self.gravity
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.active = False
            
    def draw(self, screen):
        if self.active:
            alpha = int(255 * (self.lifetime / self.max_lifetime))
            color_with_alpha = (*self.color[:3], alpha) if len(self.color) > 3 else self.color
            size = int(self.size * (self.lifetime / self.max_lifetime))
            if size > 0:
                pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), size)

# パーティクルシステムクラス
class ParticleSystem:
    def __init__(self):
        self.particles: List[Particle] = []
        
    def add_explosion(self, x, y, color, count=20, speed=5):
        """爆発エフェクトを追加"""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed_variation = random.uniform(0.5, speed)
            vx = math.cos(angle) * speed_variation
            vy = math.sin(angle) * speed_variation
            particle = Particle(
                x, y, color,
                velocity_x=vx,
                velocity_y=vy,
                size=random.randint(2, 5),
                lifetime=random.randint(20, 40),
                gravity=0.1
            )
            self.particles.append(particle)
    
    def add_sparkle(self, x, y, color, count=10):
        """キラキラエフェクトを追加"""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 3)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            particle = Particle(
                x, y, color,
                velocity_x=vx,
                velocity_y=vy,
                size=random.randint(1, 3),
                lifetime=random.randint(15, 30),
                gravity=-0.05
            )
            self.particles.append(particle)
    
    def add_trail(self, x, y, color):
        """軌跡エフェクトを追加"""
        for _ in range(3):
            particle = Particle(
                x + random.randint(-5, 5),
                y + random.randint(-5, 5),
                color,
                velocity_x=random.uniform(-0.5, 0.5),
                velocity_y=random.uniform(-0.5, 0.5),
                size=2,
                lifetime=10,
                gravity=0
            )
            self.particles.append(particle)
    
    def update(self):
        for particle in self.particles[:]:
            particle.update()
            if not particle.active:
                self.particles.remove(particle)
    
    def draw(self, screen):
        for particle in self.particles:
            particle.draw(screen)

# 風パーティクルクラス
class WindParticle:
    def __init__(self, x, y, length, speed, color, layer=0):
        self.x = x
        self.y = y
        self.length = length  # 線の長さ
        self.speed = speed  # 左への移動速度
        self.color = color
        self.layer = layer  # レイヤー（深度）
        self.width = random.randint(1, 3)  # 線の太さ
        self.max_x = x  # 開始位置（グラデーション用）
        self.active = True
        
    def update(self):
        self.x -= self.speed
        # 画面左端を超えたら削除
        if self.x + self.length < 0:
            self.active = False
            
    def draw(self, screen):
        if self.active:
            # グラデーション計算（右側が濃く、左側が薄く）
            start_x = int(self.x)
            end_x = int(self.x + self.length)
            
            # 右側（開始位置からの距離に基づく透明度）
            distance_from_start = self.max_x - self.x
            max_distance = SCREEN_WIDTH
            alpha_right = int(255 * (1 - min(distance_from_start / max_distance, 1)))
            
            # 左側（より薄く）
            alpha_left = max(0, alpha_right - 100)
            
            # グラデーション線を描画（複数の線で表現）
            segments = max(5, self.length // 10)
            for i in range(segments):
                seg_start_x = start_x + (i * self.length // segments)
                seg_end_x = start_x + ((i + 1) * self.length // segments)
                progress = i / segments
                alpha = int(alpha_right * (1 - progress) + alpha_left * progress)
                
                # 透明度を適用したSurfaceを作成
                if alpha > 0 and seg_end_x > seg_start_x:
                    line_surf = pygame.Surface((seg_end_x - seg_start_x, self.width + 2), pygame.SRCALPHA)
                    color_with_alpha = (*self.color[:3], min(255, alpha))
                    line_surf.fill(color_with_alpha)
                    screen.blit(line_surf, (seg_start_x, int(self.y) - self.width // 2))

# 風エフェクトクラス
class WindEffect:
    def __init__(self):
        self.particles: List[WindParticle] = []
        self.active = False
        self.duration = 0
        self.timer = 0
        self.spawn_timer = 0
        self.spawn_interval = 3  # 連続生成の間隔（フレーム）
        self.density = 1.0  # 密度（速度に応じて変わる）
        self.layers = 3  # レイヤー数（奥行き感）
        
    def start(self, duration=90, density=1.0):
        """風エフェクトを開始"""
        self.active = True
        self.duration = duration
        self.timer = 0
        self.spawn_timer = 0
        self.density = density
        # バースト生成（開始時に一度に大量生成）
        self.burst_spawn()
        
    def stop(self):
        """風エフェクトを停止"""
        self.active = False
        self.particles.clear()
        
    def burst_spawn(self):
        """バースト生成（一度に大量生成）"""
        count = int(30 * self.density)  # 密度に応じた数
        for _ in range(count):
            self.spawn_particle(use_random=True)
            
    def spawn_particle(self, use_random=True):
        """パーティクルを生成"""
        if use_random:
            # ランダム配置
            y = random.randint(0, SCREEN_HEIGHT)
            length = random.randint(20, 60)
            speed = random.uniform(8, 12) * self.density  # 速度を上げる（3-6 → 8-12）
            layer = random.randint(0, self.layers - 1)
        else:
            # グリッド配置
            grid_y = random.randint(0, SCREEN_HEIGHT // 20) * 20
            y = grid_y + random.randint(-5, 5)
            length = random.randint(30, 50)
            speed = random.uniform(9, 12) * self.density  # 速度を上げる（4-6 → 9-12）
            layer = random.randint(0, self.layers - 1)
            
        # レイヤーに応じた色と速度の調整
        if layer == 0:  # 前景（速く、濃い）
            color = (255, 255, 255)  # 白
            speed *= 1.5  # 速度倍率を上げる（1.2 → 1.5）
        elif layer == 1:  # 中景
            color = (200, 220, 255)  # 薄い青
            speed *= 1.2  # 速度倍率を上げる（1.0 → 1.2）
        else:  # 背景（遅く、薄い）
            color = (150, 170, 200)  # グレー
            speed *= 1.0  # 速度倍率を上げる（0.8 → 1.0）
            
        particle = WindParticle(SCREEN_WIDTH, y, length, speed, color, layer)
        self.particles.append(particle)
        
    def update(self):
        """風エフェクトを更新"""
        self.timer += 1
        
        # アクティブな時のみ新しいパーティクルを生成
        if self.active:
            self.spawn_timer += 1
            
            # 連続生成（一定間隔で右端に生成）
            if self.spawn_timer >= self.spawn_interval:
                # ランダム配置とグリッド配置を混在
                if random.random() < 0.7:  # 70%がランダム
                    self.spawn_particle(use_random=True)
                else:  # 30%がグリッド
                    self.spawn_particle(use_random=False)
                self.spawn_timer = 0
                
            # 持続時間が終わったら新しい生成を停止
            if self.timer >= self.duration:
                self.active = False
                # パーティクルは自然に消えるまで残す（削除しない）
            
        # パーティクルの更新（activeがFalseでも既存のパーティクルは更新し続ける）
        for particle in self.particles[:]:
            particle.update()
            # 画面左端に消えたら削除（フェードアウト完了）
            if not particle.active:
                self.particles.remove(particle)
            
    def draw(self, screen):
        """風エフェクトを描画（レイヤー順に）"""
        # パーティクルが存在する限り描画（activeがFalseでも既存のパーティクルは表示）
        # レイヤーごとに描画（背景から前景へ）
        for layer in range(self.layers):
            for particle in self.particles:
                if particle.layer == layer:
                    particle.draw(screen)

# 画面シェイクエフェクト
class ScreenShake:
    def __init__(self):
        self.shake_intensity = 0
        self.shake_duration = 0
        self.offset_x = 0
        self.offset_y = 0
        
    def shake(self, intensity=10, duration=10):
        self.shake_intensity = intensity
        self.shake_duration = duration
        
    def update(self):
        if self.shake_duration > 0:
            self.offset_x = random.randint(-self.shake_intensity, self.shake_intensity)
            self.offset_y = random.randint(-self.shake_intensity, self.shake_intensity)
            self.shake_duration -= 1
            if self.shake_duration <= 0:
                self.offset_x = 0
                self.offset_y = 0
        else:
            self.offset_x = 0
            self.offset_y = 0

# グロー効果クラス
class GlowEffect:
    @staticmethod
    def draw_glow_circle(screen, x, y, radius, color, intensity=3):
        """グロー効果付き円を描画"""
        for i in range(intensity):
            alpha = max(0, 50 - i * 15)
            size = radius + i * 3
            glow_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            glow_color = (*color[:3], alpha) if len(color) > 3 else color
            pygame.draw.circle(glow_surf, glow_color, (size, size), size)
            try:
                screen.blit(glow_surf, (x - size, y - size), special_flags=pygame.BLEND_ALPHA_SDL2)
            except:
                screen.blit(glow_surf, (x - size, y - size))
        pygame.draw.circle(screen, color, (int(x), int(y)), radius)
    
    @staticmethod
    def draw_glow_rect(screen, rect, color, intensity=3):
        """グロー効果付き矩形を描画"""
        x, y, w, h = rect
        for i in range(intensity):
            alpha = max(0, 50 - i * 15)
            offset = i * 2
            glow_rect = pygame.Rect(x - offset, y - offset, w + offset * 2, h + offset * 2)
            glow_surf = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            glow_color = (*color[:3], alpha) if len(color) > 3 else color
            pygame.draw.rect(glow_surf, glow_color, (0, 0, glow_rect.width, glow_rect.height))
            try:
                screen.blit(glow_surf, glow_rect.topleft, special_flags=pygame.BLEND_ALPHA_SDL2)
            except:
                screen.blit(glow_surf, glow_rect.topleft)
        pygame.draw.rect(screen, color, rect)

# エネルギーパーティクルクラス（背景用）
class EnergyParticle:
    def __init__(self, x, y, color, speed=1.0, size=2, lifetime=200):
        self.x = x
        self.y = y
        self.color = color
        self.speed = speed
        self.size = size
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.angle = random.uniform(0, 2 * math.pi)
        self.radius = random.uniform(50, 200)
        self.center_x = x
        self.center_y = y
        self.rotation_speed = random.uniform(0.005, 0.015)  # 0.01-0.03 → 0.005-0.015（より滑らかに）
        
    def update(self):
        self.lifetime -= 1
        # 渦巻き運動
        self.angle += self.rotation_speed
        self.radius += self.speed
        self.x = self.center_x + math.cos(self.angle) * self.radius
        self.y = self.center_y + math.sin(self.angle) * self.radius
        
    def draw(self, screen):
        if self.lifetime > 0:
            alpha = int(255 * (self.lifetime / self.max_lifetime))
            color_with_alpha = (*self.color[:3], alpha)
            particle_surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surf, color_with_alpha, (self.size, self.size), self.size)
            screen.blit(particle_surf, (int(self.x - self.size), int(self.y - self.size)))

# タイトル画面背景クラス
class TitleBackground:
    def __init__(self):
        self.time = 0
        self.energy_particles: List[EnergyParticle] = []
        self.gradient_centers = [
            (SCREEN_WIDTH * 0.3, SCREEN_HEIGHT * 0.3),
            (SCREEN_WIDTH * 0.7, SCREEN_HEIGHT * 0.7),
            (SCREEN_WIDTH * 0.5, SCREEN_HEIGHT * 0.5),
        ]
        self.gradient_colors = [
            [(29, 78, 216), (15, 23, 42), (96, 165, 250)],
            [(37, 99, 235), (17, 24, 39), (59, 130, 246)],
            [(96, 165, 250), (15, 23, 42), (147, 197, 253)],
        ]
        # エネルギーパーティクルを初期化
        self._init_energy_particles()
        
    def _init_energy_particles(self):
        """エネルギーパーティクルを初期化"""
        for _ in range(30):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            color = random.choice([
                (96, 165, 250),  # 青
                (59, 130, 246),  # 明るい青
                (147, 197, 253),  # 薄い青
                (255, 255, 255),  # 白
            ])
            self.energy_particles.append(EnergyParticle(x, y, color))
    
    def update(self):
        """背景を更新"""
        self.time += 1
        
        # エネルギーパーティクルの更新
        for particle in self.energy_particles[:]:
            particle.update()
            if particle.lifetime <= 0 or particle.radius > SCREEN_WIDTH * 1.5:
                # 新しいパーティクルを生成
                x = random.randint(0, SCREEN_WIDTH)
                y = random.randint(0, SCREEN_HEIGHT)
                color = random.choice([
                    (96, 165, 250),
                    (59, 130, 246),
                    (147, 197, 253),
                    (255, 255, 255),
                ])
                self.energy_particles.remove(particle)
                self.energy_particles.append(EnergyParticle(x, y, color))
    
    def draw_radial_gradient(self, screen, center_x, center_y, colors, radius, time_offset=0):
        """放射状グラデーションを描画（アニメーション対応、滑らか版）"""
        # 色をアニメーション（時間に応じて変化、より滑らかに）
        animated_colors = []
        for color in colors:
            # 色を時間に応じて変化させる（速度を遅くして滑らかに）
            r, g, b = color
            r = int(r + math.sin((self.time + time_offset) * 0.003) * 15)  # 0.01 → 0.003、20 → 15
            g = int(g + math.sin((self.time + time_offset) * 0.004) * 15)  # 0.015 → 0.004、20 → 15
            b = int(b + math.sin((self.time + time_offset) * 0.0035) * 15)  # 0.012 → 0.0035、20 → 15
            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))
            animated_colors.append((r, g, b))
        
        # 放射状グラデーションを描画（間隔を空けてパフォーマンス向上）
        step = 2  # 2ピクセルごとに描画（滑らかさとパフォーマンスのバランス）
        for i in range(0, radius, step):
            ratio = i / radius
            # 複数色のグラデーション（3色以上）
            if ratio < 0.33:
                # 最初の色から中間色へ
                local_ratio = ratio / 0.33
                r = int(animated_colors[0][0] * (1 - local_ratio) + animated_colors[1][0] * local_ratio)
                g = int(animated_colors[0][1] * (1 - local_ratio) + animated_colors[1][1] * local_ratio)
                b = int(animated_colors[0][2] * (1 - local_ratio) + animated_colors[1][2] * local_ratio)
            elif ratio < 0.66:
                # 中間色から最後の色へ
                local_ratio = (ratio - 0.33) / 0.33
                r = int(animated_colors[1][0] * (1 - local_ratio) + animated_colors[2][0] * local_ratio)
                g = int(animated_colors[1][1] * (1 - local_ratio) + animated_colors[2][1] * local_ratio)
                b = int(animated_colors[1][2] * (1 - local_ratio) + animated_colors[2][2] * local_ratio)
            else:
                # 最後の色から外側へ（暗く）
                local_ratio = (ratio - 0.66) / 0.34
                r = int(animated_colors[2][0] * (1 - local_ratio) + BG_DARK[0] * local_ratio)
                g = int(animated_colors[2][1] * (1 - local_ratio) + BG_DARK[1] * local_ratio)
                b = int(animated_colors[2][2] * (1 - local_ratio) + BG_DARK[2] * local_ratio)
            
            # ノイズを追加（テクスチャ感、ただし固定シードでちらつきを減らす）
            # ノイズを位置ベースにして、毎フレーム同じ位置で同じノイズを生成
            noise_seed = int(center_x + center_y + i) % 11 - 5
            r = max(0, min(255, r + noise_seed))
            g = max(0, min(255, g + noise_seed))
            b = max(0, min(255, b + noise_seed))
            
            color = (r, g, b)
            # 円を描画（間隔を空けてパフォーマンス向上、でも見た目は滑らか）
            pygame.draw.circle(screen, color, (int(center_x), int(center_y)), radius - i)
    
    def draw_energy_wave(self, screen, center_x, center_y, time_offset=0):
        """エネルギー波を描画（より滑らかに）"""
        wave_count = 3
        for i in range(wave_count):
            # 波の速度を遅くして滑らかに
            wave_radius = 100 + (self.time + time_offset) * 1.5 + i * 50  # 2 → 1.5
            wave_alpha = int(100 * (1 - (wave_radius % 200) / 200))
            if wave_alpha > 0:
                wave_surf = pygame.Surface((wave_radius * 2, wave_radius * 2), pygame.SRCALPHA)
                wave_color = (96, 165, 250, wave_alpha)
                pygame.draw.circle(wave_surf, wave_color, (wave_radius, wave_radius), wave_radius, 2)
                screen.blit(wave_surf, (int(center_x - wave_radius), int(center_y - wave_radius)))
    
    def draw(self, screen):
        """タイトル画面背景を描画"""
        # ベース背景（暗い色）
        screen.fill(BG_DARK)
        
        # 複数の中心点から放射状グラデーションを描画
        for i, (center_x, center_y) in enumerate(self.gradient_centers):
            # 中心点をアニメーション（移動、より滑らかに）
            animated_x = center_x + math.sin(self.time * 0.005 + i) * 50  # 0.02 → 0.005
            animated_y = center_y + math.cos(self.time * 0.005 + i) * 50  # 0.02 → 0.005
            
            # 放射状グラデーションを描画
            colors = self.gradient_colors[i % len(self.gradient_colors)]
            self.draw_radial_gradient(screen, animated_x, animated_y, colors, 
                                     int(SCREEN_WIDTH * 0.8), time_offset=i * 100)
        
        # エネルギーパーティクルを描画
        for particle in self.energy_particles:
            particle.draw(screen)
        
        # エネルギー波を描画（各中心点から）
        for i, (center_x, center_y) in enumerate(self.gradient_centers):
            animated_x = center_x + math.sin(self.time * 0.005 + i) * 50  # 0.02 → 0.005
            animated_y = center_y + math.cos(self.time * 0.005 + i) * 50  # 0.02 → 0.005
            self.draw_energy_wave(screen, animated_x, animated_y, time_offset=i * 50)

# エフェクトクラス（演出用、改良版）
class Effect:
    def __init__(self, text, x, y, duration=60, color=YELLOW, scale_effect=True):
        self.text = text
        self.x = x
        self.y = y
        self.duration = duration
        self.timer = 0
        self.active = True
        self.color = color
        self.scale_effect = scale_effect
        self.rotation = 0
        
    def update(self):
        self.timer += 1
        if self.timer >= self.duration:
            self.active = False
        self.y -= 2  # 上に移動
        self.rotation += 2  # 回転効果
        
    def draw(self, screen):
        if self.active:
            # 派手な演出
            progress = self.timer / self.duration
            alpha = int(255 * (1 - progress))
            
            if self.scale_effect:
                size = int(60 + math.sin(progress * math.pi) * 20)
            else:
                size = 60 + int(self.timer * 0.5)
            
            # TextRendererのdraw_effectを使用（かっこよく）
            # ただし、サイズと位置は動的に変更
            TextRenderer.draw_effect(screen, self.text, self.x, self.y, 
                                   size=size, color=self.color, center=False)

# ゲームクラス
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("yokero")
        self.clock = pygame.time.Clock()
        self.state = GameState.START
        self.player = Player()
        self.obstacles: List[Obstacle] = []
        self.items: List[Item] = []
        self.effects: List[Effect] = []
        self.score_manager = ScoreManager()
        
        # パーティクルシステムと画面エフェクト
        self.particle_system = ParticleSystem()
        self.screen_shake = ScreenShake()
        self.flash_alpha = 0  # フラッシュエフェクト用
        self.game_over_effect_timer = 0  # ゲームオーバー演出のタイマー
        
        # キー状態を保持
        self.keys = {
            pygame.K_UP: False,
            pygame.K_DOWN: False
        }
        
        self.score = 0
        self.game_started = False
        self.game_time = 0
        self.last_obstacle_spawn = 0
        self.last_item_spawn = 0
        self.last_speed_up = 0
        self.last_obstacle_count_increase = 0  # 最後に障害物の数を増やした時間
        self.obstacle_increase_counter = 0  # 追加処理の回数カウント
        self.obstacle_spawn_interval = 120  # フレーム
        self.item_spawn_interval = 300  # フレーム
        self.base_obstacle_speed = 3
        self.obstacle_speed = self.base_obstacle_speed
        self.obstacle_count = 0
        self.obstacle_spawn_count = 1  # 一度に生成する障害物の数
        
        # アイテム効果（10秒 = 60FPS * 10 = 600フレーム）
        item_effect_duration = 600  # 10秒
        self.item_effects = {
            'speed': {'active': False, 'timer': 0, 'duration': item_effect_duration},
            'shrink': {'active': False, 'timer': 0, 'duration': item_effect_duration},
            'obstacle_shrink': {'active': False, 'timer': 0, 'duration': item_effect_duration},
            'slow': {'active': False, 'timer': 0, 'duration': item_effect_duration}
        }
        
        # スコアタイマー
        self.score_timer = 0
        
        # 背景Surfaceをキャッシュ（パフォーマンス向上）
        self.bg_surface = None
        self._create_bg_surface()
        
        # タイトル画面専用の背景
        self.title_background = TitleBackground()
        
        # タイトル画面のウインドウ表示状態
        self.show_window = None  # None, 'scores', 'instructions'
    
    def _create_bg_surface(self):
        """背景Surfaceを作成（一度だけ）"""
        self.bg_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        for i in range(SCREEN_HEIGHT):
            ratio = i / SCREEN_HEIGHT
            r = int(BG_DARK[0] * (1 - ratio) + BG_DARKEST[0] * ratio)
            g = int(BG_DARK[1] * (1 - ratio) + BG_DARKEST[1] * ratio)
            b = int(BG_DARK[2] * (1 - ratio) + BG_DARKEST[2] * ratio)
            pygame.draw.line(self.bg_surface, (r, g, b), (0, i), (SCREEN_WIDTH, i))
        
    def handle_start_screen(self, event):
        # ウインドウが開いている場合の処理
        if self.show_window:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.show_window = None
                return True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                window_width = int(600)
                window_height = int(600)
                window_x = (SCREEN_WIDTH - window_width) // 2
                window_y = (SCREEN_HEIGHT - window_height) // 2
                close_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, window_y + window_height - 70, 200, 45)
                # 閉じるボタンをクリックした場合
                if close_button_rect.collidepoint(mouse_x, mouse_y):
                    self.show_window = None
                    return True
                # ウインドウ外をクリックしたら閉じる
                elif not (window_x <= mouse_x <= window_x + window_width and window_y <= mouse_y <= window_y + window_height):
                    self.show_window = None
                    return True
            return True
        
        # 通常のボタン処理
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            
            # ゲームスタートボタン
            if 450 <= mouse_x <= 750 and 280 <= mouse_y <= 330:
                self.state = GameState.PLAYING
                self.reset_game()
                
            # スコアボタン
            elif 450 <= mouse_x <= 750 and 360 <= mouse_y <= 410:
                self.show_window = 'scores'
                
            # 説明ボタン
            elif 450 <= mouse_x <= 750 and 440 <= mouse_y <= 490:
                self.show_window = 'instructions'
                
            # 終了ボタン
            elif 450 <= mouse_x <= 750 and 520 <= mouse_y <= 570:
                return False
                
        return True
        
    def handle_playing_screen(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not self.game_started:
                self.game_started = True
                self.effects.append(Effect("Go!!!", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, 90, color=YELLOW))
                # 開始時のパーティクルエフェクト
                self.particle_system.add_explosion(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, YELLOW, count=50, speed=10)
            elif event.key == pygame.K_ESCAPE and self.game_started:
                self.state = GameState.PAUSED
            # キー状態を更新
            if event.key in self.keys:
                self.keys[event.key] = True
        elif event.type == pygame.KEYUP:
            if event.key in self.keys:
                self.keys[event.key] = False
                
    def handle_paused_screen(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state = GameState.PLAYING
            elif event.key == pygame.K_RETURN:
                self.state = GameState.START
                self.reset_game()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            
            box_width, box_height = 400, 250
            box_x = (SCREEN_WIDTH - box_width) // 2
            box_y = (SCREEN_HEIGHT - box_height) // 2
            
            # 再開ボタン
            if box_x + 50 <= mouse_x <= box_x + box_width - 50 and box_y + 120 <= mouse_y <= box_y + 165:
                self.state = GameState.PLAYING
                
            # ゲーム終了ボタン
            elif box_x + 50 <= mouse_x <= box_x + box_width - 50 and box_y + 180 <= mouse_y <= box_y + 225:
                self.state = GameState.START
                self.reset_game()
                
    def handle_result_screen(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.state = GameState.PLAYING
                self.reset_game()
            elif event.key == pygame.K_ESCAPE:
                self.state = GameState.START
                self.reset_game()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            
            # もう一度遊ぶ
            if 450 <= mouse_x <= 750 and 380 <= mouse_y <= 430:
                self.state = GameState.PLAYING
                self.reset_game()
                
            # タイトルに戻る
            elif 450 <= mouse_x <= 750 and 450 <= mouse_y <= 500:
                self.state = GameState.START
                self.reset_game()
                
            # ゲーム終了
            elif 450 <= mouse_x <= 750 and 520 <= mouse_y <= 570:
                return False
                
        return True
        
    def reset_game(self):
        self.player = Player()
        self.obstacles = []
        self.items = []
        self.effects = []
        self.particle_system = ParticleSystem()
        self.screen_shake = ScreenShake()
        self.wind_effect = WindEffect()
        self.flash_alpha = 0
        self.game_over_effect_timer = 0
        self.score = 0
        self.game_started = False
        self.game_time = 0
        self.last_obstacle_spawn = 0
        self.last_item_spawn = 0
        self.last_speed_up = 0
        self.last_obstacle_count_increase = 0
        self.obstacle_increase_counter = 0
        self.obstacle_spawn_interval = 120
        self.item_spawn_interval = 300
        self.obstacle_speed = self.base_obstacle_speed
        self.obstacle_count = 0
        self.obstacle_spawn_count = 1
        self.score_timer = 0
        
        # アイテム効果をリセット
        for effect in self.item_effects:
            self.item_effects[effect]['active'] = False
            self.item_effects[effect]['timer'] = 0
            
    def spawn_obstacle(self):
        """障害物を生成（複数生成可能、バリエーションあり）"""
        obstacle_types = [
            # タイプ1: 縦長の長方形（従来型）
            {'width': 40, 'height_range': (80, 200)},
            # タイプ2: 正方形
            {'width': 60, 'height_range': (60, 60)},
            # タイプ3: 横長の長方形
            {'width': 80, 'height_range': (40, 60)},
            # タイプ4: 細長い縦長
            {'width': 30, 'height_range': (100, 180)},
            # タイプ5: 中サイズの正方形
            {'width': 50, 'height_range': (50, 50)},
        ]
        
        for _ in range(self.obstacle_spawn_count):
            # ランダムにタイプを選択
            obstacle_type = random.choice(obstacle_types)
            width = obstacle_type['width']
            min_height, max_height = obstacle_type['height_range']
            height = random.randint(min_height, max_height)
            y = random.randint(0, SCREEN_HEIGHT - height)
            obstacle = Obstacle(SCREEN_WIDTH, y, width, height, self.obstacle_speed)
            self.obstacles.append(obstacle)
        
    def spawn_item(self):
        item_types = ['speed', 'shrink', 'obstacle_shrink', 'slow']
        item_type = random.choice(item_types)
        y = random.randint(50, SCREEN_HEIGHT - 50)
        item = Item(SCREEN_WIDTH, y, item_type)
        self.items.append(item)
        
    def update_game(self):
        # ゲームオーバー演出中は更新を続ける
        if not self.game_started and self.game_over_effect_timer == 0:
            return
            
        # ゲームオーバー演出中でない場合のみ、通常のゲーム進行を更新
        if self.game_over_effect_timer == 0:
            self.game_time += 1
            self.score_timer += 1
            
            # スコア加算（0.1秒ごと = 6フレームごと）
            if self.score_timer >= 6:
                self.score += 1
                self.score_timer = 0
                
            # 障害物の生成
            if self.game_time - self.last_obstacle_spawn >= self.obstacle_spawn_interval:
                self.spawn_obstacle()
                self.last_obstacle_spawn = self.game_time
                # 時間経過で生成間隔を短く
                if self.obstacle_spawn_interval > 60:
                    self.obstacle_spawn_interval -= 1
            
            # 時間経過で障害物の数を増やす（15秒ごと = 900フレームごと）
            # 追加処理を3回行うと追加数を+1する
            # カウンターの増加量は現在の追加数に応じて変わる
            if self.game_time - self.last_obstacle_count_increase >= 300:  # 15秒ごと
                # カウンターの増加量 = 現在の追加数
                increment = self.obstacle_spawn_count
                self.obstacle_increase_counter += increment
                self.last_obstacle_count_increase = self.game_time
                
                # 追加処理を3回行ったら（3の倍数の時）、追加数を+1する
                if self.obstacle_increase_counter % 3 == 0:
                    self.obstacle_spawn_count += 1  # 追加数を+1
                    
            # アイテムの生成（出現頻度を少し増やす）
            if self.game_time - self.last_item_spawn >= self.item_spawn_interval:
                if random.random() < 0.4:  # 40%の確率
                    self.spawn_item()
                self.last_item_spawn = self.game_time
                
            # 速度上昇（20秒 = 1200フレームごと）
            if self.game_time - self.last_speed_up >= 1200:
                self.obstacle_speed += 0.5
                self.base_obstacle_speed += 0.5
                self.last_speed_up = self.game_time
                # すべての障害物の速度を更新
                for obstacle in self.obstacles:
                    obstacle.base_speed = self.obstacle_speed
                    if not self.item_effects['slow']['active']:
                        obstacle.speed = self.obstacle_speed
                # 演出
                self.effects.append(Effect("Speed UP!!!", SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2, 90, color=YELLOW))
                # パーティクルエフェクト
                self.particle_system.add_explosion(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, YELLOW, count=30, speed=8)
                # 風エフェクトを開始（速度に応じた密度）
                speed_factor = self.obstacle_speed / self.base_obstacle_speed
                self.wind_effect.start(duration=120, density=min(2.0, speed_factor))
                
            # プレイヤーの更新（キー状態を使用）- ゲームオーバー演出中は停止
            keys_pressed = pygame.key.get_pressed()
            # キー状態を更新（毎フレーム最新の状態を取得）
            self.keys[pygame.K_UP] = keys_pressed[pygame.K_UP]
            self.keys[pygame.K_DOWN] = keys_pressed[pygame.K_DOWN]
            self.player.update(self.keys)
        
        # アイテム効果の更新
        for effect_name, effect_data in self.item_effects.items():
            if effect_data['active']:
                effect_data['timer'] += 1
                if effect_data['timer'] >= effect_data['duration']:
                    effect_data['active'] = False
                    effect_data['timer'] = 0
                    # 効果を解除
                    if effect_name == 'speed':
                        self.player.apply_speed_boost(1.0)
                    elif effect_name == 'shrink':
                        self.player.apply_size_reduction(1.0)
                    elif effect_name == 'obstacle_shrink':
                        for obstacle in self.obstacles:
                            obstacle.apply_size_reduction(1.0)
                    elif effect_name == 'slow':
                        for obstacle in self.obstacles:
                            obstacle.apply_speed_reduction(1.0)
                            
        # アイテム効果の適用
        if self.item_effects['speed']['active']:
            self.player.apply_speed_boost(1.5)
        if self.item_effects['shrink']['active']:
            self.player.apply_size_reduction(0.6)
        if self.item_effects['obstacle_shrink']['active']:
            for obstacle in self.obstacles:
                obstacle.apply_size_reduction(0.7)
        if self.item_effects['slow']['active']:
            for obstacle in self.obstacles:
                obstacle.apply_speed_reduction(0.7)
                
        # 障害物の更新（ゲームオーバー演出中は停止）
        if self.game_over_effect_timer == 0:
            for obstacle in self.obstacles[:]:
                obstacle.update()
                if obstacle.x + obstacle.width < 0:
                    self.obstacles.remove(obstacle)
                # 衝突判定
                if self.player.get_rect().colliderect(obstacle.get_rect()):
                    # 衝突時の派手な演出を開始
                    collision_x = obstacle.x + obstacle.width // 2
                    collision_y = obstacle.y + obstacle.height // 2
                    self.particle_system.add_explosion(collision_x, collision_y, WHITE, count=40, speed=8)
                    self.screen_shake.shake(intensity=15, duration=60)  # 長めのシェイク
                    self.flash_alpha = 200  # 強いフラッシュ
                    self.game_over_effect_timer = 90  # 1.5秒（90フレーム）の演出時間
                    # ゲームを停止（プレイヤーと障害物の移動を停止）
                    self.game_started = False
                    return
                
        # アイテムの更新（ゲームオーバー演出中は停止）
        if self.game_over_effect_timer == 0:
            for item in self.items[:]:
                if not item.collected:
                    item.update()
                    if item.x + item.width < 0:
                        self.items.remove(item)
                    # 取得判定
                    elif self.player.get_rect().colliderect(item.get_rect()):
                        item.collected = True
                        self.score += 100
                        # 効果を適用
                        self.item_effects[item.type]['active'] = True
                        self.item_effects[item.type]['timer'] = 0
                        
                        # 派手な演出
                        item_x = item.x + item.width // 2
                        item_y = item.y + item.height // 2
                        self.particle_system.add_explosion(item_x, item_y, item.color, count=25, speed=6)
                        self.particle_system.add_sparkle(item_x, item_y, item.color, count=15)
                        self.flash_alpha = 100  # フラッシュエフェクト
                        
                        # スコア加算エフェクト
                        self.effects.append(Effect("+100", item_x, item_y, duration=40, color=item.color))
                        
                        self.items.remove(item)
                    
        # エフェクトの更新
        for effect in self.effects[:]:
            effect.update()
            if not effect.active:
                self.effects.remove(effect)
        
        # パーティクルシステムの更新
        self.particle_system.update()
        
        # 画面シェイクの更新
        self.screen_shake.update()
        
        # 風エフェクトの更新
        self.wind_effect.update()
        
        # フラッシュエフェクトの減衰
        if self.flash_alpha > 0:
            self.flash_alpha = max(0, self.flash_alpha - 5)
        
        # ゲームオーバー演出の処理
        if self.game_over_effect_timer > 0:
            self.game_over_effect_timer -= 1
            # 演出が終わったらリザルト画面に移行
            if self.game_over_effect_timer <= 0:
                self.end_game()
                
    def end_game(self):
        is_new_high = self.score_manager.is_new_high_score(self.score)
        if is_new_high:
            self.score_manager.save_score(self.score)
            self.effects.append(Effect("NEW HIGH SCORE!!!", SCREEN_WIDTH // 2 - 200, 200, 180, color=YELLOW))
            # ハイスコア更新時の派手な演出
            self.particle_system.add_explosion(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, YELLOW, count=60, speed=12)
            self.particle_system.add_sparkle(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, YELLOW, count=30)
        else:
            self.score_manager.save_score(self.score)
        self.state = GameState.RESULT
        
    def draw_gradient_background(self):
        """グラデーション背景を描画（キャッシュを使用）"""
        if self.bg_surface:
            self.screen.blit(self.bg_surface, (0, 0))
        else:
            # フォールバック
            self.screen.fill(BG_DARK)
    
    def draw_gradient_rect(self, surface, rect, color1, color2, direction='vertical', radius=0):
        """グラデーション矩形を描画"""
        x, y, w, h = rect
        if radius > 0:
            # 角丸の場合は複数の線で描画
            for i in range(h):
                ratio = i / h if direction == 'vertical' else 0.5
                if direction == 'horizontal':
                    ratio = i / w
                r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
                g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
                b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
                pygame.draw.line(surface, (r, g, b), (x, y + i), (x + w, y + i))
        else:
            # 通常の矩形
            for i in range(h):
                ratio = i / h if direction == 'vertical' else 0.5
                if direction == 'horizontal':
                    ratio = i / w
                r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
                g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
                b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
                pygame.draw.line(surface, (r, g, b), (x, y + i), (x + w, y + i))
    
    def draw_rounded_rect(self, surface, rect, color, radius=10, border_width=0, border_color=None):
        """角丸矩形を描画（改善版）"""
        x, y, w, h = rect
        if radius <= 0:
            if border_width > 0 and border_color:
                pygame.draw.rect(surface, border_color, rect, border_width)
            else:
                pygame.draw.rect(surface, color, rect)
            return
        
        # 角丸矩形を描画
        # メインの矩形（角を除く）
        pygame.draw.rect(surface, color, (x + radius, y, w - radius * 2, h))
        pygame.draw.rect(surface, color, (x, y + radius, w, h - radius * 2))
        
        # 角の円
        if radius > 0:
            pygame.draw.circle(surface, color, (x + radius, y + radius), radius)
            pygame.draw.circle(surface, color, (x + w - radius, y + radius), radius)
            pygame.draw.circle(surface, color, (x + radius, y + h - radius), radius)
            pygame.draw.circle(surface, color, (x + w - radius, y + h - radius), radius)
        
        # ボーダー（角丸対応）
        if border_width > 0 and border_color:
            # 上下の線
            pygame.draw.line(surface, border_color, (x + radius, y), (x + w - radius, y), border_width)
            pygame.draw.line(surface, border_color, (x + radius, y + h), (x + w - radius, y + h), border_width)
            # 左右の線
            pygame.draw.line(surface, border_color, (x, y + radius), (x, y + h - radius), border_width)
            pygame.draw.line(surface, border_color, (x + w, y + radius), (x + w, y + h - radius), border_width)
            # 角の円弧（簡易版：円で表現）
            if radius > border_width:
                pygame.draw.arc(surface, border_color, (x, y, radius * 2, radius * 2), math.pi / 2, math.pi, border_width)
                pygame.draw.arc(surface, border_color, (x + w - radius * 2, y, radius * 2, radius * 2), 0, math.pi / 2, border_width)
                pygame.draw.arc(surface, border_color, (x, y + h - radius * 2, radius * 2, radius * 2), math.pi, 3 * math.pi / 2, border_width)
                pygame.draw.arc(surface, border_color, (x + w - radius * 2, y + h - radius * 2, radius * 2, radius * 2), 3 * math.pi / 2, 2 * math.pi, border_width)
    
    def draw_button(self, x, y, width, height, text, font, hover=False, clicked=False):
        """かっこいいボタンを描画（グラデーション、影、ニューモーフィズム、アニメーション）"""
        # アニメーション効果
        scale = 1.05 if hover else 1.0
        if clicked:
            scale = 0.98  # 押し込み感
            y_offset = 2
        else:
            y_offset = -2 if hover else 0  # 浮き上がり効果
        
        # スケール適用
        scaled_width = int(width * scale)
        scaled_height = int(height * scale)
        scaled_x = x + (width - scaled_width) // 2
        scaled_y = y + (height - scaled_height) // 2 + y_offset
        
        # 角丸の半径
        radius = 12
        
        # 1. ドロップシャドウ（複数層、ぼかし影、浮き上がり効果）
        shadow_offset = 4 if hover else 3
        shadow_layers = 5
        for i in range(shadow_layers):
            shadow_alpha = 30 - i * 5
            shadow_offset_i = shadow_offset + i
            shadow_rect = (scaled_x + shadow_offset_i, scaled_y + shadow_offset_i, 
                          scaled_width, scaled_height)
            shadow_surf = pygame.Surface((scaled_width + shadow_offset_i * 2, 
                                         scaled_height + shadow_offset_i * 2), pygame.SRCALPHA)
            self.draw_rounded_rect(shadow_surf, 
                                 (shadow_offset_i, shadow_offset_i, scaled_width, scaled_height),
                                 (0, 0, 0, shadow_alpha), radius=radius)
            self.screen.blit(shadow_surf, (scaled_x - shadow_offset_i, scaled_y - shadow_offset_i))
        
        # 2. ニューモーフィズム効果（立体感のある影とハイライト）
        if not hover and not clicked:
            # 外側の影（暗い）
            outer_shadow_rect = (scaled_x - 2, scaled_y - 2, scaled_width + 4, scaled_height + 4)
            shadow_surf = pygame.Surface((scaled_width + 4, scaled_height + 4), pygame.SRCALPHA)
            self.draw_rounded_rect(shadow_surf, (2, 2, scaled_width, scaled_height),
                                 (0, 0, 0, 40), radius=radius + 2)
            self.screen.blit(shadow_surf, (scaled_x - 2, scaled_y - 2))
            
            # 内側のハイライト（明るい）
            highlight_rect = (scaled_x + 2, scaled_y + 2, scaled_width - 4, scaled_height - 4)
            highlight_surf = pygame.Surface((scaled_width, scaled_height), pygame.SRCALPHA)
            self.draw_rounded_rect(highlight_surf, (0, 0, scaled_width - 4, scaled_height - 4),
                                  (255, 255, 255, 30), radius=radius - 2)
            self.screen.blit(highlight_surf, (scaled_x + 2, scaled_y + 2))
        
        # 3. グラデーション背景（垂直グラデーション、複数色）
        button_surf = pygame.Surface((scaled_width, scaled_height), pygame.SRCALPHA)
        if hover:
            # ホバー時：より明るいグラデーション
            color1 = BUTTON_HOVER_START
            color2 = BUTTON_HOVER_END
            # 中間色を追加（3色グラデーション）
            color_mid = tuple((c1 + c2) // 2 for c1, c2 in zip(color1, color2))
            # 上半分
            for i in range(scaled_height // 2):
                ratio = i / (scaled_height // 2)
                r = int(color1[0] * (1 - ratio) + color_mid[0] * ratio)
                g = int(color1[1] * (1 - ratio) + color_mid[1] * ratio)
                b = int(color1[2] * (1 - ratio) + color_mid[2] * ratio)
                pygame.draw.line(button_surf, (r, g, b), (0, i), (scaled_width, i))
            # 下半分
            for i in range(scaled_height // 2, scaled_height):
                ratio = (i - scaled_height // 2) / (scaled_height // 2)
                r = int(color_mid[0] * (1 - ratio) + color2[0] * ratio)
                g = int(color_mid[1] * (1 - ratio) + color2[1] * ratio)
                b = int(color_mid[2] * (1 - ratio) + color2[2] * ratio)
                pygame.draw.line(button_surf, (r, g, b), (0, i), (scaled_width, i))
        else:
            # 通常時：2色グラデーション
            color1 = BUTTON_BLUE_START
            color2 = BUTTON_BLUE_END
            for i in range(scaled_height):
                ratio = i / scaled_height
                r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
                g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
                b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
                pygame.draw.line(button_surf, (r, g, b), (0, i), (scaled_width, i))
        
        # 角丸矩形のマスクを作成して適用（pygameにはborder_radiusがないので手動で実装）
        mask = pygame.Surface((scaled_width, scaled_height), pygame.SRCALPHA)
        # 角丸矩形のマスクを手動で描画
        # メインの矩形
        pygame.draw.rect(mask, (255, 255, 255, 255), (radius, 0, scaled_width - radius * 2, scaled_height))
        pygame.draw.rect(mask, (255, 255, 255, 255), (0, radius, scaled_width, scaled_height - radius * 2))
        # 角の円
        if radius > 0:
            pygame.draw.circle(mask, (255, 255, 255, 255), (radius, radius), radius)
            pygame.draw.circle(mask, (255, 255, 255, 255), (scaled_width - radius, radius), radius)
            pygame.draw.circle(mask, (255, 255, 255, 255), (radius, scaled_height - radius), radius)
            pygame.draw.circle(mask, (255, 255, 255, 255), (scaled_width - radius, scaled_height - radius), radius)
        # マスクを適用（角丸以外を透明に）
        button_surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        
        self.screen.blit(button_surf, (scaled_x, scaled_y))
        
        # 4. ボーダー（グラデーション、アニメーション）
        border_width = 2
        if hover:
            # ホバー時：明るいボーダー
            border_color = tuple(min(255, c + 30) for c in BORDER_COLOR)
        else:
            border_color = BORDER_COLOR
        
        # ボーダーを描画（角丸対応）
        border_surf = pygame.Surface((scaled_width, scaled_height), pygame.SRCALPHA)
        # 上下の線
        pygame.draw.line(border_surf, border_color, (radius, 0), (scaled_width - radius, 0), border_width)
        pygame.draw.line(border_surf, border_color, (radius, scaled_height), (scaled_width - radius, scaled_height), border_width)
        # 左右の線
        pygame.draw.line(border_surf, border_color, (0, radius), (0, scaled_height - radius), border_width)
        pygame.draw.line(border_surf, border_color, (scaled_width, radius), (scaled_width, scaled_height - radius), border_width)
        # 角の円弧
        if radius > 0:
            pygame.draw.arc(border_surf, border_color, (0, 0, radius * 2, radius * 2), math.pi / 2, math.pi, border_width)
            pygame.draw.arc(border_surf, border_color, (scaled_width - radius * 2, 0, radius * 2, radius * 2), 0, math.pi / 2, border_width)
            pygame.draw.arc(border_surf, border_color, (0, scaled_height - radius * 2, radius * 2, radius * 2), math.pi, 3 * math.pi / 2, border_width)
            pygame.draw.arc(border_surf, border_color, (scaled_width - radius * 2, scaled_height - radius * 2, radius * 2, radius * 2), 3 * math.pi / 2, 2 * math.pi, border_width)
        self.screen.blit(border_surf, (scaled_x, scaled_y))
        
        # 5. 内側シャドウ（上部にハイライト、下部に影）
        if not clicked:
            # 上部のハイライト
            highlight_surf = pygame.Surface((scaled_width - 4, scaled_height // 3), pygame.SRCALPHA)
            highlight_surf.fill((255, 255, 255, 20))
            self.screen.blit(highlight_surf, (scaled_x + 2, scaled_y + 2))
        
        # 6. テキスト（影付き）
        text_surface = font.render(text, True, TEXT_LIGHT)
        text_rect = text_surface.get_rect(center=(scaled_x + scaled_width // 2, 
                                                  scaled_y + scaled_height // 2))
        # テキストの影
        shadow_text = font.render(text, True, (0, 0, 0))
        self.screen.blit(shadow_text, (text_rect.x + 1, text_rect.y + 1))
        self.screen.blit(text_surface, text_rect)
        
        return pygame.Rect(scaled_x, scaled_y, scaled_width, scaled_height)
    
    def draw_window(self, title, content_lines, close_button_text="閉じる"):
        """かっこいいウインドウを描画"""
        window_width = int(600 * 1.3)  # 780
        window_height = int(500 * 1.3)  # 650
        window_x = (SCREEN_WIDTH - window_width) // 2
        window_y = (SCREEN_HEIGHT - window_height) // 2
        radius = 16
        
        # 1. 背景を半透明で覆う
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # 2. ウインドウの影（複数層）
        shadow_layers = 8
        for i in range(shadow_layers):
            shadow_alpha = 40 - i * 4
            shadow_offset = i * 2
            shadow_surf = pygame.Surface((window_width + shadow_offset * 2, window_height + shadow_offset * 2), pygame.SRCALPHA)
            self.draw_rounded_rect(shadow_surf, 
                                 (shadow_offset, shadow_offset, window_width, window_height),
                                 (0, 0, 0, shadow_alpha), radius=radius)
            self.screen.blit(shadow_surf, (window_x - shadow_offset, window_y - shadow_offset))
        
        # 3. ウインドウの背景（グラデーション）
        window_surf = pygame.Surface((window_width, window_height), pygame.SRCALPHA)
        # グラデーション背景
        color1 = (15, 23, 42)  # 暗い青
        color2 = (2, 6, 23)  # より暗い青
        for i in range(window_height):
            ratio = i / window_height
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            pygame.draw.line(window_surf, (r, g, b), (0, i), (window_width, i))
        
        # 角丸矩形のマスクを作成
        mask = pygame.Surface((window_width, window_height), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), (radius, 0, window_width - radius * 2, window_height))
        pygame.draw.rect(mask, (255, 255, 255, 255), (0, radius, window_width, window_height - radius * 2))
        if radius > 0:
            pygame.draw.circle(mask, (255, 255, 255, 255), (radius, radius), radius)
            pygame.draw.circle(mask, (255, 255, 255, 255), (window_width - radius, radius), radius)
            pygame.draw.circle(mask, (255, 255, 255, 255), (radius, window_height - radius), radius)
            pygame.draw.circle(mask, (255, 255, 255, 255), (window_width - radius, window_height - radius), radius)
        window_surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        self.screen.blit(window_surf, (window_x, window_y))
        
        # 4. ボーダー（グラデーション）
        border_width = 2
        border_color = BORDER_COLOR
        border_surf = pygame.Surface((window_width, window_height), pygame.SRCALPHA)
        pygame.draw.line(border_surf, border_color, (radius, 0), (window_width - radius, 0), border_width)
        pygame.draw.line(border_surf, border_color, (radius, window_height), (window_width - radius, window_height), border_width)
        pygame.draw.line(border_surf, border_color, (0, radius), (0, window_height - radius), border_width)
        pygame.draw.line(border_surf, border_color, (window_width, radius), (window_width, window_height - radius), border_width)
        if radius > 0:
            pygame.draw.arc(border_surf, border_color, (0, 0, radius * 2, radius * 2), math.pi / 2, math.pi, border_width)
            pygame.draw.arc(border_surf, border_color, (window_width - radius * 2, 0, radius * 2, radius * 2), 0, math.pi / 2, border_width)
            pygame.draw.arc(border_surf, border_color, (0, window_height - radius * 2, radius * 2, radius * 2), math.pi, 3 * math.pi / 2, border_width)
            pygame.draw.arc(border_surf, border_color, (window_width - radius * 2, window_height - radius * 2, radius * 2, radius * 2), 3 * math.pi / 2, 2 * math.pi, border_width)
        self.screen.blit(border_surf, (window_x, window_y))
        
        # 5. タイトル
        title_y = window_y + 40
        TextRenderer.draw_title(self.screen, title, SCREEN_WIDTH // 2, title_y, size=48, color=TEXT_LIGHT)
        
        # 6. コンテンツ
        content_start_y = window_y + 100
        content_font = get_japanese_font(28)
        line_index = 0
        for line in content_lines:
            if line:  # 空行はスキップ
                y = content_start_y + line_index * 35
                TextRenderer.draw_normal(self.screen, line, SCREEN_WIDTH // 2, y, 
                                       size=28, color=TEXT_LIGHT, center=True)
                line_index += 1
            else:
                # 空行の場合は間隔を空ける
                line_index += 1
        
        # 7. 閉じるボタン
        close_button_y = window_y + window_height - 70
        close_button_font = get_japanese_font(28)
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        close_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, close_button_y, 200, 45)
        hover = close_button_rect.collidepoint(mouse_x, mouse_y)
        clicked = hover and mouse_pressed
        self.draw_button(SCREEN_WIDTH // 2 - 100, close_button_y, 200, 45, 
                        close_button_text, close_button_font, hover, clicked)
        
        return close_button_rect
    
    def draw_start_screen(self):
        # タイトル画面専用の背景を描画
        self.title_background.draw(self.screen)
        
        # タイトル（かっこよく）
        TextRenderer.draw_title(self.screen, "yokero", SCREEN_WIDTH // 2, 120, size=80, color=TEXT_LIGHT)
        
        # ボタン
        button_font = get_japanese_font(32)
        buttons = [
            ("ゲームスタート", 280),
            ("スコア", 360),
            ("説明", 440),
            ("終了", 520)
        ]
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]  # 左クリック状態
        for text, y in buttons:
            hover = 450 <= mouse_x <= 750 and y <= mouse_y <= y + 50
            clicked = hover and mouse_pressed
            self.draw_button(450, y, 300, 50, text, button_font, hover, clicked)
        
        # ウインドウを表示
        if self.show_window == 'scores':
            scores = self.score_manager.scores
            if not scores:
                content_lines = ["まだスコアが記録されていません"]
            else:
                content_lines = [f"{i+1}. {score}" for i, score in enumerate(scores[:10])]
            self.draw_window("スコアランキング", content_lines)
                
        elif self.show_window == 'instructions':
            self.draw_window("説明", INSTRUCTIONS_TEXT)
            
    def draw_playing_screen(self):
        # 画面シェイクのオフセットを適用
        offset_x = self.screen_shake.offset_x
        offset_y = self.screen_shake.offset_y
        
        # 一時的なサーフェスに描画（シェイク対応）
        temp_screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # 背景を描画
        if self.bg_surface:
            temp_screen.blit(self.bg_surface, (0, 0))
        else:
            temp_screen.fill(BG_DARK)
        
        # 風エフェクトを描画（背景の上、障害物の下）
        self.wind_effect.draw(temp_screen)
        
        # パーティクルを描画
        self.particle_system.draw(temp_screen)
        
        # 障害物（グロー効果付き）
        for obstacle in self.obstacles:
            GlowEffect.draw_glow_rect(temp_screen, 
                                     (obstacle.x, obstacle.y, obstacle.width, obstacle.height),
                                     obstacle.color, intensity=2)
            obstacle.draw(temp_screen)
        
        # アイテム（グロー効果付き）
        for item in self.items:
            if not item.collected:
                center_x = item.x + item.width // 2
                center_y = item.y + item.height // 2
                GlowEffect.draw_glow_circle(temp_screen, center_x, center_y, 
                                           item.width // 2, item.color, intensity=3)
                item.draw(temp_screen)
        
        # プレイヤー（グロー効果付き）
        GlowEffect.draw_glow_rect(temp_screen,
                                  (self.player.x, self.player.y, self.player.width, self.player.height),
                                  self.player.color, intensity=3)
        self.player.draw(temp_screen)
        
        # エフェクト
        for effect in self.effects:
            effect.draw(temp_screen)
        
        # シェイクオフセットを適用してメインスクリーンに描画
        self.screen.blit(temp_screen, (offset_x, offset_y))
        
        # フラッシュエフェクト
        if self.flash_alpha > 0:
            flash_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            flash_surf.set_alpha(self.flash_alpha)
            flash_surf.fill(WHITE)
            self.screen.blit(flash_surf, (0, 0))
        
        # スコア表示（シェイクの影響を受けないように最後に描画、見やすく）
        TextRenderer.draw_normal(self.screen, f"スコア: {self.score}", 30, 30, 
                               size=42, color=TEXT_LIGHT, center=False)
        
        # ゲーム開始前のメッセージ（ゲームオーバー演出中は表示しない、演出用）
        if not self.game_started and self.game_over_effect_timer == 0:
            TextRenderer.draw_effect(self.screen, "スペースキーでスタート", 
                                   SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, 
                                   size=52, color=YELLOW)
            
    def draw_paused_screen(self):
        # ゲーム画面を半透明で覆う
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BG_DARKEST)
        self.screen.blit(overlay, (0, 0))
        
        # メニューボックス
        box_width, box_height = 400, 250
        box_x = (SCREEN_WIDTH - box_width) // 2
        box_y = (SCREEN_HEIGHT - box_height) // 2
        
        # 背景
        pygame.draw.rect(self.screen, BG_DARK, (box_x, box_y, box_width, box_height))
        pygame.draw.rect(self.screen, BORDER_COLOR, (box_x, box_y, box_width, box_height), 2)
        
        # タイトル（かっこよく）
        TextRenderer.draw_title(self.screen, "一時停止", SCREEN_WIDTH // 2, box_y + 50, 
                              size=48, color=TEXT_LIGHT)
        
        button_font = get_japanese_font(32)
        buttons = [
            ("再開", box_y + 120),
            ("ゲーム終了", box_y + 180)
        ]
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]  # 左クリック状態
        for text, y in buttons:
            hover = box_x + 50 <= mouse_x <= box_x + box_width - 50 and y <= mouse_y <= y + 45
            clicked = hover and mouse_pressed
            self.draw_button(box_x + 50, y, box_width - 100, 45, text, button_font, hover, clicked)
            
    def draw_result_screen(self):
        self.draw_gradient_background()
        
        # スコア表示
        score_font = get_japanese_font(72)
        score_text = score_font.render(f"スコア: {self.score}", True, TEXT_LIGHT)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 180))
        shadow = score_font.render(f"スコア: {self.score}", True, (0, 0, 0))
        self.screen.blit(shadow, (score_rect.x + 3, score_rect.y + 3))
        self.screen.blit(score_text, score_rect)
        
        # ハイスコア表示
        high_score = self.score_manager.get_high_score()
        high_font = get_japanese_font(44)
        high_text = high_font.render(f"ハイスコア: {high_score}", True, YELLOW)
        high_rect = high_text.get_rect(center=(SCREEN_WIDTH // 2, 260))
        shadow = high_font.render(f"ハイスコア: {high_score}", True, (0, 0, 0))
        self.screen.blit(shadow, (high_rect.x + 2, high_rect.y + 2))
        self.screen.blit(high_text, high_rect)
        
        # エフェクト（NEW HIGH SCORE演出）
        for effect in self.effects:
            effect.draw(self.screen)
            
        # ボタン
        button_font = get_japanese_font(32)
        buttons = [
            ("もう一度遊ぶ", 380),
            ("タイトルに戻る", 450),
            ("ゲーム終了", 520)
        ]
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]  # 左クリック状態
        for text, y in buttons:
            hover = 450 <= mouse_x <= 750 and y <= mouse_y <= y + 50
            clicked = hover and mouse_pressed
            self.draw_button(450, y, 300, 50, text, button_font, hover, clicked)
            
    def run(self):
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
                if self.state == GameState.START:
                    if not self.handle_start_screen(event):
                        running = False
                elif self.state == GameState.PLAYING:
                    self.handle_playing_screen(event)
                elif self.state == GameState.PAUSED:
                    self.handle_paused_screen(event)
                elif self.state == GameState.RESULT:
                    if not self.handle_result_screen(event):
                        running = False
            
            # ゲーム更新（PLAYING状態の時は常に更新）
            if self.state == GameState.PLAYING:
                self.update_game()
            # タイトル画面の背景を更新
            elif self.state == GameState.START:
                self.title_background.update()
                        
            # 描画
            if self.state == GameState.START:
                self.draw_start_screen()
            elif self.state == GameState.PLAYING:
                self.draw_playing_screen()
            elif self.state == GameState.PAUSED:
                self.draw_playing_screen()
                self.draw_paused_screen()
            elif self.state == GameState.RESULT:
                self.draw_result_screen()
                
            pygame.display.flip()
            self.clock.tick(FPS)
            
        pygame.quit()

if __name__ == "__main__":
    try:
        game = Game()
        game.run()
    except Exception as e:
        import traceback
        print(f"エラーが発生しました: {e}")
        traceback.print_exc()
        input("\nEnterキーを押して終了してください...")

