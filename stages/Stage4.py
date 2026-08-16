import pygame  # pip install pygame
import sys
import time
import random
import os

# PyInstaller で EXE 化された場合のファイルパス解決
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_asset_path(relative_path):
    return os.path.join(base_path, relative_path)

from modules import functions as f

pygame.init()
pygame.mixer.init()
pygame.mixer.music.stop()

# 画面サイズ設定
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))

# 色の定義
black = (0, 0, 0)
white = (255, 255, 255)
blue = (0, 0, 255)
ocean_bg = (100, 200, 255)

# --- 素材読み込み ---
hit_sound = pygame.mixer.Sound(get_asset_path("sounds/stage4/broken.mp3"))  # ボールがぶつかったときの音
miss_sound = pygame.mixer.Sound(get_asset_path("sounds/stage4/miss.mp3"))
pygame.mixer.music.load(get_asset_path("sounds/stage4/lovelyflower.mp3"))   # BGM
pygame.mixer.music.play(-1)

# フォントの設定
font = pygame.font.Font(None, 36)

# パドルの設定
paddle_width = 200
paddle_height = 10
paddle_acceleration = 2
max_speed = 15

# ボールの定義
ball_radius = 10
ball_speed_increment = 0.01

# ブロック設定
block_width = 40
block_height = 15

# ブロックの配置(0が空白)
block_pattern = [
    [0,0,0,0,0,0,0,1,0,0,0,0,0,0],
    [0,0,0,0,0,0,1,1,0,0,0,0,0,0],
    [0,0,0,0,1,1,1,1,1,0,0,0,0,0],
    [0,0,0,1,1,1,1,1,1,1,1,0,0,1],
    [0,0,1,1,1,1,1,1,1,1,1,1,0,1],
    [0,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,0,1],
    [0,0,0,1,1,1,1,1,1,1,1,0,0,1],
    [0,0,0,0,0,0,1,1,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,1,0,0,0,0,0,0],
]
# 目の位置
eye_positions = [(5, 3)]
# ブロックの開始位置
block_offset_x = (screen_width - (block_width + 10) * len(block_pattern[0])) // 2
block_offset_y = 35


# グラデーション
def get_block_color(row_index, max_rows):
    top_color = (0, 50, 160)
    bottom_color = (120, 180, 255)
    ratio = row_index / max_rows
    r = top_color[0] + (bottom_color[0] - top_color[0]) * ratio
    g = top_color[1] + (bottom_color[1] - top_color[1]) * ratio
    b = top_color[2] + (bottom_color[2] - top_color[2]) * ratio
    return (int(r), int(g), int(b))


def create_blocks():
    blocks = []
    for row_index, row in enumerate(block_pattern):
        block_row = []
        for col_index, block_on in enumerate(row):
            if block_on:
                block_x = col_index * (block_width + 10) + block_offset_x
                block_y = row_index * (block_height + 10) + block_offset_y
                block = pygame.Rect(block_x, block_y, block_width, block_height)
                block_row.append(block)
        blocks.append(block_row)
    return blocks


