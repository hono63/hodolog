# -*- coding: utf-8 -*-

from tiny_prolog import *
A, B, C, D, X, Y, Z = Var("A"), Var("B"), Var("C"), Var("D"), Var("X"), Var("Y"), Var("Z") 

import pred_arith
arith = Pred("arith")
pred_arith.set_pred(arith)
print pred_arith.set_pred.__doc__

