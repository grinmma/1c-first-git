import sys
import sqlite3
import random as ran
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QMainWindow, QAction, QSpinBox, QLineEdit, QLabel, \
    QTableWidgetItem


class DBSaper(QMainWindow):
    def __init__(self, main=None, player='player1'):
        self.main = main
        super().__init__(main)
        uic.loadUi('gamerStat.ui', self)
        self.player = player
        self.con = sqlite3.connect('Saper_Games_and_Players.db')
        self.show_b.clicked.connect(self.showGames)
        self.back_b.clicked.connect(self.back)
        self.showPlayer_b.clicked.connect(self.showPlayers)
        self.showAll_b.clicked.connect(self.showAllGame)
        self.deleteAllGames_b.clicked.connect(self.deleteAllGames)

    def back(self):
        self.close()
        self.main.show()

    def deleteAllGames(self):
        cur = self.con.cursor()
        cur.execute('''DELETE from Game
        WHERE id BETWEEN 1 AND 100001''')
        cur.execute('''UPDATE Players
        SET Number_of_games = 0
        WHERE id BETWEEN 1 AND 1001''')
        self.tableWidget.setRowCount(1)
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setItem(0, 0, QTableWidgetItem('Side'))
        self.tableWidget.setItem(0, 1, QTableWidgetItem('Num of Bomb'))
        self.tableWidget.setItem(0, 2, QTableWidgetItem('Player'))
        self.tableWidget.setItem(0, 3, QTableWidgetItem('Result'))

        self.con.commit()

    def showGames(self):
        cur = self.con.cursor()
        result = cur.execute('''Select side, bombs, player, result from Game WHERE player=
        (Select id from Players WHERE PlayerName like ?)''',
                             (self.player,)).fetchall()
        self.tableWidget.setRowCount(len(result) + 1)
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setItem(0, 0, QTableWidgetItem('Side'))
        self.tableWidget.setItem(0, 1, QTableWidgetItem('Num of Bomb'))
        self.tableWidget.setItem(0, 2, QTableWidgetItem('Player'))
        self.tableWidget.setItem(0, 3, QTableWidgetItem('Result'))
        for i, elem in enumerate(result):
            for j, val in enumerate(elem):
                self.tableWidget.setItem(i + 1, j, QTableWidgetItem(str(val)))

    def showPlayers(self):
        cur = self.con.cursor()
        result = cur.execute(
            '''Select PlayerName, Number_of_Games from Players WHERE id BETWEEN 1 AND 1001''').fetchall()
        self.tableWidget.setRowCount(len(result) + 1)
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setItem(0, 0, QTableWidgetItem('Player Name'))
        self.tableWidget.setItem(0, 1, QTableWidgetItem('Numb of Game'))
        for i, elem in enumerate(result):
            for j, val in enumerate(elem):
                self.tableWidget.setItem(i + 1, j, QTableWidgetItem(str(val)))

    def showAllGame(self):
        cur = self.con.cursor()
        result = cur.execute(
            '''Select side, bombs, player, result from Game WHERE id BETWEEN 0 AND 1001''').fetchall()
        self.tableWidget.setRowCount(len(result) + 1)
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setItem(0, 0, QTableWidgetItem('Side'))
        self.tableWidget.setItem(0, 1, QTableWidgetItem('Num of Bomb'))
        self.tableWidget.setItem(0, 2, QTableWidgetItem('Player'))
        self.tableWidget.setItem(0, 3, QTableWidgetItem('Result'))
        for i, elem in enumerate(result):
            for j, val in enumerate(elem):
                if j == 2:
                    temp = cur.execute('Select PlayerName from Players WHERE id = ?', (val,)).fetchall()[0][0]
                    self.tableWidget.setItem(i + 1, j, QTableWidgetItem(temp))
                    continue
                self.tableWidget.setItem(i + 1, j, QTableWidgetItem(str(val)))


