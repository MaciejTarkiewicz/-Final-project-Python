import abc
from sys import stdin


class Board:
    def __init__(self, size = 8):
        self.size = size
        self.blacks = self.whites = (self.size / 2) * 3
        self.board = [[Pawn('_', x, y) for x in range (size)] for y in range (size)]
        for i in range(3):
            for j in range(4):
                self.board[i][(2 * j) + ((i + 1) % 2)] = Pawn('B', (2 * j) + ((i + 1) % 2), i)
                self.board[len(self.board) - 1 - i][(2 * j) + (i % 2)] = Pawn('W', (2 * j) + (i % 2), len(self.board) - 1 - i)

    def __str__(self):
        l = ["".join([(self.board[y][x].color + " ") for x in range(self.size)]) for y in range(self.size)]
        printed = "  "
        for i in range(self.size):
            printed += chr(ord('A') + i) + " "
        for i in range(self.size):
            printed += "\n" + str(i) + " " + l[i]
        return printed


class Pawn:
    def __init__(self, color, x, y):
        self.color = color
        self.x = x
        self.y = y


class Engine:
    def __init__(self):
        self.board = Board()
        self.turn = []
        self.turn.append("White's turn")
        self.turn.append("Black's turn")
        self.translator = {}
        self.translator['left'] = self.translator['down'] = -1
        self.translator['right'] = self.translator['up'] = 1
        self.translator[1] = "White Player Wins!"
        self.translator[0] = "Black Player Wins!"

    def game_loop(self):
        turn = 0
        print("W - normal white pawn\nB - normal black pawn\nψ - special white pawn\nβ - special black pawn\n\n")
        print("Syntax:\nFirst argument - X coordinate\nSecond argument - Y coordinate\n" +
                "Third argument - X direction (left or right)\nFourth argument - Y direction (down or up)\n" +
                "Example: A 5 right down.\nPS. Down means y-=1, up means y+=1, left means x-=1, right means x+=1\n" +
                "Size of the letters is arbitrary.\n\n")
        while(True):
            if (not self.__can_move_color(turn)):
                print(self.translator[turn])
                break
            print(self.board)
            print('\n' + self.turn[turn])
            if (self.board.whites <= 0):
                print("Black Player Wins!")
                break
            elif (self.board.blacks <= 0):
                print("White Player Wins!")
                break

            cmd = stdin.readline()[:-1]
            cmdlist = cmd.split(" ")
            if(len(cmdlist) < 4):
                print("Tell me what to do")
                continue

            cmdlist[0] = cmdlist[0].upper()
            cmdlist[2] = cmdlist[2].lower()
            cmdlist[3] = cmdlist[3].lower()

            try:
                x = Engine.__decode(cmdlist[0])
                y = int(cmdlist[1])
                if (x >= 8 or y >= 8 or x < 0 or y < 0):
                    print("Enter correct coordinates!")
                    continue
            except:
                print("Enter correct coordinates!")
                continue
            try:
                self.move(self.board.board[y][x], turn, self.translator[cmdlist[2]], self.translator[cmdlist[3]])
            except WrongMoveException as exc:
                print("Wrong move! Message: {0}".format(exc))
                continue
            except:
                print("Unknown command {0} {1}".format(cmdlist[2], cmdlist[3]))
                continue
            print("\n\n")
            turn = (turn + 1) % 2

    def move(self, pwn, turn, mod_x, mod_y):
        try:
            Engine.__valid_pawn(pwn)
            Engine.__valid_down(pwn, pwn.y + mod_y)
            Engine.__valid_move(pwn, mod_x, mod_y, turn)

            if (self.board.board[pwn.y + mod_y][pwn.x + mod_x].color == '_'):
                self.board.board[pwn.y + mod_y][pwn.x + mod_x] = pwn
                self.board.board[pwn.y][pwn.x] = Pawn('_', pwn.x, pwn.y)
                pwn.x += mod_x
                pwn.y += mod_y

            elif (self.board.board[pwn.y + 2 * mod_y][pwn.x + 2 * mod_x].color == '_' and
                self.board.board[pwn.y + mod_y][pwn.x + mod_x].color != pwn.color):

                Engine.__valid_move(pwn, 2 * mod_x, 2 * mod_y, turn)
                if (self.board.board[pwn.y + mod_y][pwn.x + mod_x].color == 'W' or
                    self.board.board[pwn.y + mod_y][pwn.x + mod_x].color == 'ψ'):

                    self.board.whites -= 1
                else:
                    self.board.blacks -= 1
                self.board.board[pwn.y + 2 * mod_y][pwn.x + 2 * mod_x] = pwn
                self.board.board[pwn.y + mod_y][pwn.x + mod_x] = Pawn('_', pwn.x + mod_x, pwn.y + mod_y)
                self.board.board[pwn.y][pwn.x] = Pawn('_', pwn.x, pwn.y)
                pwn.x += 2 * mod_x
                pwn.y += 2 * mod_y
                turn = (turn + 1) % 2
            else:
                raise WrongMoveException("You can't move on your another pawn!")

            if (pwn.color == 'W' and pwn.y == 0):
                pwn.color = 'ψ'
            elif (pwn.color == 'B' and pwn.y == 7):
                pwn.color = 'β'
        except Exception as exc:
            raise WrongMoveException(exc)


    @staticmethod
    def __valid_pawn(pwn):
        if (pwn.color == '_'):
            raise NullPawnException("There's no pawn at coordinates ({0}, {1})".format(Engine.__encode(pwn.x), pwn.y))

    @staticmethod
    def __valid_down(pwn, new_y):
        if (pwn.color == 'W' and pwn.y < new_y or pwn.color == 'B' and pwn.y > new_y):
            raise WrongMoveException("You can't move back with normal pawn")

    @staticmethod
    def __valid_move(pwn, step_x, step_y, turn):
        if (pwn.x + step_x >= 8 or pwn.y + step_y >= 8 or pwn.x + step_x < 0 or pwn.y + step_y < 0):
            raise OutOfBoardException("You can't move out of board")
        if (pwn.color == 'W' and turn == 1 or pwn.color == 'B' and turn == 0):
            raise TurnException("It's not your turn!")

    def __can_move_color(self, turn):
        list = []
        mod_y = 0
        if (turn):
            list = [black for l in self.board.board for black in l if (black.color == 'B' or black.color == 'β')]
            mod_y = 1
        else:
            list = [white for l in self.board.board for white in l if (white.color == 'W' or white.color == 'ψ')]
            mod_y = -1
        for pwn in list:
            if (self.__can_move(pwn, turn, mod_y)): return True
            if (pwn.color == 'ψ' or pwn.color == 'β'):
                if (self.__can_move(pwn, turn, -mod_y)): return True
        return False


    def __can_move(self, pwn, turn, mod_y):
        if (pwn.x + 1 < 8 and pwn.y + mod_y >= 0 and pwn.y + mod_y < 8):
            if (self.board.board[pwn.y + mod_y][pwn.x + 1].color == '_'):
                return True
        elif (pwn.x - 1 >= 0 and pwn.y + mod_y >= 0 and pwn.y + mod_y < 8):
            if (self.board.board[pwn.y + mod_y][pwn.x - 1].color == '_'):
                return True
        elif (pwn.x + 2 < 8 and pwn.y + 2 * mod_y >= 0 and pwn.y + 2 * mod_y < 8):
            if (self.board.board[pwn.y + 2 * mod_y][pwn.x + 2].color == '_' and self.board.board[pwn.y + mod_y][pwn.x + 1].color != pwn.color):
                return True
        elif (pwn.x - 2 >= 0 and pwn.y + 2 * mod_y >= 0 and pwn.y + 2 * mod_y < 8):
            if (self.board.board[pwn.y + 2 * mod_y][pwn.x - 2].color == '_' and self.board.board[pwn.y + mod_y][pwn.x - 1].color != pwn.color):
                return True
        return False

    @staticmethod
    def __decode(x):
        return ord(x) - ord('A')

    @staticmethod
    def __encode(x):
        return chr(x + ord('A'))


class TurnException(Exception):
    pass

class OutOfBoardException(Exception):
    pass

class WrongMoveException(Exception):
    pass

class NullPawnException(Exception):
    pass


def main():
    e = Engine()
    e.game_loop()

main()
