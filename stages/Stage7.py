import pygame  # Pygameライブラリの読み込み
import sys     # 終了処理などのためにsysモジュールを使用
import time    # カウントダウンなど時間管理に利用
import os
from PIL import Image   # pip install pillow

# PyInstaller で EXE 化された場合のファイルパス解決
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_asset_path(relative_path):
    return os.path.join(base_path, relative_path)

from modules import functions as f

# Pygame初期化
pygame.init()
pygame.mixer.init()
pygame.mixer.music.stop()

# 画面サイズ設定
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))  # ウィンドウを作成

# 色定義
black = (0, 0, 0)
white = (255, 255, 255)


# 画像のリサイズ
def img_resize(img_path, width, height):
    # PyInstaller の場合でも機能するように get_asset_path でパスを解決
    asset_path = get_asset_path(img_path) if img_path.startswith("images") else img_path
    img = Image.open(asset_path).resize((width, height))
    surface = pygame.image.fromstring(img.tobytes(), img.size, img.mode).convert()      # pygameが扱える方式に変換
    return surface


background_img = img_resize("images/stage7/hosi2.png", screen_width, screen_height)     # 背景画像

# フォント設定
font = pygame.font.Font(None, 36)


# ブロッククラス
class Block:
    def __init__(self, x, y, width, height, hit_points):
        self.rect = pygame.Rect(x, y, width, height)  # ブロックの位置とサイズ
        self.hit_points = hit_points                 # ブロックの耐久値
        self.initial_hit_points = hit_points         # 得点計算用に初期耐久値を保持

    def draw(self, screen):
        # 耐久値に応じて色を変更
        if self.hit_points == 3:
            color = (255, 0, 0)      # 赤：強い
        elif self.hit_points == 2:
            color = (255, 165, 0)    # オレンジ：中程度
        else:
            color = (0, 255, 0)      # 緑：弱い
        pygame.draw.rect(screen, color, self.rect)  # ブロックの描画

    def hit(self):
        self.hit_points -= 1  # 耐久値を1減らす
        return self.hit_points <= 0  # 耐久値が0以下なら破壊された

# メニュー画面
# def main_menu():
#     while True:
#         screen.fill(black)
#         title = font.render("Block Breaker", True, white)
#         start = font.render("Press SPACE to Start", True, white)
#         quit = font.render("Press Q to Quit", True, white)
#         screen.blit(title, (screen_width//2 - title.get_width()//2, 200))
#         screen.blit(start, (screen_width//2 - start.get_width()//2, 300))
#         screen.blit(quit, (screen_width//2 - quit.get_width()//2, 350))
#         pygame.display.flip()

#         # イベントの監視（キー入力と終了）
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 pygame.quit(); sys.exit()
#             elif event.type == pygame.KEYDOWN:
#                 if event.key == pygame.K_SPACE:
#                     run_game()  # ゲーム開始
#                 elif event.key == pygame.K_q:
#                     pygame.quit(); sys.exit()  # ゲーム終了