class SaperGame:
    def __init__(self, len_pole=10, num_of_bomb=3):
        self.bomb = 'b'
        self.map_ = []
        self.map_bool = []
        self.playr_die = False
        self.player_win = False
        self.num_bomb_gl = 0
        self.map_generate(len_pole, num_of_bomb)

    def check_bomb_around(self, ind_i, ind_j):
        num_bomb = 0
        if self.map_[ind_i][ind_j] != self.bomb:
            for i in range(ind_i - 1, ind_i + 2):
                for j in range(ind_j - 1, ind_j + 2):
                    if not (0 <= i < len(self.map_[0]) and 0 <= j < len(self.map_)):
                        continue
                    else:
                        if self.map_[i][j] == self.bomb:
                            num_bomb += 1
            return num_bomb
        else:
            return self.bomb

    def check_player_win(self):
        global num_bomb_gl
        num_of_flag_point = 0
        player_win_temp = True
        for i in range(len(self.map_[0])):
            for j in range(len(self.map_)):
                if self.map_bool[i][j] == 'c':
                    player_win_temp = False
                    break
                if self.map_bool[i][j] == 'f' or self.map_bool[i][j] == '?':
                    num_of_flag_point += 1
            if not player_win_temp:
                break
        if num_of_flag_point != self.num_bomb_gl or not player_win_temp:
            player_win_temp = False
        return player_win_temp

    def player_check_point(self, x, y, operation, after_the_num=False):
        if not (0 <= x < len(self.map_[0]) and 0 <= y < len(self.map_)):
            return 'ERROR: wrong coords'
        if self.map_bool[x][y] != 'o':
            if operation == 'open':
                if self.map_bool[x][y] == 'f':
                    self.map_bool[x][y] = '?'
                    return 'make "?"'
                elif self.map_bool[x][y] == '?':
                    self.map_bool[x][y] = 'c'
                    return 'make close'
                else:
                    if self.map_[x][y] == self.bomb and not after_the_num:
                        self.playr_die = True
                        self.map_bool[x][y] = 'o'
                        return 'You are lose'
                    self.map_bool[x][y] = 'o'
                if self.map_[x][y] == 0:
                    if x + 1 < len(self.map_[0]):
                        if y + 1 < len(self.map_):
                            self.player_check_point(x + 1, y + 1, operation, True)
                        self.player_check_point(x + 1, y, operation, True)
                        if y - 1 >= 0:
                            self.player_check_point(x + 1, y - 1, operation, True)
                    if y + 1 < len(self.map_):
                        self.player_check_point(x, y + 1, operation, True)
                    if y - 1 >= 0:
                        self.player_check_point(x, y - 1, operation, True)
                    if x - 1 >= 0:
                        if y - 1 >= 0:
                            self.player_check_point(x - 1, y - 1, operation, True)
                        self.player_check_point(x - 1, y, operation, True)
                        if y + 1 < len(self.map_):
                            self.player_check_point(x - 1, y + 1, operation, True)
                return 'make open'
            if operation == 'flag':
                self.map_bool[x][y] = 'f'
                return 'make flag'
        else:
            return 'Opened point'

    def map_generate(self, x, num_bomb):
        self.num_bomb_gl = num_bomb
        self.map_ = [[0 for j in range(x)] for i in range(x)]
        self.map_bool = [['c' for j in range(x)] for i in range(x)]
        temp_x = []
        for i in range(x):
            for j in range(x):
                temp_x.append((i, j))
        for i in range(num_bomb):
            x_bomb_coord = ran.choice(temp_x)
            self.map_[x_bomb_coord[0]][x_bomb_coord[1]] = self.bomb
            del temp_x[temp_x.index(x_bomb_coord)]
        for i in range(x):
            for j in range(x):
                self.map_[i][j] = self.check_bomb_around(i, j)


