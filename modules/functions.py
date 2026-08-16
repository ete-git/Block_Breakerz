# 関数用


# インポート
import pygame
import sys
import Main
import time
from stages import Stage1
from stages import Stage2
from stages import Stage3
from stages import Stage4
from stages import Stage5
from stages import Stage6
from stages import Stage7


# ゲームをクリアしているかチェック
def is_cleared(score, target_score):  # スコア、目標スコア
    # もしスコアが目標スコアを超えていたらTrueを返す
    if score >= target_score:
        return True
    else:
        False


# ゲームクリア関数
def game_clear(screen, font, screen_width, screen_height, stage_num):  # 画面サイズ、フォント、縦サイズ、横サイズ、ステージ番号

    # ステージのリスト
    stages = [Stage1, Stage2, Stage3, Stage4, Stage5, Stage6, Stage7]

    screen.fill((0, 0, 0))
    congrats_text = font.render(f"Stage{stage_num} Clear!!", True, (255, 255, 255))
    if stage_num != 7:
        next_text = font.render(f"Next: Stage{stage_num + 1}", True, (255, 255, 255))
    else:
        next_text = font.render("Congratulation!!", True, (255, 255, 255))
    screen.blit(next_text, (screen_width // 2 - next_text.get_width() // 2, (screen_height // 2 - next_text.get_height() // 2) + 40))
    screen.blit(congrats_text, (screen_width // 2 - congrats_text.get_width() // 2, screen_height // 2 - congrats_text.get_height() // 2))

    pygame.display.flip()
    time.sleep(3)
    # 最終ステージでないなら次のステージを実行
    if stage_num != 7:
        stages[stage_num].run_game()
    else:
        # 最終ステージの場合はそのまま終了
        time.sleep(3)
        pygame.quit()
        sys.exit()


# ゲームオーバー関数
# stege_numには各ステージの番号を入力
def game_over(score, screen, font, screen_width, stage_num):

    # ステージのリスト
    stages = [Stage1, Stage2, Stage3, Stage4, Stage5, Stage6, Stage7]

    waiting = True
    while waiting:
        screen.fill((0, 0, 0))
        # メッセージ作成
        gameover_txt = font.render(f"GAME OVER!!", True, (255, 255, 255))
        score_txt = font.render(f"Score:{score}", True, (255, 255, 255))
        retry_txt = font.render(f"Press R to Retry", True, (255, 255, 255))
        quit_txt = font.render(f"Press Q to Quit", True, (255, 255, 255))

        # メッセージ表示
        screen.blit(gameover_txt, (screen_width//2 - gameover_txt.get_width()//2, 200))
        screen.blit(score_txt, (screen_width//2 - score_txt.get_width()//2, 250))
        screen.blit(retry_txt, (screen_width//2 - retry_txt.get_width()//2, 350))
        screen.blit(quit_txt, (screen_width//2 - quit_txt.get_width()//2, 400))
        pygame.display.flip()

        # 入力関連イベント
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    # リトライ
                    stages[stage_num-1].run_game()
                elif event.key == pygame.K_q:
                    # 終了
                    pygame.quit()
                    sys.exit()


# 追加----------------------------------------------------------------------------
# ゲーム中に一時停止する関数
def pause_game(screen, clock, font):
    paused = True
    pause_text = font.render("PAUSED - Press P to Resume", True, (255, 255, 255))
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                paused = False

        screen.fill((0, 0, 0))
        screen.blit(pause_text, (screen.get_width() // 2 - pause_text.get_width() // 2,
                                 screen.get_height() // 2 - pause_text.get_height() // 2))
        pygame.display.flip()
        clock.tick(60)


# テキストを折り返す関数（文字単位で折り返す）
def wrap_text(text, font, max_width):
    wrapped_lines = []
    line = ""
    for char in text:
        test_line = line + char
        if font.size(test_line)[0] > max_width:
            wrapped_lines.append(line)
            line = char
        else:
            line = test_line
    if line:
        wrapped_lines.append(line)
    return wrapped_lines


# クレジットを表示する関数
def show_credits(screen, screen_width, screen_height, font):
    japanese_font_path = "modules/NotoSansJP-Regular.ttf"
    font = pygame.font.Font(japanese_font_path, 24)

    showing_credits = True

    credits_lines = [
        "Credits",
        " ",  # 空行
        " ",  # 空行
        "◆Asset Credits◆",
        " ",  # 空行
        " ",  # 空行
        "◆stage1◆",  # 確認◎
        " ",  # 空行
        " ",  # 空行
        "■images■",  # -- 画像 --
        "background image: ",
        "'miyakojima-12695_TP_V4.jpg'by ぱくたそ",
        "(https://www.pakutaso.com/20231034293post-43560.html)",
        "ball image: ",
        "'beach_ball.png' by いらすとや",
        "(https://www.irasutoya.com/2012/03/blog-post_6415.html)",
        "block image: ",
        "'kaigara_nimaigai.png' by いらすとや",
        "(https://www.irasutoya.com/2013/03/blog-post_2173.html)",
        " ",  # 空行
        "■sounds■",  # -- 音楽 --
        "Music:'happytime.mp3' by 甘茶の音楽工房",
        "(https://amachamusic.chagasi.com/music_happytime.html)",
        "sound effects:'miss.mp3' by springn",
        "(https://www.springin.org/sound-stock/category/retrogame/)",
        "'paddle_sound1.mp3' by 効果音ラボ",
        "(https://soundeffect-lab.info/sound/button/)",
        " ",  # 空行

        " ",  # 空行
        "◆stage2◆",  # 確認◎
        " ",  # 空行
        "■images■",  # -- 画像 --
        "background image: ",
        "'hosi2.png','hs0law.png','hs0law2.png' by craftpix.net",
        "(https://craftpix.net/freebies/free-nature-backgrounds-pixel-art/)",
        " ",  # 空行
        "■sounds■",  # -- 音楽 --
        "Music:'sanjinooyatsu.mp3' by 甘茶の音楽工房",
        "(https://amachamusic.chagasi.com/music_sanjinooyatsu.html)",
        "sound effects:'miss.mp3' by springn",
        "(https://www.springin.org/sound-stock/category/retrogame/)",
        "'broken2.mp3' by 効果音ラボ",
        "(https://soundeffect-lab.info/sound/anime/)",
        " ",  # 空行

        " ",  # 空行
        "◆stage3◆",  # 確認◎
        " ",  # 空行
        "■images■",  # -- 画像 --
        "background image: ",
        "'haikei1.png' by Pinterest",
        "(https://jp.pinterest.com/pin/brick-breaker-background--139048707236607950/)",
        " ",  # 空行
        "■sounds■",  # -- 音楽 --
        "Music:'hosi1.mp3' by 甘茶の音楽工房",
        "(https://amachamusic.chagasi.com/music_marbletechno1.html)",
        "sound effects:'break.mp3', 'miss.mp3', 'paddle.mp3' by Springin",
        "(https://www.springin.org/sound-stock/category/retrogame/)",
        " ",  # 空行

        " ",  # 空行
        "◆stage4◆",  # 確認◎
        " ",  # 空行
        "■sounds■",  # -- 音楽 --
        "Music: 'lovelyflower.mp3' by 甘茶の音楽工房",
        "(https://amachamusic.chagasi.com/music_lovelyflower.html)",
        "sound effects:'miss.mp3' by springn",
        "(https://www.springin.org/sound-stock/category/retrogame/)",
        "'broken.mp3' by 効果音ラボ",
        "(https://soundeffect-lab.info/sound/anime/mp3/papa1.mp3)",
        " ",  # 空行

        " ",  # 空行
        "◆stage5◆",  # 確認◎
        " ",  # 空行
        "■images■",  # -- 画像 --
        "background image: ",
        "'FYs2A9.png' by CRAFTPIX.NET",
        "(https://craftpix.net/freebies/free-nature-backgrounds-pixel-art/)",
        "ball/brick/paddle/item image: ",
        "'ball.png/brick_blue.png/paddle.png/item_extend.png' by Aigei",
        "(https://www.aigei.com/s?q=%E7%90%83&type=2d_ui&tab=file)",
        " ",  # 空行
        "■sounds■",  # -- 音楽 --
        "Music:'BGM.mp3' by Aigei",
        "(https://www.aigei.com/sound/class/da_fang_ku/?page=3)",
        "sound effects:'hit.wav/pickup.wav' by Aigei",
        "(https://www.aigei.com/sound/class/da_fang_ku/?page=3)",
        " ",  # 空行

        " ",  # 空行
        "◆stage6◆",  # 確認◎
        " ",  # 空行
        "■images■",  # -- 画像 --
        "background image: ",
        "'FYs2A9.png' by CRAFTPIX.NET",
        "(https://craftpix.net/freebies/free-nature-backgrounds-pixel-art/)",
        "item image: 'item_extend.png' by  Aigei",
        "(https://www.aigei.com/s?q=%E7%90%83&type=2d_ui&tab=file)",
        " ",  # 空行
        "■sounds■",  # -- 音楽 --
        "Music:'retroparty.mp3' by 甘茶の音楽工房 ",
        "(https://amachamusic.chagasi.com/music_retroparty.html)",
        "sound effects:'miss.mp3' by springn",
        "(https://www.springin.org/sound-stock/category/retrogame/)",
        "'paddle_sound_1' by 効果音ラボ",
        "(https://soundeffect-lab.info/sound/button/)",
        "'broken2.mp3' by 効果音ラボ",
        "(https://soundeffect-lab.info/sound/anime/)",
        " ",  # 空行

        " ",  # 空行
        "◆stage7◆",  # 確認◎
        " ",  # 空行
        "■images■",  # -- 画像 --
        "background image: ",
        "'hosi2.png' by FREEP!K",
        "(https://jp.freepik.com/premium-vector/night-sky-with-stars-stars-background_6740039.htm)",
        " ",  # 空行
        "■sounds■",  # -- 音楽 --
        "Music:'picopicodisco.mp3' by 甘茶の音楽工房",
        "(https://amachamusic.chagasi.com/music_picopicodisco.html)",
        "sound effects:'reflection_wall.mp3' by Springin",
        "(https://www.springin.org/sound-stock/category/retrogame/)",
        "'miss.mp3' by 効果音ラボ",
        "(https://soundeffect-lab.info/sound/button/)",
        " ",  # 空行
        " ",  # 空行
        "◇◇ Press ESC to return ◇◇",
    ]

    # 各行をレンダリングしてリストに保存
    rendered_lines = []

    for line in credits_lines:
        wrapped = wrap_text(line, font, screen_width - 100)  # 画面の横幅から少し余裕を引いた値
        for sub_line in wrapped:
            surface = font.render(sub_line, True, (255, 255, 255))
            rendered_lines.append(surface)

    # スクロール用のオフセット初期値（画面の下からスタート）
    y_offset = screen_height

    # スクロール速度
    scroll_speed = 1

    clock = pygame.time.Clock()

    while showing_credits:
        screen.fill((0, 0, 0))

        # 各行を表示（スクロールオフセットを加味）
        for i, line_surface in enumerate(rendered_lines):
            text_x = screen_width // 2 - line_surface.get_width() // 2
            text_y = y_offset + i * 40  # 行間は40px
            screen.blit(line_surface, (text_x, text_y))

        pygame.display.flip()

        # スクロール
        y_offset -= scroll_speed

        # 終了イベントの処理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                showing_credits = False

        clock.tick(60)  # 60FPSで制御