# カウントダウン関数
def countdown():
    target_score = 3000
    for i in range(3, 0, -1):
        screen.fill(black)
        clearscore_text = font.render(f"Clear if over 3000 points", True, white)
        countdown_text = font.render(f"Starting in {i}", True, white)  # カウントテキスト生成
        screen.blit(clearscore_text, (screen_width // 2 - clearscore_text.get_width() // 2, (screen_height // 2 - clearscore_text.get_height() // 2) - 30))  # 中央に表示
        screen.blit(countdown_text, (screen_width // 2 - countdown_text.get_width() // 2, screen_height // 2 - countdown_text.get_height() // 2))  # 中央に表示
        pygame.display.flip()  # 表示を更新
        time.sleep(1)  # 1秒待つ


def game_loop():
    pygame.display.set_caption("Block Breakerz Stage4")
    paddle_speed = 5
    left_passed_time = 0
    right_passed_time = 0

    clock = pygame.time.Clock()  # ポーズに使うclockを追加

    paddle = pygame.Rect(screen_width // 2 - paddle_width // 2, screen_height - 30, paddle_width, paddle_height)
    ball = pygame.Rect(screen_width // 2, screen_height // 2, ball_radius * 2, ball_radius * 2)
    ball_speed_x = 5
    ball_speed_y = 5
    score = 0

    # クリアに必要な目標スコア
    target_score = 3000
    # target_score = 1 #テスト用、使用しないならコメントアウト

    blocks = create_blocks()

    # 背景の泡初期値
    bubbles = [{'x': random.randint(0, screen_width),
                'y': random.randint(0, screen_height),
                'r': random.randint(2, 5)} for _ in range(30)]

    running = True
    # 終了判定
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # Pキーでポーズ
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                f.pause_game(screen, clock, font)

        # パドルの移動
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            left_passed_time += 1
            right_passed_time = 0
            paddle_speed = min(10 + paddle_acceleration * left_passed_time, max_speed)
            if paddle.left > 0:
                paddle.left -= paddle_speed
        elif keys[pygame.K_RIGHT]:
            right_passed_time += 1
            left_passed_time = 0
            paddle_speed = min(10 + paddle_acceleration * right_passed_time, max_speed)
            if paddle.right < screen_width:
                paddle.right += paddle_speed
        else:
            # キーが押されていないときは加速リセット
            left_passed_time = 0
            right_passed_time = 0
            paddle_speed = 5

        # ボールの移動
        ball.left += ball_speed_x
        ball.top += ball_speed_y

        # ボールと壁の衝突
        if ball.left <= 0 or ball.right >= screen_width:
            ball_speed_x = -ball_speed_x * (1 + ball_speed_increment)
            hit_sound.play()
        if ball.top <= 0:
            ball_speed_y = -ball_speed_y * (1 + ball_speed_increment)
            hit_sound.play()
        if ball.bottom >= screen_height:
            miss_sound.play()
            f.game_over(score, screen, font, screen_width, 4)
            running = False  # 下に落ちたら終了

        # ボールとパドルの衝突
        if ball.colliderect(paddle):
            hit_pos = (ball.left + ball.right) / 2 - (paddle.left + paddle.right) / 2
            ball_speed_x = hit_pos * 0.3
            ball_speed_y = -ball_speed_y
            hit_sound.play()
            ball_speed_x *= 1.05
            ball_speed_y *= 1.05
            ball_speed_x = max(-max_speed, min(max_speed, ball_speed_x))
            ball_speed_y = max(-max_speed, min(max_speed, ball_speed_y))

        # ボールとブロックの衝突
        block_hit = False
        for row in blocks:
            for block in row:
                if ball.colliderect(block):
                    ball_speed_y = -ball_speed_y * (1 + ball_speed_increment)
                    hit_sound.play()
                    row.remove(block)  # ブロックの削除
                    score += 100
                    block_hit = True
                    break
            if block_hit:
                break

        # 画面描画
        screen.fill(ocean_bg)  # 背景色

        # 泡描画
        for bubble in bubbles:
            bubble['y'] -= 1
            if bubble['y'] < 0:
                bubble['y'] = screen_height
                bubble['x'] = random.randint(0, screen_width)
                bubble['r'] = random.randint(2, 5)
            pygame.draw.circle(screen, (200, 255, 255), (bubble['x'], bubble['y']), bubble['r'])

        pygame.draw.rect(screen, blue, paddle)      # パドル描画
        pygame.draw.ellipse(screen, white, ball)    # ボール描画

        # ブロック描画
        for row_index, row in enumerate(blocks):
            for block in row:
                col_index = (block.left - block_offset_x) // (block_width + 10)
                if (row_index, col_index) in eye_positions:
                    pygame.draw.rect(screen, (70, 70, 70), block)  # 目の色
                else:
                    base_color = get_block_color(row_index, len(blocks))
                    pygame.draw.rect(screen, base_color, block)
                    # 魚の模様
                    dot_color = (
                        min(base_color[0] + 30, 255),
                        min(base_color[1] + 30, 255),
                        min(base_color[2] + 30, 255)
                    )
                    dot_radius = 4
                    for i in range(2):
                        for j in range(4):
                            dot_x = block.left + (j + 0.5) * block_width / 4
                            dot_y = block.top + (i + 0.5) * block_height / 2
                            pygame.draw.circle(screen, dot_color, (int(dot_x), int(dot_y)), dot_radius)
        # スコア表示
        score_text = font.render(f"Score: {score}", True, white)
        screen.blit(score_text, (10, 10))

        # ブロック全消しクリア判定
        if all(len(row) == 0 for row in blocks):
            running = False

        # 目標スコアを超えていればクリアとし次のステージに実行
        judge = f.is_cleared(score, target_score)
        if judge is True:
            f.game_clear(screen, font, screen_width, screen_height, 4)

        pygame.display.flip()
        time.sleep(0.03)  # フレーム制御

    return score, blocks


# ゲームの開始と再スタート処理
def run_game():
    # 正常に指定している音楽が流れなかったため追加
    pygame.mixer.music.stop()
    pygame.mixer.music.unload()
    pygame.mixer.music.load("sounds/stage4/lovelyflower.mp3")
    pygame.mixer.music.play(-1)

    while True:
        # カウント
        countdown()

        score, blocks = game_loop()  # ゲームの実行

        # 終了時の画面
        screen.fill(black)
        final_score_text = font.render(f"Final Score: {score}", True, white)
        message_text = None
        if all(len(row) == 0 for row in blocks):  # 全消しでクリア
            screen.fill(((102, 205, 170)))
            message_text = font.render("== Stage Clear! ==", True, white)

        restart_text = font.render("Press R to Restart or Enter to Exit", True, white)
        if message_text:
            screen.blit(message_text, (screen_width // 2 - message_text.get_width() // 2, screen_height // 2 - 20))
        screen.blit(final_score_text, (screen_width // 2 - final_score_text.get_width() // 2, screen_height // 2 - 60))
        screen.blit(restart_text, (screen_width // 2 - restart_text.get_width() // 2, screen_height // 2 + 20))
        pygame.display.flip()

        # リスタートor終了のループ
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:  # Rキーでリスタート
                        waiting = False  # リスタート
                    elif event.key == pygame.K_RETURN:  # Enterで終了
                        pygame.quit()
                        sys.exit()


if __name__ == "__main__":
    run_game()
