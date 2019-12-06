import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import random

import cv2
import numpy as np
from mods import image_processer
import math

MS_SIZE = 30  # ゲームボードのサイズ
CLOSE, OPEN, FLAG = 0, 1, 2


class Game:
    def __init__(self, number_of_mines=10):
        """ ゲームボードの初期化
        Arguments:
        number_of_mines -- 地雷の数のデフォルト値は10

        Side effects:
        mine_map[][] -- 地雷マップ(-1: 地雷，>=0 8近傍の地雷数)
        game_board[][] -- 盤面 (0: CLOSE(初期状態), 1: 開いた状態, 2: フラグ)
        """

        self.init_make_game_board()

    def init_make_game_board(self):
        """ ゲーム盤を初期化 """
        "最初に表示するゲーム盤を作成する"
        self.max_bit_counter = math.ceil(MS_SIZE/3)

        # 正実のgame_boardのサイズ
        self.raw_size = MS_SIZE - self.max_bit_counter

        # 塗り絵をする部分全てCLOSE 大きさは (MS_SIZE-1)
        self.game_board = \
            [[CLOSE for _ in range(self.raw_size)] for _ in range(self.raw_size)]

        # ダミーのbit_imgを作成 全て塗りつぶす図
        self.bit_img = \
            [[1 for _ in range(self.raw_size)] for _ in range(self.raw_size)]

    def open_cell(self, x, y):
        """セル(x, y)を開ける
        Arguments:
        x, y -- セルの位置

        Returns:
          True  -- 8近傍セルをOPENに設定．
                   ただし，既に開いているセルの近傍セルは開けない．
                   地雷セル，FLAGが設定されたセルは開けない．
          False -- 地雷があるセルを開けてしまった場合（ゲームオーバ）
        """
        print(self.bit_img)
        if self.bit_img[y][x] == 1:
            self.game_board[y][x] = OPEN
            print("True")
            return True
        elif self.bit_img[y][x] == 0:
            print("False")
            return False

    def flag_cell(self, x, y):
        """
        セル(x, y)にフラグを設定する，既に設定されている場合はCLOSE状態にする
        """
        # <-- (STEP 5) ここにコードを追加
        if self.game_board[y][x] == OPEN:
            return

        if self.game_board[y][x] == FLAG:
            self.game_board[y][x] = CLOSE
        else:
            self.game_board[y][x] = FLAG

    def is_finished(self):
        """セルが全て開かれたかチェック
        """
        # 全てのボードを開いていたらTrueを返す．まだならFalse.
        # bit_img = 1 and game_board != open ならば まだ完了していない.

        for i in range(self.max_bit_counter, MS_SIZE):
            for j in range(self.max_bit_counter, MS_SIZE):
                if self.bit_img[i][j] == 1 and self.game_board[i][j] != OPEN:
                    return False
        return True


class MyPushButton(QPushButton):
    def __init__(self, text, x, y, parent):
        """ セルに対応するボタンを生成 """
        super(MyPushButton, self).__init__(text, parent)
        self.parent = parent
        self.x = x
        self.y = y
        self.setMinimumSize(25, 25)
        self.setSizePolicy(QSizePolicy.MinimumExpanding,
                           QSizePolicy.MinimumExpanding)

    def set_bg_color(self, colorname):
        """ セルの色を指定する
        Arguments:
            self
            colorname: 文字列 -- 色名 (例, "white")
        """
        self.setStyleSheet("MyPushButton{{background-color: {}}}".format(colorname))

    def on_click(self):
        """ セルをクリックしたときの動作 """
        # *以下，コードを追加*
        print("on_click")
        modifiers = QApplication.keyboardModifiers()
        x = self.x-self.parent.game.max_bit_counter
        y = self.y-self.parent.game.max_bit_counter
        if x < 0 or y < 0:
            return

        if modifiers == Qt.ShiftModifier:# フラグを立てる

            # print(self.x, self.y)
            self.parent.game.flag_cell(x, y)

        elif self.parent.game.game_board[y][x] == CLOSE:#セルを開く

            if not self.parent.game.open_cell(x, y):
                # 地雷があるセルを開けてしまった場合
                QMessageBox.information(self.parent, "Game Over", "ゲームオーバー!")
                print("game over")
                self.parent.close()

        # セルの状態を表示
        self.parent.show_cell_status()

        "ゲームが終了しているかの確認"
        if self.parent.game.is_finished():
            QMessageBox.information(self.parent, "Game Clear", "ゲームクリア!")
            self.parent.close()


