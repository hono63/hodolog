# -*- coding: utf-8 -*-
from tiny_prolog import *


def hanoi_pred(top):
    A, B, C, X, Y = Var("A"), Var("B"), Var("C"), Var("X"), Var("Y")
    hanoi, write_move, write = Pred("hanoi"), Pred("write_move"), Pred("write")

    def write_callback(env):
        print env[A],
        return True

    write(A).calls(write_callback)

    write_move(X, A, B) << (
        write("move"), write(X), 
        write("from"), write(A), write("to"), write(B), write("\n"))

    hanoi(top, A, B, C) << (    # 頂上 top を A から B に移すには
        write_move(top, A, B))  # top を A から B に移す。

    hanoi((X, Y), A, B, C) << ( # 底が X, 上部が Y の塔を A から B に移すには
        hanoi(Y, A, C, B),      # Y を A から C に移して
        write_move(X, A, B),    # X を A から B に移して 
        hanoi(Y, C, B, A))      # Y を C から B に移す。
    return hanoi


if __name__=="__main__":
	hanoi = hanoi_pred("top")
	query (hanoi(("base", ("3rd", ("2nd", "top"))), "Left", "Center", "Right"))

