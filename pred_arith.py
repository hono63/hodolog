# -*- coding: utf-8 -*-
from tiny_prolog import *


def set_pred(arith):
	u"""
	define of arithmetic pred.
	pred : arith(A, M, B, X)
	M : +,-,*,/,>,>=,<,<=,==
	ex) query(arith(12, "+", -5, X))
		=> arith(12, "+", -5, 7)
	"""

	A, B, C, M, N, X, Y = Var("A"), Var("B"), Var("C"), Var("M"), Var("N"), Var("X"), Var("Y")
	add, sub, le = Pred("add"), Pred("sub"), Pred("le")

	isinstance(arith, Pred)

	def add_callback(env):
		a, b = env[A], env[B]
		assert not isinstance(a, Var)
		assert not isinstance(b, Var)
		return env.unify(X, a + b)

	def sub_callback(env):
		a, b = env[A], env[B]
		assert not isinstance(a, Var)
		assert not isinstance(b, Var)
		return env.unify(X, a - b)

	def le_callback(env):
		a, b = env[A], env[B]
		assert not isinstance(a, Var)
		assert not isinstance(b, Var)
		return env.unify(X, a <= b)

	add(A, B, X).calls(add_callback)
	sub(A, B, X).calls(sub_callback)
	le(A, B, X).calls(le_callback)

	arith(A, "+", B, X) << (add(A, B, X))
	arith(A, "-", B, X) << (sub(A, B, X))
	arith(A, "<=", B, X) << (le(A, B, X))