# ゲームオーバー画面関数（スコア表示＆リトライ）
def game_over(score):
    while True:
        screen.fill(black)
        final = font.render(f"Final Score: {score}", True, white)
        retry = font.render("Press R to Retry", True, white)
        exit = font.render("Press Q to Quit", True, white)
        # メッセージを中央表示
        screen.blit(final, (screen_width//2 - final.get_width()//2, 200))
        screen.blit(retry, (screen_width//2 - retry.get_width()//2, 300))
        screen.blit(exit, (screen_width//2 - exit.get_width()//2, 350))
        pygame.display.flip()

        # 入力受付
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    run_game()  # 再挑戦
                elif event.key == pygame.K_q:
                    pygame.quit(); sys.exit()  # 終了


# メインのゲーム処理
def run_game():

    clock = pygame.time.Clock()  # ポーズに使うclockを追加

    # --- 素材読み込み ---
    # background_img = pygame.image.load(get_asset_path("images/stage7/hosi2.png"))      # 背景

    hit_sound = pygame.mixer.Sound(get_asset_path("sounds/stage7/reflection_wall.mp3"))  # ボールがぶつかったときの音
    miss_sound = pygame.mixer.Sound(get_asset_path("sounds/stage7/miss.mp3"))
    pygame.mixer.music.load(get_asset_path("sounds/stage7/picopicodisco.mp3"))  # BGM
    pygame.mixer.music.play(-1)

    pygame.display.set_caption("Block Breakerz Stage7")  # タイトルバーの文字列設定
    # パドル設定
    paddle_width = 100
    paddle_height = 10
    paddle_speed = 15    # ★ 数値を修正（元は20）
    """ 削除
    paddle_acceleration = 3  # ★ 押し続けると加速する（元は5）
    left_time = 0
    right_time = 0
    """
    paddle_y = screen_height - 30  # 画面下に配置
    paddle = pygame.Rect(screen_width//2 - paddle_width//2, paddle_y, paddle_width, paddle_height)

    # ボール設定
    ball_radius = 10
    ball_speed_x = 6  # ★ 元は5
    ball_speed_y = 6  # ★ 元は5
    ball_inc = 0.03   # ★ バウンド時の加速率（元は0.05）
    max_speed = 12    # ★ 最大速度制限を追加
    ball = pygame.Rect(screen_width//2, screen_height//2, ball_radius*2, ball_radius*2)

    # ブロック配置設定
    block_width = 60
    block_height = 20
    block_rows = 5
    block_cols = 11
    blocks = []

    # 各行にブロックを配置（耐久値に応じた色分け）
    for row in range(block_rows):
        block_row = []
        for col in range(block_cols):
            x = col * (block_width + 10) + 20
            y = row * (block_height + 10) + 35

            # 耐久値の割り当て
            if row in [0, 1]:  # 最上段2行
                hit_points = 1
                if col in [2, 5, 8]:  # 特定列に赤ブロック（強）
                    hit_points = 3
            elif row == 2:  # 中段
                hit_points = 2
            else:  # 下段
                hit_points = 1

            block_row.append(Block(x, y, block_width, block_height, hit_points))
        blocks.append(block_row)

    # ゲーム開始前のカウントダウン表示
    for i in range(3, 0, -1):
        screen.fill(black)  # 画面を黒で塗りつぶす
        clearscore_text = font.render(f"Clear if over 4000 points", True, white)
        countdown_text = font.render(f"Starting in {i}", True, white)  # カウントテキスト生成
        screen.blit(clearscore_text, (screen_width // 2 - clearscore_text.get_width() // 2, (screen_height // 2 - clearscore_text.get_height() // 2) - 30))  # 中央に表示
        screen.blit(countdown_text, (screen_width // 2 - countdown_text.get_width() // 2, screen_height // 2 - countdown_text.get_height() // 2))  # 中央に表示
        pygame.display.flip()  # 表示を更新
        time.sleep(1)  # 1秒待つ

    running = True
    score = 0  # 得点初期化

    # クリアに必要な目標スコア
    target_score = 4000
    # target_score = 1 #テスト用、使用しないならコメントアウト

    # ゲームループ
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            # Pキーでポーズ
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                f.pause_game(screen, clock, font)
        """ 削除
        # # パドル操作（キー押しっぱなしで加速）
        # keys = pygame.key.get_pressed()
        # if keys[pygame.K_LEFT]:
        #     left_time += 1; right_time = 0
        #     speed = paddle_speed + paddle_acceleration * left_time
        #     if paddle.left > 0:
        #         paddle.left -= speed
        # elif keys[pygame.K_RIGHT]:
        #     right_time += 1; left_time = 0
        #     speed = paddle_speed + paddle_acceleration * right_time
        #     if paddle.right < screen_width:
        #         paddle.right += speed
        # else:
        #     left_time = right_time = 0
        """

        # パドルの操作(滑らかに動かすよう改良)
        keys = pygame.key.get_pressed()
        # 左右のキーが押されてる間一定の速度で移動する
        if keys[pygame.K_LEFT] and paddle.left > 0:
            paddle.left -= paddle_speed
        if keys[pygame.K_RIGHT] and paddle.right < screen_width:
            paddle.right += paddle_speed

        # ボール移動処理
        ball.left += ball_speed_x
        ball.top += ball_speed_y

        # 壁に当たったら反射＆加速
        if ball.left <= 0 or ball.right >= screen_width:
            # ball_speed_y *= (1 + ball_inc)
            ball_speed_x = -ball_speed_x
            hit_sound.play()
        if ball.top <= 0:
            # ball_speed_y *= (1 + ball_inc)
            ball_speed_y = -ball_speed_y
            hit_sound.play()
        if ball.bottom >= screen_height:
            miss_sound.play()
            f.game_over(score, screen, font, screen_width, 7)
            running = False  # ボールが下に落ちたら終了

        # ★ 最大速度制限を適用
        ball_speed_x = max(-max_speed, min(ball_speed_x, max_speed))
        ball_speed_y = max(-max_speed, min(ball_speed_y, max_speed))

        # パドルとの衝突判定
        if ball.colliderect(paddle):
            hit_pos = (ball.left + ball.right) / 2 - (paddle.left + paddle.right) / 2
            ball_speed_x = hit_pos * 0.3  # パドルの中心との相対位置で方向調整
            # ball_speed_y *= (1 + ball_inc)
            ball_speed_y = -ball_speed_y
            hit_sound.play()

        # ブロックとの衝突処理
        for row in blocks:
            for block in row[:]:
                if ball.colliderect(block.rect):
                    ball_speed_y *= (1 + ball_inc)
                    ball_speed_y = -ball_speed_y
                    hit_sound.play()
                    if block.hit():
                        row.remove(block)
                        if block.initial_hit_points == 3:
                            score += 400
                        elif block.initial_hit_points == 2:
                            score += 200
                        else:
                            score += 100

        # 目標スコアを超えていればクリアとし次のステージに実行
        judge = f.is_cleared(score, target_score)
        if judge is True:
            f.game_clear(screen, font, screen_width, screen_height, 7)

        # 画面の反映
        # screen.fill(black)
        bg_x = (screen_width - background_img.get_width()) // 2
        bg_y = (screen_height - background_img.get_height()) // 2
        screen.blit(background_img, (bg_x, bg_y))

        # パドルとボールを描画
        pygame.draw.rect(screen, white, paddle)
        pygame.draw.ellipse(screen, white, ball)

        # ブロックを描画
        for row in blocks:
            for block in row:
                block.draw(screen)

        # スコア表示
        score_text = font.render(f"Score: {score}", True, white)
        screen.blit(score_text, (10, 10))

        # 画面更新と速度調整
        pygame.display.flip()
        pygame.time.delay(30)

    # ゲーム終了後にスコア画面へ
    # game_over(score)


# スクリプト実行時にメニュー表示
if __name__ == "__main__":
    run_game()
