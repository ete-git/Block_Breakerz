# ブロック崩しゲーム

# 必要なライブラリのインポート
import pygame
import sys     # システム関連用
import time    # 時間操作用のtime
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
from stages import Stage4


def run_game():
    pygame.init()  # Pygameの初期化

    # 効果音の初期化
    pygame.mixer.init()
    pygame.mixer.music.stop()

    # 画面サイズの設定(width=幅、height=高さ)
    screen_width = 800
    screen_height = 600

    # 画面の作成
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Block Breakerz Stage3")  # タイトルを設定

    clock = pygame.time.Clock()  # ポーズに使うclockを追加

    # 色の定義
    black = (0, 0, 50)
    white = (255, 255, 255)
    blue = (0, 0, 255)
    yellow = (255, 215, 0)
    yellow_ALT = (218, 165, 32)

    # --- 素材読み込み ---
    # 画像のリサイズ
    def img_resize(img_path, width, height):
        img = Image.open(img_path).resize((width, height))
        surface = pygame.image.fromstring(img.tobytes(), img.size, img.mode).convert()  # pygameが扱える方式に変換
        return surface
    background_img = img_resize(get_asset_path("images/stage3/haikei1.png"), screen_width, screen_height)   # 背景画像

    break_sound = pygame.mixer.Sound(get_asset_path("sounds/stage3/break.mp3"))
    paddle_sound = pygame.mixer.Sound(get_asset_path("sounds/stage3/paddle.mp3"))
    miss_sound = pygame.mixer.Sound(get_asset_path("sounds/stage3/miss.mp3"))
    pygame.mixer.music.load(get_asset_path("sounds/stage3/hosi1.mp3"))  # BGM
    pygame.mixer.music.play(-1)

    # フォントサイズの設定
    font = pygame.font.Font(None, 36)

    # パドル関連の設定
    # パドルの幅、高さ、速さ
    paddle_width = 100
    paddle_height = 10
    paddle_speed = 15
    # paddle_acceleration = 5  # 長押しで加速する値
    # left_passed_time = 0     # 左キーが押された経過時間
    # right_passed_time = 0    # 右キーが押された経過時間
    paddle = pygame.Rect(screen_width // 2 - paddle_width // 2, screen_height - 30, paddle_width, paddle_height)  # パドルの初期位置とサイズ

    # ボール関連の設定
    ball_radius = 10
    ball_speed_x = 7  # 横方向の速度
    ball_speed_y = 7  # 縦方向の速度
    ball_speed_increment = 0.05  # 衝突時の加速率
    ball = pygame.Rect(screen_width // 2, screen_height // 2, ball_radius * 2, ball_radius * 2)  # ボールの初期位置とサイズ

    # ブロック関連の設定
    block_width = 60
    block_height = 20
    block_rows = 5
    block_cols = 11
    blocks = []  # ブロックのリスト

    # ブロックの配置マップ(0=空白, 1=ブロック, 2=壊すと加速するブロック)
    block_map = [
        [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
        [0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0],
        [1, 2, 1, 0, 1, 2, 1, 0, 1, 2, 1],
        [0, 1, 0, 0, 1, 1, 1, 0, 0, 1, 0],
        [0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0]
    ]

    # ブロックの配置
    blocks = []
    for row_index, row in enumerate(block_map):
        block_row = []
        for col_index, block_type in enumerate(row):
            if block_type != 0:
                block_x = col_index * (block_width + 10) + 20
                block_y = row_index * (block_height + 10) + 35
                block = pygame.Rect(block_x, block_y, block_width, block_height)
                # ブロックとその種類を保存
                block_row.append((block, block_type))
        blocks.append(block_row)

    # カウントダウン表示
    for i in range(3, 0, -1):
        screen.fill(black)  # 画面を黒で塗りつぶす
        clearscore_text = font.render(f"Clear if over 2000 points", True, white)
        countdown_text = font.render(f"Starting in {i}", True, white)  # カウントテキスト生成
        screen.blit(clearscore_text, (screen_width // 2 - clearscore_text.get_width() // 2, (screen_height // 2 - clearscore_text.get_height() // 2) - 30))  # 中央に表示
        screen.blit(countdown_text, (screen_width // 2 - countdown_text.get_width() // 2, screen_height // 2 - countdown_text.get_height() // 2))  # 中央に表示
        pygame.display.flip()  # 表示を更新
        time.sleep(1)  # 1秒待つ

    runnning = True
    # スコア
    score = 0

    # クリアに必要な目標スコア
    target_score = 2000
    # target_score = 1 #テスト用、使用しないならコメントアウト

    # ゲーム開始時の処理
    while runnning:
        # イベントを取得させる
        for event in pygame.event.get():
            # 閉じるボタンがクリックされたら終了させる
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # Pキーでポーズ
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                f.pause_game(screen, clock, font)

        # パドルの操作(滑らかに動かすよう改良)
        keys = pygame.key.get_pressed()
        # 左右のキーが押されてる間一定の速度で移動する
        if keys[pygame.K_LEFT] and paddle.left > 0:
            paddle.left -= paddle_speed
        if keys[pygame.K_RIGHT] and paddle.right < screen_width:
            paddle.right += paddle_speed

        # ボールの移動
        ball.left += ball_speed_x
        ball.top += ball_speed_y

        # ボールと壁の衝突判定(変な挙動を防ぐためシンプルに)
        if ball.left <= 0 or ball.right >= screen_width:
            # ball_speed_y *= (1 + ball_speed_increment) ←変な挙動を起こす？
            ball_speed_x = -ball_speed_x
        if ball.top <= 0:
            # ball_speed_y *= (1 + ball_speed_increment)
            ball_speed_y = -ball_speed_y
        # ボールが下に落ちたらゲームオーバー
        if ball.bottom >= screen_height:
            miss_sound.play()
            f.game_over(score, screen, font, screen_width, 3)
            runnning = False

        # ボールとパドルとの衝突判定
        if ball.colliderect(paddle):
            # ボールが触れたら効果音を鳴らす
            paddle_sound.play()
            # 上方向に反射するようにする
            ball_speed_y = -abs(ball_speed_y)

            # パドルの中心より左なら左に、右なら右に反射
            if ball.centerx < paddle.centerx:
                ball_speed_x = -abs(ball_speed_x)
            else:
                ball_speed_x = abs(ball_speed_x)

        # ブロックとの衝突判定
        for row in blocks:
            for block_tuple in row:
                block, block_type = block_tuple  # タプルの分解
                if ball.colliderect(block):
                    # ボールが触れたら効果音を鳴らす
                    break_sound.play()
                    ball_speed_y = -ball_speed_y
                    row.remove(block_tuple)
                    score += 100
                    # ブロックのタイプが2なら加速&スコア増加
                    if block_type == 2:
                        score += 400
                        ball_speed_x *= 1.2
                        ball_speed_y *= 1.2
                    break  # 一度の衝突で終了

        # 目標スコアを超えていればクリアとし次のステージに実行
        judge = f.is_cleared(score, target_score)
        if judge is True:
            f.game_clear(screen, font, screen_width, screen_height, 3)

        # 画面の描画
        bg_x = (screen_width - background_img.get_width()) // 2
        bg_y = (screen_height - background_img.get_height()) // 2
        screen.blit(background_img, (bg_x, bg_y))
        # screen.fill(black)
        pygame.draw.rect(screen, blue, paddle)
        pygame.draw.ellipse(screen, white, ball)
        for row in blocks:
            for block, block_type in row:
                # typeが2なら別の黄色に置き換える
                color = yellow if block_type == 1 else yellow_ALT
                pygame.draw.rect(screen, color, block)

        # スコア表示
        score_text = font.render(f"Score: {score}", True, white)
        screen.blit(score_text, (10, 10))

        time.sleep(0.03)
        pygame.display.flip()

    # ゲーム終了後のスコア表示
    screen.fill(black)
    final_score_text = font.render(f"Final Score: {score}", True, white)
    exit_text = font.render("Press Enter to exit", True, white)
    screen.blit(final_score_text, (screen_width // 2 - final_score_text.get_width() // 2, screen_height // 2 - final_score_text.get_height() // 2 - 20))
    screen.blit(exit_text, (screen_width // 2 - exit_text.get_width() // 2, screen_height // 2 - exit_text.get_height() // 2 + 20))
    pygame.display.flip()

    waiting_for_exit = True
    while waiting_for_exit:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                pygame.quit()
                sys.exit()

    return score
