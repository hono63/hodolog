# -*- coding: utf-8 -*-
from tiny_prolog import *


def arith_pred(arith):
	A, B, C, M, N, X, Y = Var("A"), Var("B"), Var("C"), Var("M"), Var("N"), Var("X"), Var("Y")
	sub, le = Pred("sub"), Pred("le")

	assert isinstance(arith, Pred)

	def sub_callback(env):
		a, b = env[A], env[B]
		assert not isinstance(a, Var)
		assert not isinstance(b, Var)
		return env.unify(X, a - b)

	sub(A, B, X).calls(sub_callback)

	def le_callback(env):
		a, b = env[A], env[B]
		assert not isinstance(a, Var)
		assert not isinstance(b, Var)
		return env.unify(X, a <= b)

	le(A, B, X).calls(le_callback)

	arith(A, "<=", B, X) << (le(A, B, X))
	arith(A, "-", B, X) << (sub(A, B, X))
	#arith((A,M,B), N, C, Y) << (arith(A,M,B,X), arith(X,N,C,Y))
	#arith(C, N, (A,M,B), Y) << (arith(A,M,B,X), arith(C,N,X,Y))

def arith_add(arith):
	A, B, X = Var("A"), Var("B"), Var("X")
	add = Pred("add")

	assert isinstance(arith, Pred)

	def add_callback(env):
		a, b = env[A], env[B]
		assert not isinstance(a, Var)
		assert not isinstance(b, Var)
		return env.unify(X, a + b)

	add(A, B, X).calls(add_callback)
	arith(A, "+", B, X) << (add(A, B, X))


if __name__=="__main__":
	arith = Pred("arith")
	arith_pred(arith)
	arith_add(arith)
	print "pred : arith(A, M, B, X)"