class Saper(QMainWindow):
    def __init__(self):
        super().__init__()
        self.con = sqlite3.connect('Saper_Games_and_Players.db')
        self.pole = []
        self.side_number = 0
        self.bombs_number = 0
        self.game = SaperGame()
        self.operation = 'open'
        self.player = 'player1'
        self.resalt = ''
        self.initUI()

    def playerGamesPlusOne(self):
        cur = self.con.cursor()
        player = cur.execute('''Select id from Players WHERE PlayerName like ?''',
                             (self.player,)).fetchall()[0][0]
        cur.execute('''UPDATE Players
        SET Number_of_games = Number_of_games + 1
        WHERE id = ?''', (player,))
        self.con.commit()

    def addPlayer(self):
        cur = self.con.cursor()
        players = [i[0] for i in cur.execute('''Select PlayerName from Players
         WHERE id BETWEEN 0 AND 1001''').fetchall()]
        if self.player not in players:
            cur.execute('INSERT INTO Players(PlayerName, Number_of_games) VALUES(?, ?)', (self.player, 0))
        self.con.commit()

    def addGame(self, side, bombs, result):
        cur = self.con.cursor()
        player = cur.execute('''Select id from Players WHERE PlayerName like ?''',
                             (self.player,)).fetchall()[0][0]
        cur.execute('INSERT INTO Game(side, bombs, player, result) VALUES(?, ?, ?, ?)', (side, bombs, player, result))
        self.con.commit()

    def newGameWindow(self):

        self.side_number = self.side_sb.value()
        self.bombs_number = self.bombs.value()
        self.player = self.player_line.text()
        self.addPlayer()
        self.game = SaperGame(self.side_sb.value(), self.bombs.value())
        self.close()
        for i in self.pole:
            for j in i:
                j.close()
        self.pole.clear()
        x, y = 10, 70 + self.flag_to_open_b.height() + 10
        for i in range(len(self.game.map_)):
            self.pole.append([])
            for j in range(len(self.game.map_)):
                self.pole[i].append(QPushButton(self))
                self.pole[i][j].move(x, y)
                self.pole[i][j].resize(20, 20)
                self.pole[i][j].clicked.connect(self.checkCell)
                self.pole[i][j].setText('')
                self.pole[i][j].setStyleSheet('background: #76428a;')
                x += 20
            y += 20
            x = 10
        temp = (30 + self.play_b.width() + 10 + self.player_line.width() + 10 + self.side_sb.width() + 10
                + self.bombs.width() + 30)
        self.setGeometry(300, 300, self.width(), len(self.game.map_) * 20 + 70 + self.flag_to_open_b.height() + 10 + 20)
        if len(self.game.map_) * 20 + 20 >= temp:
            self.setGeometry(300, 300, len(self.game.map_) * 20 + 20, self.height())
        elif len(self.game.map_) * 20 + 20 < temp and len(self.game.map_) * 20 + 20 < self.width():
            self.setGeometry(300, 300, temp, self.height())
        self.show()

    def gamerStat(self):

        db = DBSaper(self, self.player)
        db.show()
        self.hide()

    def initUI(self):

        self.flag_to_open_b = QPushButton(self)
        self.flag_to_open_b.setText('Operation:' + self.operation)
        self.flag_to_open_b.clicked.connect(self.button_that_change_operation_Flag_and_Open)
        self.flag_to_open_b.move(30, 70)
        self.flag_to_open_b.resize(self.flag_to_open_b.sizeHint())

        self.labelresalts = QLabel(self)
        self.labelresalts.setText('')
        self.labelresalts.move(30 + self.flag_to_open_b.width() + 10, 70)

        self.play_b = QPushButton(self)
        self.play_b.setText('Play!')
        self.play_b.clicked.connect(self.newGameWindow)
        self.play_b.move(30, 40)
        self.play_b.resize(self.play_b.sizeHint())

        self.labels = [QLabel(self), QLabel(self), QLabel(self)]

        self.player_line = QLineEdit(self)
        self.player_line.setText('player1')
        self.player_line.move(self.play_b.x() + self.play_b.width() + 10, 40)
        self.labels[0].setText('Enter Player name:')
        self.labels[0].move(self.player_line.x(), 15)

        self.side_sb = QSpinBox(self)
        self.side_sb.setMinimum(10)
        self.side_sb.setMaximum(32)
        self.side_sb.move(self.player_line.x() + self.player_line.width() + 10, 40)
        self.side_sb.resize(self.side_sb.sizeHint())
        self.labels[1].setText('Side:')
        self.labels[1].move(self.side_sb.x(), 15)

        self.bombs = QSpinBox(self)
        self.bombs.setMaximum(99)
        self.bombs.setMinimum(3)
        self.bombs.move(self.side_sb.x() + self.side_sb.width() + 10, 40)
        self.bombs.resize(self.bombs.sizeHint())
        self.labels[2].setText('Num bombs:')
        self.labels[2].move(self.bombs.x(), 15)

        gamerStatAction = QAction('&Show Past Games', self)
        gamerStatAction.setShortcut('Ctrl+S')
        gamerStatAction.setStatusTip('You will see the results of previous games')
        gamerStatAction.triggered.connect(self.gamerStat)

        self.statusBar()
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&Games')
        fileMenu.addAction(gamerStatAction)
        self.setGeometry(300, 300,
                         30 + self.play_b.width() + 10 + self.player_line.width() + 10 + self.side_sb.width() + 10
                         + self.bombs.width() + 30, 300)  # окно
        self.setWindowTitle('Saper')

    def button_that_change_operation_Flag_and_Open(self):
        if self.operation == 'open':
            self.operation = 'flag'
        else:
            self.operation = 'open'
        self.flag_to_open_b.setText('Operation:' + self.operation)

    def checkCell(self):
        x, y = 0, 0
        for i in self.pole:
            if self.sender() in i:
                x, y = i.index(self.sender()), self.pole.index(i)
        temp = self.game.player_check_point(x, y, self.operation)
        if temp == 'You are lose':
            self.breakGame()
        if self.game.check_player_win():
            self.congratulateThePlayer()
        for i in self.pole:
            for j in i:
                if self.game.map_bool[i.index(j)][self.pole.index(i)] == 'c':
                    j.setText('')
                    j.setStyleSheet('background: #76428a;')
                    continue
                j.setText(str(self.game.map_[i.index(j)][self.pole.index(i)]))
                j.setStyleSheet('background: #82a8ff;')
                if self.game.map_bool[i.index(j)][self.pole.index(i)] == 'f':
                    j.setText('⚑')
                    j.setStyleSheet('background: #f00000;')
                if self.game.map_bool[i.index(j)][self.pole.index(i)] == '?':
                    j.setText('?')
                    j.setStyleSheet('background: #82a8ff;')
                if self.game.map_[i.index(j)][self.pole.index(i)] == 0:
                    j.setText('')

    def congratulateThePlayer(self):

        for i in self.pole:
            for j in i:
                j.setEnabled(False)
        self.resalt = 'You are the winner! New game?)'
        self.labelresalts.setText(self.resalt)
        self.labelresalts.resize(self.labelresalts.sizeHint())
        self.addGame(self.side_number, self.bombs_number, 'win')
        self.playerGamesPlusOne()

    def breakGame(self):
        for i in self.pole:
            for j in i:
                j.setEnabled(False)
        self.resalt = 'You were wrong ... Try again?'
        self.labelresalts.setText(self.resalt)
        self.labelresalts.resize(self.labelresalts.sizeHint())
        self.addGame(self.side_number, self.bombs_number, 'lose')
        self.playerGamesPlusOne()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Saper()
    ex.show()
    sys.exit(app.exec())
