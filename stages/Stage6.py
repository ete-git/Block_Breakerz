""" ブロック崩しゲーム """

import pygame
import sys
import time
import random
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
# 次のステージのインポート
from stages import Stage7


def run_game():
    # 初期化
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.stop()

    screen_width = 800      # 画面の幅
    screen_height = 600     # 画面の高さ
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Block Breakerz Stage6")  # タイトルバーの表示

    clock = pygame.time.Clock()  # ポーズに使うclockを追加

    # 色の定義
    black = (0, 0, 0)
    white = (255, 255, 255)
    blue = (0, 0, 255)
    lightblue = (0, 150, 250)

    # --- 素材読み込み ---
    # 画像のリサイズ
    def img_resize(img_path, width, height):
        img = Image.open(img_path).resize((width, height))
        surface = pygame.image.fromstring(img.tobytes(), img.size, img.mode).convert()  # pygameが扱える方式に変換
        return surface
    background_img = img_resize(get_asset_path("images/stage6/FYs2A9.png"), 1200, 800)      # 背景画像
    item_split_img = pygame.image.load(get_asset_path("images/stage6/item_extend.png"))     # パドル抡大アイテム

    hit_sound = pygame.mixer.Sound(get_asset_path("sounds/stage6/paddle_sound_1.mp3"))      # ボールがぶつかったときの音
    item_sound = pygame.mixer.Sound(get_asset_path("sounds/stage6/broken2.mp3"))      # アイテムを取ったとき
    miss_sound = pygame.mixer.Sound(get_asset_path("sounds/stage6/miss.mp3"))
    pygame.mixer.music.load(get_asset_path("sounds/stage6/retroparty.mp3"))                 # BGM
    pygame.mixer.music.play(-1)

    # フォントの設定
    font = pygame.font.Font(None, 36)   # デフォルトのフォント, 文字サイズ

    # パドル
    paddle_width = 120
    paddle_height = 10
    paddle = pygame.Rect(screen_width // 2 - paddle_width // 2, screen_height - 30, paddle_width, paddle_height)

    # ボールの設定
    ball_radius = 10    # ボールの半径
    ball_speed_x = 8    # ボールのX方向のスピード
    ball_speed_y = 8    # ボールのY方向のスピード
    # ball_speed_increment = 0.001    # ボールが当たったときの速度増加
    ball = pygame.Rect(screen_width // 2 - ball_radius // 2, screen_height // 2 - ball_radius // 2, ball_radius * 2, ball_radius * 2)
    add_balls = []    # 追加のボールのリスト

    # ブロックの設定
    block_width = 60    # ブロックの幅
    block_height = 20   # ブロックの高さ
    block_rows = 5      # ブロックの行数
    block_cols = 11     # ブロックの列数
    blocks = []
    for row in range(block_rows):
        row_list = []
        for col in range(block_cols):
            x = col * (block_width + 10) + 20   # ブロック同士の間隔10, ブロックの初期位置20
            y = row * (block_height + 10) + 35  # ブロック同士の間隔10, ブロックの初期位置35
            rect = pygame.Rect(x, y, block_width, block_height)

            mark = None
            r = random.random()
            if r < 0.12:            # 12%で-のアイテムのブロック
                mark = "-"
            elif r < 0.08 + 0.20:   # 20%でoのアイテムのブロック
                mark = "o"
            row_list.append({"rect": rect, "mark": mark})   # ブロックを辞書に追加
        blocks.append(row_list)

    # ゲームが始まる前にカウントダウン
    count_time = 3  # カウントダウンの秒数
    for i in range(count_time, 0, -1):
        screen.fill(black)  # 画面を黒で塗りつぶす
        clearscore_text = font.render(f"Clear if over 4000 points", True, white)
        countdown_text = font.render(f"Starting in {i}", True, white)  # カウントテキスト生成
        screen.blit(clearscore_text, (screen_width // 2 - clearscore_text.get_width() // 2, (screen_height // 2 - clearscore_text.get_height() // 2) - 30))  # 中央に表示
        screen.blit(countdown_text, (screen_width // 2 - countdown_text.get_width() // 2, screen_height // 2 - countdown_text.get_height() // 2))  # 中央に表示
        pygame.display.flip()  # 表示を更新
        time.sleep(1)  # 1秒待つ

    # ゲームを動かす処理
    running = True
    score = 0

    # クリアに必要な目標スコア
    target_score = 4000
    # target_score = 1 #テスト用、使用しないならコメントアウト

    ball_launch = False  # ボールが発射フラグ
    paddle_speed = 8
    left_acceleration = 0
    right_acceleration = 0
    paddle_direction = None
    left_acceleration = 0
    right_acceleration = 0
    items = []

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:   # QUITはpygameブラウザの閉じるボタン
                pygame.quit()               # pygameを終了
                sys.exit()                  # システムを落とす
            # elif event.type == pygame.KEYDOWN and event.key == pygame.K_UP: # 上キーを押したとき
            # Pキーでポーズ
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                f.pause_game(screen, clock, font)
        ball_launch = True

        # パドルの操作
        keys = pygame.key.get_pressed()

        # どちらかの方向にしか進ませない処理
        if paddle_direction is None:
            if keys[pygame.K_LEFT]:
                paddle_direction = "left"
            elif keys[pygame.K_RIGHT]:
                paddle_direction = "right"

        elif paddle_direction == "left" and not keys[pygame.K_LEFT] and keys[pygame.K_RIGHT]:
            paddle_direction = "right"
        elif paddle_direction == "right" and not keys[pygame.K_RIGHT] and keys[pygame.K_LEFT]:
            paddle_direction = "left"

        # 左キー
        if keys[pygame.K_LEFT] and paddle_direction == "left":
            paddle_direction = None
            left_acceleration += 0.3    # 左キーを押し続けた時の加速度
            left_speed = paddle_speed + 5 * left_acceleration
            if paddle.left > 0:
                paddle.left -= left_speed
            else:
                paddle.left = 0                 # パドルの左側の座標を画面の左端に合わせる
            # paddle.left = max(paddle.left - speed, 0)

        # 右キー
        elif keys[pygame.K_RIGHT] and paddle_direction == "right":
            paddle_direction = None
            right_acceleration += 0.3   # 右キーを押し続けた時の加速度
            right_speed = paddle_speed + 5 * right_acceleration
            if paddle.right < screen_width:     # パドルが右端より小さい時は移動
                paddle.right += right_speed
            else:
                paddle.right = screen_width     # パドルの右側の座標を画面の右端に合わせる
            # paddle.right = min(paddle.right + speed, screen_width)

        else:   # キーが押されていない時
            left_acceleration = 0
            right_acceleration = 0

        # ボールをパドルの上に乗せる
        if not ball_launch:
            ball.centerx = paddle.centerx   # ボールとパドルのx座標を合わせる
            ball.bottom = paddle.top        # ボールをパドルの上に付ける

        # ボール発射時の速度
        else:
            ball.x += ball_speed_x
            ball.y += ball_speed_y

            # ボールと壁の衝突判定
            if ball.left <= 0 or ball.right >= screen_width:
                ball_speed_x = -ball_speed_x
                hit_sound.play()
            if ball.top <= 0:
                ball_speed_y = -ball_speed_y
                hit_sound.play()

            # ボールとパドルの衝突判定
            if ball.colliderect(paddle):
                hit_position = (ball.centerx - paddle.centerx) / (paddle.width / 2)   # ボールの中心座標とパドルの幅の差
                ball_speed_x = hit_position * 8     # ボールが跳ね返る方向調整
                ball_speed_y = -abs(ball_speed_y)   # ボールがパドルに当たったとき必ず上に返す
                hit_sound.play()

            # ボールとブロックの衝突判定
            for row in blocks:
                for block in row:
                    if ball.colliderect(block["rect"]):
                        ball_speed_y = -ball_speed_y
                        hit_sound.play()
                        mark = block["mark"]
                        # ブロックがoマークの時
                        if mark == "o":
                            ball_rect = pygame.Rect(block["rect"].centerx, block["rect"].bottom, ball_radius * 2, ball_radius * 2)          # 追加のボールの作成
                            add_ball_speed_x = random.choice([-6, 6])   # 追加のボールを左右どちらかに動かす
                            add_ball_speed_y = 6                        # 追加のボールを落とす
                            add_balls.append({"rect": ball_rect, "speed_x": add_ball_speed_x, "speed_y": add_ball_speed_y})
                        # ブロックが-マークの時
                        elif mark == "-":
                            item_rect = pygame.Rect(block["rect"].centerx - 10, block["rect"].bottom, ball_radius * 2, ball_radius * 2)     # パドルのアイテムの作成
                            items.append(item_rect)

                        row.remove(block)   # ブロックの削除
                        score += 100        # ブロックの得点
                        break

        # 追加ボール設定
        for b in add_balls[:]:
            # 追加ボールの最初の速度
            b["rect"].x += b["speed_x"]
            b["rect"].y += b["speed_y"]

            # 追加ボールと壁との衝突判定
            if b["rect"].left <= 0 or b["rect"].right >= screen_width:
                b["speed_x"] = -b["speed_x"]
                hit_sound.play()
            if b["rect"].top <= 0:
                b["speed_y"] = -b["speed_y"]
                hit_sound.play()

            # 追加ボールとパドルの衝突判定
            if b["rect"].colliderect(paddle):
                hit_position = (b["rect"].centerx - paddle.centerx) / (paddle.width / 2)
                b["speed_x"] = hit_position * 8
                b["speed_y"] = -abs(b["speed_y"])
                hit_sound.play()

            # ボールとブロックの衝突判定
            for row in blocks:
                for block in row:
                    if b["rect"].colliderect(block["rect"]):
                        b["speed_y"] = -b["speed_y"]
                        hit_sound.play()
                        mark = block["mark"]
                        # ブロックがoマークの時
                        if mark == "o":
                            ball_rect = pygame.Rect(block["rect"].centerx, block["rect"].bottom, ball_radius * 2, ball_radius * 2)          # 追加のボールの作成
                            add_ball_speed_x = random.choice([-6, 6])   # 追加のボールを左右どちらかに動かす
                            add_ball_speed_y = 6                        # 追加のボールを落とす
                            add_balls.append({"rect": ball_rect, "speed_x": add_ball_speed_x, "speed_y": add_ball_speed_y})
                        # ブロックが-マークの時
                        elif mark == "-":
                            item_rect = pygame.Rect(block["rect"].centerx - 10, block["rect"].bottom, ball_radius * 2, ball_radius * 2)     # パドルのアイテムの作成
                            items.append(item_rect)

                        row.remove(block)   # ブロックの削除
                        score += 100        # ブロックの得点
                        break

        # -アイテム設定
        for item in items[:]:
            item.y += 6     # -アイテムが落ちる速度
            if item.colliderect(paddle):
                item_sound.play()
                paddle.width += 20  # -アイテムを取ったときのパドル幅の変化の数値
                paddle.width = min(paddle.width, 300)   # パドル幅の制限300まで
                paddle = pygame.Rect(paddle.left, paddle.top, paddle.width, paddle.height)  # パドルの作成
                items.remove(item)  # アイテムの削除
            # アイテムが画面下に落ちた時
            elif item.top > screen_height:
                items.remove(item)  # アイテムの削除

        # ゲームオーバー
        add_ball_out = True  # 追加のボールが画面の下に出た場合
        for b in add_balls:
            if b["rect"].top <= screen_height:
                # miss_sound.play()
                add_ball_out = False
                break

        if ball.top > screen_height and add_ball_out:   # ボールが画面の下に出た場合
            miss_sound.play()
            f.game_over(score, screen, font, screen_width, 6)
            # running = False # ループ終了

        # 目標スコアを超えていればクリアとし次のステージに実行
        judge = f.is_cleared(score, target_score)
        if judge is True:
            f.game_clear(screen, font, screen_width, screen_height, 6)

        # 画面の描画
        bg_x = (screen_width - background_img.get_width()) // 2
        bg_y = (screen_height - background_img.get_height()) // 2
        screen.blit(background_img, (bg_x, bg_y))
        pygame.draw.rect(screen, blue, paddle)
        pygame.draw.ellipse(screen, white, ball)
        for b in add_balls:
            pygame.draw.ellipse(screen, white, b["rect"])   # 追加ボール

        # ブロックの表示
        for row in blocks:
            for block in row:
                pygame.draw.rect(screen, lightblue, block["rect"])
                # マーク付きブロックの表示
                if block["mark"]:
                    txt = font.render(block["mark"], True, white)   # アンチエイリアス, 文字の色
                    text_x = block["rect"].x + (block_width - txt.get_width()) // 2     # マークの幅を調整
                    text_y = block["rect"].y + (block_height - txt.get_height()) // 2   # マークの高さを調整
                    screen.blit(txt, (text_x, text_y))

        # アイテムの表示
        for item in items:
            screen.blit(item_split_img, item)
            # pygame.draw.rect(screen, white, item)
            # pygame.draw.line(screen, blue, (item.left + 4, item.centery), (item.right - 4, item.centery), 2)    # 線の色, -の線の長さ, 線の太さ

        # ゲーム中のスコアの表示
        score_text = font.render(f"Score: {score}", True, white)    # アンチエイリアス, 文字の色
        screen.blit(score_text, (10, 10))                           # テキストを反映 # 10, 10 テキストの位置
        pygame.display.flip()   # 設定を反映させる
        time.sleep(0.03)        # 0.03秒ごとにボールの位置を変える

    # ゲーム終了後のスコア表示
    screen.fill(black)      # ゲーム画面をスコア画面に上書き
    final_score_text = font.render(f"Final Score: {score}", True, white)    # アンチエイリアス, 文字の色
    exit_text = font.render("Press Enter to exit", True, white)
    screen.blit(final_score_text, (screen_width // 2 - final_score_text.get_width() // 2, screen_height // 2 - 30))     # -30で上のほうに文字を表示
    screen.blit(exit_text, (screen_width // 2 - exit_text.get_width() // 2, screen_height // 2 + 10))                   # +10で下のほうに文字を表示
    pygame.display.flip()

    # スコア画面の終了の処理
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # Enterキーを押したら終了
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                pygame.quit()
                sys.exit()