class MinesweeperWindow(QMainWindow):
    def __init__(self):
        """ インスタンスが生成されたときに呼び出されるメソッド """
        super(MinesweeperWindow, self).__init__()
        self.game = Game()
        self.initUI()

    def initUI(self):
        """ UIの初期化 """
        w = 900
        h = 600
        self.resize(w, h)
        self.setWindowTitle('Minesweeper')

        # 以下，コードを追加
        # ボタンの追加 {{{

        def gen_button(index_x, index_y, color):
            my_push_button = MyPushButton(' ', index_x, index_y, self)
            my_push_button.set_bg_color(color)
            my_push_button.clicked.connect(my_push_button.on_click)
            return my_push_button

        self.buttons = \
            [[gen_button(x, y, "white") for x in range(MS_SIZE)] for y in range(MS_SIZE)]

        v_box = QVBoxLayout()
        v_box.setSpacing(0)
        for buttons_line in self.buttons:
            h_box = QHBoxLayout()
            for button_cell in buttons_line:
                h_box.addWidget(button_cell)
            v_box.addLayout(h_box)

        container = QWidget()
        container.setLayout(v_box)

        self.setCentralWidget(container)

        # }}}

        # メニューの追加 {{{

        # (1) ニュー項目[File]-[Select]が選択されたときのアクションを生成
        selectAction = QAction('&Select', self)

        # (2) メニュー項目が選択されたときの処理として，MyViewクラスのsetImageメソッドを設定
        selectAction.triggered.connect(self.setImage)

        # (3) メインウィンドウのメニューバーオブジェクトを取得
        menubar = self.menuBar()

        # (4) メニューバーに[File]メニューを追加し，そのアクションとしてselectActionを登録
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(selectAction)

        # }}}

        self.show()
        self.setImage()

    def show_cell_status(self):
        """ ゲームボードを表示 """
        # ★以下，コードを追加★
        print("show-cell")

        def do_button(index_x, index_y, color: str, text: str):
            self.buttons[index_y][index_x].setText(text)
            self.buttons[index_y][index_x].set_bg_color(color)

        for x in range(self.game.max_bit_counter, MS_SIZE):
            for y, cnt in enumerate(self.game.bit_counter_up[x-self.game.max_bit_counter]):
                do_button(x, self.game.max_bit_counter-1-y, "green", str(cnt))

        for y in range(self.game.max_bit_counter, MS_SIZE):
            for x, cnt in enumerate(self.game.bit_counter_side[y-self.game.max_bit_counter]):
                do_button(self.game.max_bit_counter-1-x, y,  "green", str(cnt))

        for y in range(self.game.max_bit_counter, MS_SIZE):
            for x in range(self.game.max_bit_counter, MS_SIZE):
                if self.game.game_board[y-self.game.max_bit_counter][x-self.game.max_bit_counter] == 1:
                    self.buttons[y][x].set_bg_color("black")
                else:
                    self.buttons[y][x].set_bg_color("gray")


    def setImage(self):
        """ 画像を取得して表示 """

        # 画像を選択してファイル名を取得
        file_name = QFileDialog.getOpenFileName(self, 'Open file', './')

        n = np.fromfile(file_name[0], dtype=np.uint8)  # imreadだと日本語のファイル名に対応できないため，np.fromfileとcv2.imdecodeを使う
        cv_img = cv2.imdecode(n, cv2.IMREAD_COLOR)
        if cv_img is None:
            return

        self.game.bit_img = image_processer.makeillust_size(cv_img, MS_SIZE-1, MS_SIZE-1)

        print(self.game.bit_img)

        self.game.bit_counter_side = image_processer.count(self.game.bit_img)
        self.game.bit_counter_up = image_processer.count(self.game.bit_img.T)

        self.show_cell_status()

        print("setImage end")


def main():
    app = QApplication(sys.argv)
    w = MinesweeperWindow()
    app.exec_()


if __name__ == '__main__':
    main()
