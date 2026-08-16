import pygame
import sys
import time
import os

# PyInstaller で EXE 化された場合のファイルパス解決
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_asset_path(relative_path):
    return os.path.join(base_path, relative_path)

from modules import functions as f
# 次のステージのインポート
from stages import Stage2

# 初期化
pygame.init()
pygame.mixer.init()
pygame.mixer.music.stop()

# 画面サイズ
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))

# 背景画像の読み込み
background_img = pygame.image.load(get_asset_path("images/stage1/miyakojima-12695_TP_V4.jpg"))
background_img = pygame.transform.scale(background_img, (screen_width, screen_height))  # サイズを画面に合わせる

# 色の定義
black = (0, 0, 0)
white = (255, 255, 255)
blue = (0, 0, 255)
green = (0, 255, 0)
sky = (135, 206, 235)

# フォントの設定
font = pygame.font.Font(None, 36)

# パドルの設定
paddle_width = 200  # 横サイズ
paddle_height = 50  # 縦サイズ
paddle_speed = 10
paddle_acceleration = 5
left_passed_time = 0
right_passed_time = 0
paddle = pygame.Rect(screen_width // 2 - paddle_width // 2, screen_height - 30, paddle_width, paddle_height)

# パドル画像の読み込み
# paddle_image = pygame.image.load("sozai\massage_hand.png").convert_alpha()
# paddle_image = pygame.transform.scale(paddle_image, (paddle_width, paddle_height))


# ボールの設定
ball_radius = 30  # ボールの大きさ
ball_speed_x = 5
ball_speed_y = 5
ball_speed_increment = 0.05
ball = pygame.Rect(screen_width // 2, screen_height // 2, ball_radius * 2, ball_radius * 2)

# ボール画像の読み込み
ball_image = pygame.image.load(get_asset_path("images/stage1/beach_ball.png"))
ball_image = pygame.transform.scale(ball_image, (ball_radius * 2, ball_radius * 2))

# ブロックの設定
block_width = 50    # 縦
block_height = 50   # 横
block_rows = 3
block_cols = 7
blocks = []

# ブロック画像の読み込み
block_image = pygame.image.load(get_asset_path("images/stage1/kaigara_nimaigai.png")).convert_alpha()
block_image = pygame.transform.scale(block_image, (block_width, block_height))


# カウントダウン関数
def countdown():
    for i in range(3, 0, -1):
        screen.blit(background_img, (0, 0))
        clearscore_text = font.render(f"Clear if over 1500 points", True, white)
        countdown_text = font.render(f"Starting in {i}", True, white)  # カウントテキスト生成
        screen.blit(clearscore_text, (screen_width // 2 - clearscore_text.get_width() // 2, (screen_height // 2 - clearscore_text.get_height() // 2) - 30))  # 中央に表示
        screen.blit(countdown_text, (screen_width // 2 - countdown_text.get_width() // 2, screen_height // 2 - countdown_text.get_height() // 2))  # 中央に表示
        pygame.display.flip()  # 表示を更新
        time.sleep(1)  # 1秒待つ


# ゲームプレイ関数
def run_game():
    pygame.display.set_caption("Block Breakerz Stage1")

    # --- 素材読み込み ---
    hit_sound = pygame.mixer.Sound(get_asset_path("sounds/stage1/paddle_sound1.mp3"))   # ボールがぶつかったときの音
    miss_sound = pygame.mixer.Sound(get_asset_path("sounds/stage1/miss.mp3"))
    pygame.mixer.music.load(get_asset_path("sounds/stage1/happytime.mp3"))  # BGM
    pygame.mixer.music.play(-1)

    countdown()
    global ball, paddle, ball_speed_x, ball_speed_y, paddle_speed
    global left_passed_time, right_passed_time

    clock = pygame.time.Clock()  # ポーズに使うclockを追加

    runnning = True
    score = 0

    # クリアに必要な目標スコア
    target_score = 1500
    # target_score = 1 #テスト用、使用しないならコメントアウト

    # パドルとボールの初期位置
    paddle.left = screen_width // 2 - paddle_width // 2
    ball.left = screen_width // 2
    ball.top = screen_height // 2
    ball_speed_x = 5
    ball_speed_y = 5
    left_passed_time = 0
    right_passed_time = 0

    # ブロック再生成
    blocks.clear()
    for row in range(block_rows):
        block_row = []

        # 中央寄せのために1行ごとに始点Xを計算
        total_block_width = block_cols * block_width + (block_cols - 1) * 10
        start_x = (screen_width - total_block_width) // 2

        for col in range(block_cols):
            block_x = start_x + col * (block_width + 10)  # 中央から配置開始
            block_y = row * (block_height + 10) + 50      # 上端の余白を少し増やす
            block = pygame.Rect(block_x, block_y, block_width, block_height)
            block_row.append(block)

        blocks.append(block_row)

    while runnning:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # Pキーでポーズ
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                f.pause_game(screen, clock, font)

        # パドルの操作
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            left_passed_time += 1
            right_passed_time = 0
            paddle_speed = (10 + paddle_acceleration * left_passed_time)
            if paddle.left > 0:
                paddle.left -= paddle_speed
        elif keys[pygame.K_RIGHT]:
            right_passed_time += 1
            left_passed_time = 0
            paddle_speed = (10 + paddle_acceleration * right_passed_time)
            if paddle.right < screen_width:
                paddle.right += paddle_speed
        else:
            left_passed_time = 0
            right_passed_time = 0
            paddle_speed = 10

        # ボールの移動
        ball.left += ball_speed_x
        ball.top += ball_speed_y

        # ボールと壁の衝突
        if ball.left <= 0 or ball.right >= screen_width:
            ball_speed_x = -ball_speed_x
            hit_sound.play()

        if ball.top <= 0:
            ball_speed_y = -ball_speed_y
            hit_sound.play()

        if ball.bottom >= screen_height:
            miss_sound.play()
            f.game_over(score, screen, font, screen_width, 1)  # 地面に落ちたらゲームオーバー
            # return score

        # パドルとの衝突
        if ball.colliderect(paddle):
            hit_position = (ball.left + ball.right) / 2 - (paddle.left + paddle.right) / 2
            ball_speed_x = hit_position * 0.3
            ball_speed_y *= (1 + ball_speed_increment)
            ball_speed_y = -ball_speed_y
            hit_sound.play()

        # ブロックとの衝突
        for row in blocks:
            for block in row:
                if ball.colliderect(block):
                    ball_speed_y *= (1 + ball_speed_increment)
                    ball_speed_y = -ball_speed_y
                    hit_sound.play()
                    row.remove(block)
                    score += 100
                    break

        # ブロックが全て消えたら終了
        # if all(len(row) == 0 for row in blocks):
        #     return score  # ブロック全消し → スコア画面へ移行

        # 目標スコアを超えていればクリアとし次のステージに実行
        judge = f.is_cleared(score, target_score)
        if judge is True:
            f.game_clear(screen, font, screen_width, screen_height, 1)

        # 画面の描画
        screen.blit(background_img, (0, 0))  # 背景画像
    # screen.fill(sky) # 背景色
        # screen.blit(paddle_image, paddle) # パドル（画像版）
        pygame.draw.rect(screen, white, paddle)  # パドル
        screen.blit(ball_image, ball)  # ボールの描画（画像版）
        # pygame.draw.ellipse(screen, white, ball) # ボールの描画
        for row in blocks:
            for block in row:
                screen.blit(block_image, block)  # ブロック（画像版）
                # pygame.draw.rect(screen, green, block) # ブロック

        # スコア表示
        score_text = font.render(f"Score: {score}", True, white)
        screen.blit(score_text, (10, 10))

        time.sleep(0.03)
        pygame.display.flip()


# メインループ（再プレイ選択あり）
if __name__ == "__main__":
    while True:
        score = run_game()

        # # 再プレイ or 終了 選択
        # waiting_for_choice = True
        # while waiting_for_choice:
        #     for event in pygame.event.get():
        #         if event.type == pygame.QUIT:
        #             pygame.quit()
        #             sys.exit()
        #         elif event.type == pygame.KEYDOWN:
        #             if event.key == pygame.K_r:  # 再プレイ
        #                 waiting_for_choice = False
        #             elif event.key == pygame.K_q:  # 終了
        #                 pygame.quit()
        #                 sys.exit()
