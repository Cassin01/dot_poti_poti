import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import random

import cv2
import numpy as np
from mods import image_processer

MS_SIZE = 8  # ゲームボードのサイズ
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

        self.init_game_board()
        self.init_mine_map(number_of_mines)
        self.count_mines()

    def init_game_board(self):
        """ ゲーム盤を初期化 """
        # <-- (STEP 1) ここにコードを追加
        self.game_board = \
            [[CLOSE for _ in range(MS_SIZE)] for _ in range(MS_SIZE)]

    def init_mine_map(self, number_of_mines):
        """ 地雷マップ(self->mine_map)の初期化
        Arguments:
        number_of_mines -- 地雷の数

        地雷セルに-1を設定する．
        """

        # <-- (STEP 2) ここにコードを追加
        self.mine_map = \
            [[0 for _ in range(MS_SIZE)] for _ in range(MS_SIZE)]

        if number_of_mines < 0:
            return

        random_table = []
        for i in range(MS_SIZE):
            for j in range(MS_SIZE):
                random_table.append([random.random(), i, j])

        random_table = sorted(random_table, key=lambda mine: mine[0])

        for i in range(
                number_of_mines
                if number_of_mines <= MS_SIZE * MS_SIZE
                else MS_SIZE * MS_SIZE):
            a_x = random_table[i][1]
            a_y = random_table[i][2]
            self.mine_map[a_y][a_x] = -1

    def count_mines(self):
        """ 8近傍の地雷数をカウントしmine_mapに格納
        地雷数をmine_map[][]に設定する．
        """

        # <-- (STEP 3) ここにコードを追加
        def counter(i: int, j: int) -> int:
            """指定されたセル8近傍の地雷数を返す
            Arguments:
                i, j (int):
            Returns:
                int: 指定されたセル8近傍の地雷数
            """
            summer = 0
            for d_i in range(-1, 2):
                for d_j in range(-1, 2):
                    if d_i == d_j == 0:
                        continue
                    summer += search(i + d_i, j + d_j)
            return summer

        def search(i: int, j: int) -> int:
            """指定されたセルの地雷数を返す
            Arguments:
                i, j (int):
                    セルの位置
            Returns:
                int: 指定されたセルの地雷数
                :param j:
                :param i:
            """
            if 0 <= i < MS_SIZE > j >= 0 and self.mine_map[i][j] == -1:
                return 1

            return 0

        for i in range(MS_SIZE):
            for j in range(MS_SIZE):
                if self.mine_map[i][j] != -1:
                    self.mine_map[i][j] = counter(i, j)

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
        # <-- (STEP 4) ここにコードを追加
        if self.mine_map[y][x] == -1:
            return False
        if self.game_board[y][x] == OPEN:
            return True
        self.game_board[y][x] = OPEN

        def search(i: int, j: int) -> None:
            """指定されたセルを開く
            Arguments:
                i, j (int):
            Returns:
                None
            """
            if (0 <= i < MS_SIZE > j >= 0 and
                    self.game_board[i][j] != FLAG and
                    self.mine_map[i][j] != -1):
                self.game_board[i][j] = OPEN

        for d_y in range(-1, 2):
            for d_x in range(-1, 2):
                if d_y == d_x == 0:
                    continue
                search(y + d_y, x + d_x)

        return True

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
        """地雷セル以外のすべてのセルが開かれたかチェック
        """
        # <-- (STEP 6) ここにコードを追加
        for i in range(MS_SIZE):
            for j in range(MS_SIZE):
                if (self.game_board[i][j] == OPEN or
                        (self.game_board[i][j] != OPEN and
                         self.mine_map[i][j] == -1)):
                    continue
                return False
        return True

    def print_game_board(self):
        marks = ['x', ' ', 'P']
        self.print_header()
        print("[y]")
        for y in range(MS_SIZE):
            print("%2d|" % y, end="")
            for x in range(MS_SIZE):
                if self.game_board[y][x] == OPEN and self.mine_map[y][x] > 0:
                    print("%3d" % self.mine_map[y][x], end="")
                else:
                    print("%3s" % marks[self.game_board[y][x]], end="")
            print("")
        self.print_footer()


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
        modifiers = QApplication.keyboardModifiers()

        if modifiers == Qt.ShiftModifier:
            # フラグを立てる
            print(self.x, self.y)
            self.parent.game.flag_cell(self.x, self.y)
        elif self.parent.game.game_board[self.y][self.x] == CLOSE:
            if not self.parent.game.open_cell(self.x, self.y):
                # 地雷があるセルを開けてしまった場合
                QMessageBox.information(self.parent, "Game Over", "ゲームオーバー!")
                self.parent.close()

        # セルの状態を表示
        self.parent.show_cell_status()

        # ゲームが終了しているかの確認
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

        # ★以下，コードを追加★
        # ボタンの追加 {{{

        def gen_button(index_x, index_y, color):
            my_push_button = MyPushButton('x', index_x, index_y, self)
            my_push_button.set_bg_color(color)
            my_push_button.clicked.connect(my_push_button.on_click)
            return my_push_button

        self.buttons = \
            [[gen_button(x, y, "gray") for x in range(MS_SIZE)] for y in range(MS_SIZE)]

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

    def show_cell_status(self):
        """ ゲームボードを表示 """
        # ★以下，コードを追加★
        print("show-cell")
        for y, game_line in enumerate(self.game.game_board):
            for x, game_cell in enumerate(game_line):
                if game_cell == CLOSE:
                    self.buttons[y][x].setText("x")
                    self.buttons[y][x].set_bg_color("gray")
                elif game_cell == OPEN:
                    text = str(self.game.mine_map[y][x])
                    self.buttons[y][x].setText(text)
                    self.buttons[y][x].set_bg_color("blue")
                else:
                    self.buttons[y][x].setText("P")
                    self.buttons[y][x].set_bg_color("yellow")

    def setImage(self):
        """ 画像を取得して表示 """

        # 画像を選択してファイル名を取得
        file_name = QFileDialog.getOpenFileName(self, 'Open file', './')

        n = np.fromfile(file_name[0], dtype=np.uint8)  # imreadだと日本語のファイル名に対応できないため，np.fromfileとcv2.imdecodeを使う
        cv_img = cv2.imdecode(n, cv2.IMREAD_COLOR)
        if cv_img is None:
            return

        bit_img = image_processer.makeillust_size(cv_img, 30, 30)
        side = image_processer.count(bit_img)
        up = image_processer.count(bit_img.T)
        print("side: ", side)
        print("up: ", up)


def main():
    app = QApplication(sys.argv)
    w = MinesweeperWindow()
    app.exec_()


if __name__ == '__main__':
    main()
