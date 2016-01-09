# -*- coding: utf-8 -*-
import tiny_prolog as pl

A, B, C, X = pl.Var("A"), pl.Var("B"), pl.Var("C"), pl.Var("X")

be, do = pl.Pred("be"), pl.Pred("do")

male, female = pl.Pred("male"), pl.Pred("female")
parent, child = pl.Pred("parent"), pl.Pred("child")
grandparent, grandchild = pl.Pred("grandparent"), pl.Pred("grandchild")
grandparent, offspring = pl.Pred("predecessor"), pl.Pred("offspring")
father, mother = pl.Pred("father"), pl.Pred("mother")
son, daughter = pl.Pred("son"), pl.Pred("daughter")
brother, sister = pl.Pred("brother"), pl.Pred("sister")
brothers, sisters = pl.Pred("brothers"), pl.Pred("sisters")

child(A, B) << (parent(B, A))
father(A, B) << (parent(A, B), male(A))
mother(A, B) << (parent(A, B), female(A))
son(A, B) << (child(A, B), male(A))
daughter(A, B) << (child(A, B), female(A))
brother(A, B) << (child(A, X), child(B, X), male(A))
sister(A, B) << (child(A, X), child(B, X), female(A))
brothers(A, B) << (child(A, X), child(B, X), male(A), male(B))
sisters(A, B) << (child(A, X), child(B, X), female(A), female(B))

if __name__=="__main__":
	male("kiyoaki")  << ()
	female("chieko") << ()
	female("yuki")   << ()
	female("ai")     << ()
	male("norifumi") << ()

	parent("kiyoaki", "yuki") << ()
	parent("kiyoaki", "ai") << ()
	parent("kiyoaki", "norifumi") << ()
	parent("chieko", "yuki") << ()
	parent("chieko", "ai") << ()
	parent("chieko", "norifumi") << ()
