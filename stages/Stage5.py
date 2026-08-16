import pygame
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
# 次のステージのインポート
from stages import Stage6

import warnings
warnings.filterwarnings("ignore")


def run_game():

    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.stop()

    SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Block Breakerz Stage5")

    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)

    clock = pygame.time.Clock()  # ポーズに使うclockを追加

    # --- 素材読み込み ---
    background_img = pygame.image.load(get_asset_path("images/stage5/background.png"))
    ball_img = pygame.image.load(get_asset_path("images/stage5/ball.png"))
    paddle_img = pygame.image.load(get_asset_path("images/stage5/paddle.png"))
    brick_green_img = pygame.image.load(get_asset_path("images/stage5/brick_green.png"))
    brick_blue_img = pygame.image.load(get_asset_path("images/stage5/brick_blue.png"))
    brick_red_img = pygame.image.load(get_asset_path("images/stage5/brick_red.png"))
    item_extend_img = pygame.image.load(get_asset_path("images/stage5/item_extend.png"))
    item_split_img = pygame.image.load(get_asset_path("images/stage5/item_split.png"))

    hit_sound = pygame.mixer.Sound(get_asset_path("sounds/stage5/hit.wav"))
    pickup_sound = pygame.mixer.Sound(get_asset_path("sounds/stage5/pickup.wav"))
    miss_sound = pygame.mixer.Sound(get_asset_path("sounds/stage5/miss.mp3"))
    pygame.mixer.music.load(get_asset_path("sounds/stage5/BGM.mp3"))
    pygame.mixer.music.play(-1)

    # ボールのサイズを1.2倍の大きさにする★
    width, height = ball_img.get_size()
    resize = (int(width * 1.2), int(height * 1.2))
    ball_img = pygame.transform.scale(ball_img, resize)

    font = pygame.font.Font(None, 36)

    PADDLE_Y = SCREEN_HEIGHT - 50
    paddle_width = paddle_img.get_width()
    paddle_height = paddle_img.get_height()

    ball_radius = ball_img.get_width() // 2
    BALL_SPEED_X = 5
    BALL_SPEED_Y = -5

    BRICK_ROWS = 5
    BRICK_COLS = 13  # 10列に増やして両端に空白を作る
    BRICK_WIDTH = brick_green_img.get_width()
    BRICK_HEIGHT = brick_green_img.get_height()

    score = 0

    # クリアに必要な目標スコア
    target_score = 4000
    # target_score = 1 #テスト用、使用しないならコメントアウト

    BRICK_COLS = 13  # 13列

    # --- ブロック生成（左に1列空き、右に1列空き、中間と右側に計13列ブロック）---
    bricks = []
    for row in range(BRICK_ROWS):
        row_bricks = []
        for col in range(1, BRICK_COLS - 1):  # 1～13列（左端と右端を空ける）
            x = col * BRICK_WIDTH
            y = row * BRICK_HEIGHT + 50
            if row < 2:
                hp = 3
            elif row < 4:
                hp = 2
            else:
                hp = 1
            rect = pygame.Rect(x, y, BRICK_WIDTH, BRICK_HEIGHT)
            row_bricks.append({"rect": rect, "hp": hp})
        bricks.append(row_bricks)

    paddle_x = SCREEN_WIDTH // 2

    balls = [{
        "x": paddle_x,
        "y": PADDLE_Y - ball_radius,
        "speed_x": 0,
        "speed_y": 0,
        "active": False
    }]

    powerups = []  # 落ちている道具リスト
    POWERUP_SPEED = 3  # 道具落下速度
    POWERUP_TYPES = ["extend", "split"]

    running = True
    game_started = False
    game_over = False
    game_clear = False

    clock = pygame.time.Clock()

    def reset_game():
        nonlocal paddle_width, paddle_x, balls, bricks, score, powerups, game_started, game_over, game_clear
        paddle_width = paddle_img.get_width()
        paddle_x = SCREEN_WIDTH // 2
        balls = [{
            "x": paddle_x,
            "y": PADDLE_Y - ball_radius,
            "speed_x": 0,
            "speed_y": 0,
            "active": False
        }]
        powerups = []
        score = 0

        game_started = False
        game_over = False
        game_clear = False

        # ブロック再生成
        bricks.clear()
        for row in range(BRICK_ROWS):
            row_bricks = []
            for col in range(1, BRICK_COLS -1):
                x = col * BRICK_WIDTH
                y = row * BRICK_HEIGHT + 50
                if row < 2:
                    hp = 3
                elif row < 4:
                    hp = 2
                else:
                    hp = 1
                rect = pygame.Rect(x, y, BRICK_WIDTH, BRICK_HEIGHT)
                row_bricks.append({"rect": rect, "hp": hp})
            bricks.append(row_bricks)

    reset_game()

    # カウントダウン表示
    for i in range(3, 0, -1):
        screen.fill(BLACK)  # 画面を黒で塗りつぶす
        clearscore_text = font.render(f"Clear if over 4000 points", True, WHITE)
        countdown_text = font.render(f"Starting in {i}", True, WHITE)  # カウントテキスト生成
        screen.blit(clearscore_text, (SCREEN_WIDTH // 2 - clearscore_text.get_width() // 2, (SCREEN_HEIGHT // 2 - clearscore_text.get_height() // 2) - 30))  # 中央に表示
        screen.blit(countdown_text, (SCREEN_WIDTH // 2 - countdown_text.get_width() // 2, SCREEN_HEIGHT // 2 - countdown_text.get_height() // 2))  # 中央に表示
        pygame.display.flip()  # 表示を更新
        time.sleep(1)

    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Pキーでポーズ
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                f.pause_game(screen, clock, font)

            # Rキーでゲーム再スタート
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and (game_over or game_clear):
                    reset_game()

        keys = pygame.key.get_pressed()
        if not game_over and not game_clear:
            # パドル移動
            if keys[pygame.K_LEFT]:
                paddle_x -= 10
                if paddle_x - paddle_width // 2 < 0:
                    paddle_x = paddle_width // 2
            if keys[pygame.K_RIGHT]:
                paddle_x += 10
                if paddle_x + paddle_width // 2 > SCREEN_WIDTH:
                    paddle_x = SCREEN_WIDTH - paddle_width // 2

            # ボール未発射時はパドルに追従
            for ball in balls:
                if not ball["active"]:
                    ball["x"] = paddle_x
                    ball["y"] = PADDLE_Y - ball_radius

            # # スペースキーでボール発射
            # if keys[pygame.K_SPACE]:
            for ball in balls:
                if not ball["active"]:
                    ball["speed_x"] = BALL_SPEED_X
                    ball["speed_y"] = BALL_SPEED_Y
                    ball["active"] = True
            game_started = True

            # ボール移動と判定
            for ball in balls[:]:
                if ball["active"]:
                    ball["x"] += ball["speed_x"]
                    ball["y"] += ball["speed_y"]

                    # 壁判定
                    if ball["x"] - ball_radius <= 0 or ball["x"] + ball_radius >= SCREEN_WIDTH:
                        ball["speed_x"] = -ball["speed_x"]
                        hit_sound.play()
                    if ball["y"] - ball_radius <= 0:
                        ball["speed_y"] = -ball["speed_y"]
                        hit_sound.play()
                    if ball["y"] - ball_radius > SCREEN_HEIGHT:
                        miss_sound.play()
                        balls.remove(ball)  # ボール消滅

                    # パドル判定
                    paddle_rect = pygame.Rect(paddle_x - paddle_width // 2, PADDLE_Y, paddle_width, paddle_height)
                    ball_rect = pygame.Rect(int(ball["x"]) - ball_radius, int(ball["y"]) - ball_radius, ball_radius * 2, ball_radius * 2)

                    if ball_rect.colliderect(paddle_rect) and ball["speed_y"] > 0:
                        hit_sound.play()
                        offset = (ball["x"] - paddle_x) / (paddle_width / 2)
                        ball["speed_x"] = BALL_SPEED_X * offset
                        ball["speed_y"] = -abs(ball["speed_y"])

                    # ブロック判定
                    broken_brick = None
                    for row in bricks:
                        for brick in row:
                            if brick["rect"].colliderect(ball_rect):
                                hit_sound.play()
                                ball["speed_y"] = -ball["speed_y"]
                                brick["hp"] -= 1
                                if brick["hp"] <= 0:
                                    row.remove(brick)
                                    score += 100
                                    broken_brick = brick
                                break
                        if broken_brick:
                            break

                    # 道具生成判定
                    if broken_brick:
                        if random.random() < 0.55:
                            kind = random.choice(POWERUP_TYPES)
                            powerup_rect = pygame.Rect(broken_brick["rect"].x + BRICK_WIDTH // 2 - 15, broken_brick["rect"].y, 30, 30)
                            powerups.append({"rect": powerup_rect, "type": kind})

            # 道具移動と取得判定
            for powerup in powerups[:]:
                powerup["rect"].y += POWERUP_SPEED
                paddle_rect = pygame.Rect(paddle_x - paddle_width // 2, PADDLE_Y, paddle_width, paddle_height)
                if powerup["rect"].colliderect(paddle_rect):
                    pickup_sound.play()
                    if powerup["type"] == "extend":
                        paddle_width = min(paddle_width + 40, 300)
                    elif powerup["type"] == "split":
                        if len(balls) < 20:
                            new_balls = []
                            for ball in balls:
                                new_balls.append(ball)
                                new_balls.append({
                                    "x": ball["x"],
                                    "y": ball["y"],
                                    "speed_x": -ball["speed_x"],
                                    "speed_y": ball["speed_y"],
                                    "active": True
                                })
                            balls = new_balls
                    powerups.remove(powerup)
                elif powerup["rect"].top > SCREEN_HEIGHT:
                    powerups.remove(powerup)

            # ゲームクリア判定
            total_bricks_left = sum(len(row) for row in bricks)
            # 目標スコアを超えていればクリア
            if total_bricks_left == 0 or score >= target_score:
                game_clear = True

            # ゲームオーバー判定
            if len(balls) == 0:
                game_over = True

        # --- 描画 ---
        bg_x = (SCREEN_WIDTH - background_img.get_width()) // 2
        bg_y = (SCREEN_HEIGHT - background_img.get_height()) // 2
        screen.blit(background_img, (bg_x, bg_y))

        paddle_draw_x = paddle_x - paddle_width // 2
        paddle_draw_img = pygame.transform.scale(paddle_img, (paddle_width, paddle_height))
        screen.blit(paddle_draw_img, (paddle_draw_x, PADDLE_Y))

        for ball in balls:
            screen.blit(ball_img, (int(ball["x"]) - ball_radius, int(ball["y"]) - ball_radius))

        for row in bricks:
            for brick in row:
                if brick["hp"] == 3:
                    screen.blit(brick_red_img, brick["rect"])
                elif brick["hp"] == 2:
                    screen.blit(brick_blue_img, brick["rect"])
                else:
                    screen.blit(brick_green_img, brick["rect"])

        for powerup in powerups:
            if powerup["type"] == "extend":
                screen.blit(item_extend_img, powerup["rect"])
            else:
                screen.blit(item_split_img, powerup["rect"])

        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        if game_over:
            pygame.mixer.music.stop()
            f.game_over(score, screen, font, SCREEN_WIDTH, 5)
            # screen.fill((0, 0, 0))
            # over_text = font.render("Game Over! Press R to Restart", True, WHITE)
            # score_text = font.render(f"Final Score: {score}", True, WHITE)
            # screen.blit(over_text, (SCREEN_WIDTH // 2 - over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            # screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2 + 10))

        if game_clear:
            pygame.mixer.music.stop()
            f.game_clear(screen, font, SCREEN_WIDTH, SCREEN_HEIGHT, 5)
            # screen.fill((0, 0, 0))
            # clear_text = font.render("Stage5 Clear!", True, WHITE)
            # next_text = font.render("Next: Stage6", True, WHITE)
            # # score_text = font.render(f"Final Score: {score}", True, WHITE)
            # screen.blit(next_text, (SCREEN_WIDTH // 2 - next_text.get_width() // 2,(SCREEN_HEIGHT // 2 - next_text.get_height() // 2) + 30))
            # screen.blit(clear_text, (SCREEN_WIDTH // 2 - clear_text.get_width() // 2,SCREEN_HEIGHT // 2 - clear_text.get_height() // 2))
            # # screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2 + 10))

        pygame.display.flip()

    pygame.quit()
    return
