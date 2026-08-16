import pygame  # Pygameライブラリをインポート
import sys     # システム関連の処理を扱うsysモジュールをインポート
import time    # 時間操作用のtimeモジュールをインポート
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
from stages import Stage3


def run_game():
    pygame.init()  # Pygameの初期化
    pygame.mixer.init()
    pygame.mixer.music.stop()

    screen_width = 1000  # 画面の幅を設定
    screen_height = 600  # 画面の高さを設定
    screen = pygame.display.set_mode((screen_width, screen_height))  # 指定サイズの画面を作成
    pygame.display.set_caption("Block Breakerz Stage2")  # タイトルを設定

    clock = pygame.time.Clock()  # ポーズに使うclockを追加

    # 使用する色を定義
    black = (0, 0, 0)
    white = (255, 255, 255)
    blue = (0, 0, 255)
    green = (0, 255, 0)

    # 画像のリサイズ
    def img_resize(img_path, width, height):
        img = Image.open(img_path).resize((width, height))
        surface = pygame.image.fromstring(img.tobytes(), img.size, img.mode).convert()      # pygameが扱える方式に変換
        return surface
    background_img = img_resize(get_asset_path("images/stage2/hs0Iaw2.png"), screen_width, screen_height)   # 背景画像

    hit_sound = pygame.mixer.Sound(get_asset_path("sounds/stage2/broken2.mp3"))  # ボールがぶつかったときの音
    miss_sound = pygame.mixer.Sound(get_asset_path("sounds/stage2/miss.mp3"))
    pygame.mixer.music.load(get_asset_path("sounds/stage2/sanjinooyatsu.mp3"))  # BGM
    pygame.mixer.music.play(-1)

    font = pygame.font.Font(None, 36)  # デフォルトフォントでサイズ36のフォントを作成

    # パドル（プレイヤーの操作するバー）の設定
    paddle_width = 100
    paddle_height = 10
    paddle_speed = 10
    paddle_acceleration = 5  # 長押しで加速する値
    left_passed_time = 0     # 左キーが押された経過時間
    right_passed_time = 0    # 右キーが押された経過時間
    paddle = pygame.Rect(screen_width // 2 - paddle_width // 2, screen_height - 30, paddle_width, paddle_height)  # パドルの初期位置とサイズ

    # ボールの設定
    ball_radius = 10
    ball_speed_x = 5  # 横方向の速度
    ball_speed_y = 5  # 縦方向の速度
    ball_speed_increment = 0.05  # 衝突時の加速率
    ball = pygame.Rect(screen_width // 2, screen_height // 2, ball_radius * 2, ball_radius * 2)  # ボールの初期位置とサイズ

    # ブロックの設定
    block_width = 55
    block_height = 20
    block_rows = 5
    block_cols = 11
    blocks = []  # ブロックのリスト

    # ブロックを配置するループ
    # for row in range(block_rows):
    #    block_row = []
    #    for col in range(block_cols):
    #        block_x = col * (block_width + 10) + 20  # 横位置の計算（間隔10px + 余白20px）
    #        block_y = row * (block_height + 10) + 35  # 縦位置の計算（間隔10px + 余白35px）
    #        block = pygame.Rect(block_x, block_y, block_width, block_height)
    #        block_row.append(block)
    #    blocks.append(block_row)

    # S, I, W のブロック配置
    blocks = []

    # S の形
    s_shape = [
        (1, 0), (2, 0), (3, 0),
        (1, 1),
        (1, 2), (2, 2), (3, 2),
        (3, 3),
        (1, 4), (2, 4), (3, 4),
    ]

    # I の形
    i_shape = [
        (6, 0), (6, 1), (6, 2), (6, 3), (6, 4)
    ]

    # W の形
    w_shape = [
        (9, 0), (9, 1), (9, 2), (9, 3), (9, 4),
        (10, 4),
        (11, 3),
        (12, 4),
        (13, 0), (13, 1), (13, 2), (13, 3), (13, 4),
    ]

    # すべて結合
    all_shapes = s_shape + i_shape + w_shape

    # 各ブロック配置
    for col, row in all_shapes:
        block_x = col * (block_width + 10) + 20
        block_y = row * (block_height + 10) + 35
        rect = pygame.Rect(block_x, block_y, block_width, block_height)
        blocks.append([rect])  # リストの中にリストを入れる（元の処理と合わせるため）

    # ゲーム開始前のカウントダウン表示
    for i in range(3, 0, -1):
        screen.fill(black)  # 画面を黒で塗りつぶす
        clearscore_text = font.render(f"Clear if over 1500 points", True, white)
        countdown_text = font.render(f"Starting in {i}", True, white)  # カウントテキスト生成
        screen.blit(clearscore_text, (screen_width // 2 - clearscore_text.get_width() // 2, (screen_height // 2 - clearscore_text.get_height() // 2) - 30))  # 中央に表示
        screen.blit(countdown_text, (screen_width // 2 - countdown_text.get_width() // 2, screen_height // 2 - countdown_text.get_height() // 2))  # 中央に表示
        pygame.display.flip()  # 表示を更新
        time.sleep(1)  # 1秒待つ

    runnning = True  # ゲームループの状態
    score = 0  # スコアの初期化

    # クリアに必要な目標スコア
    target_score = 1500
    # target_score = 1 #テスト用、使用しないならコメントアウト

    # メインゲームループ
    while runnning:
        for event in pygame.event.get():  # イベントの取得
            if event.type == pygame.QUIT:  # 閉じるボタンが押されたら終了
                pygame.quit()
                sys.exit()
            # Pキーでポーズ
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                f.pause_game(screen, clock, font)

        # キー入力の判定（パドルの操作）
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            left_passed_time += 1
            right_passed_time = 0
            paddle_speed = 10 + paddle_acceleration * left_passed_time  # 長押しによる加速
            if paddle.left > 0:  # 左端に到達しないように制限
                paddle.left -= paddle_speed
        elif keys[pygame.K_RIGHT]:
            right_passed_time += 1
            left_passed_time = 0
            paddle_speed = 10 + paddle_acceleration * right_passed_time
            if paddle.right < screen_width:  # 右端に到達しないように制限
                paddle.right += paddle_speed
        else:
            left_passed_time = 0
            right_passed_time = 0
            paddle_speed = 10

        # ボールの移動処理
        ball.left += ball_speed_x
        ball.top += ball_speed_y

        # ボールと壁の衝突判定(変な挙動を防ぐためシンプルに)
        if ball.left <= 0 or ball.right >= screen_width:
            # ball_speed_y *= (1 + ball_speed_increment) ←変な挙動を起こす？
            ball_speed_x = -ball_speed_x
            hit_sound.play()
        if ball.top <= 0:
            # ball_speed_y *= (1 + ball_speed_increment)
            ball_speed_y = -ball_speed_y
            hit_sound.play()
        if ball.bottom >= screen_height:
            miss_sound.play()
            f.game_over(score, screen, font, screen_width, 2)
            runnning = False  # 画面下に落ちたらゲーム終了

        # パドルとの衝突判定
        if ball.colliderect(paddle):
            hit_position = (ball.left + ball.right) / 2 - (paddle.left + paddle.right) / 2  # パドルの中心との相対位置
            ball_speed_x = hit_position * 0.3  # 打ち返す角度を調整
            ball_speed_y *= (1 + ball_speed_increment)
            ball_speed_y = -ball_speed_y
            hit_sound.play()

        # ブロックとの衝突判定
        for row in blocks:
            for block in row:
                if ball.colliderect(block):
                    ball_speed_y *= (1 + ball_speed_increment)
                    ball_speed_y = -ball_speed_y
                    hit_sound.play()
                    row.remove(block)  # ブロックを消す
                    score += 100  # スコア加算
                    break  # 一度の衝突で処理終了

        # 目標スコアを超えていればクリアとし次のステージに実行
        judge = f.is_cleared(score, target_score)
        if judge is True:
            f.game_clear(screen, font, screen_width, screen_height, 2)

        # 画面の描画
        bg_x = (screen_width - background_img.get_width()) // 2
        bg_y = (screen_height - background_img.get_height()) // 2
        screen.blit(background_img, (bg_x, bg_y))
        # screen.fill(black)
        pygame.draw.rect(screen, blue, paddle)  # パドル描画
        pygame.draw.ellipse(screen, white, ball)  # ボール描画
        for row in blocks:
            for block in row:
                pygame.draw.rect(screen, green, block)  # ブロック描画

        # スコア表示
        score_text = font.render(f"Score: {score}", True, white)
        screen.blit(score_text, (10, 10))

        time.sleep(0.03)  # 少し待って滑らかに描画
        pygame.display.flip()  # 画面更新

    # ゲーム終了後のスコア表示画面
    screen.fill(black)
    final_score_text = font.render(f"Final Score: {score}", True, white)
    exit_text = font.render("Press Enter to exit", True, white)
    screen.blit(final_score_text, (screen_width // 2 - final_score_text.get_width() // 2, screen_height // 2 - final_score_text.get_height() // 2 - 20))
    screen.blit(exit_text, (screen_width // 2 - exit_text.get_width() // 2, screen_height // 2 - exit_text.get_height() // 2 + 20))
    pygame.display.flip()

    # ゲーム終了待ちループ
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
