"""
プログラム構造
Main.pyからStage1のメイン関数を実行し、クリアするとStage1.pyからStage2.pyのメイン関数を呼び出す。
Stage2もクリアしたら同じようにStage3.pyを実行し、これをStage7まで繰り返す。

テストで即クリアさせたい場合は各ステージファイルの "target_score = 1" の部分のコメントアウトを解除してください
target_scoreと検索すれば見つけやすいです
"""
#pip install pygame
#pip install pillow
#↑実行前にこれをインストール

import pygame
import sys
from modules import functions as f

# ステージのインポート
from stages import Stage1
from stages import Stage2
from stages import Stage3
from stages import Stage4
from stages import Stage5
from stages import Stage6
from stages import Stage7


# スタート画面
def main():
    # 初期化
    pygame.init()
    # 音声の初期化
    pygame.mixer.init()
    pygame.mixer.music.stop()

    # 画面幅
    screen_width = 800
    screen_height = 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    # ディスプレイ名
    pygame.display.set_caption("Block Breakerz")
    # フォント
    title_font = pygame.font.Font(None, 80)
    font = pygame.font.Font(None, 36)

    # 待機状態
    waiting = True

    # 待機状態がTrueの間はスタート画面で待機
    while waiting:
        screen.fill((0, 0, 0))
        title_text = title_font.render("Block Breakerz", True, (255, 255, 255))
        start_text = font.render("Press SPACE to start", True, (255, 255, 255))
        end_text = font.render("Press Q to quit", True, (255, 255, 255))
        credit_text = font.render("Press C for credits", True, (255, 255, 255))  # 追加
        controls_text = font.render("Left / Right Arrow Keys – Move paddle", True, (255, 255, 255))
        pause_text = font.render("Press P to pause the game", True, (255, 255, 255))  # ポーズ説明追加

        screen.blit(title_text, (screen_width//2 - title_text.get_width()//2, screen_height//3.5))
        screen.blit(start_text, (screen_width//2 - start_text.get_width()//2, screen_height//1.5))
        screen.blit(end_text, (screen_width//2 - end_text.get_width()//2, screen_height//1.35))
        screen.blit(credit_text, (screen_width//2 - credit_text.get_width()//2, screen_height//1.25))  # 追加
        screen.blit(controls_text, (screen_width//2 - controls_text.get_width()//2, screen_height//1.1))
        screen.blit(pause_text, (screen_width//2 - pause_text.get_width()//2, screen_height//1.05))  # 表示位置

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # 閉じるボタンが押されたら終了
                pygame.quit()
                sys.exit()
            # スペースキーが押されるとstage1から開始
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False  # 待機状態を解除
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
                # 追加 クレジット表示関数
                elif event.key == pygame.K_c:
                    f.show_credits(screen, screen_width, screen_height, font)

    # whileループを抜けたらstage.pyにあるrun_gameを呼びだす
    Stage1.run_game()  # テストしたいステージの番号(例:Stage3)に変えると、そのステージから実行されます。
    pygame.quit()


if __name__ == "__main__":
    main()
