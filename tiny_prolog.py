# -*- coding: utf-8 -*- Copyright (c) 1998, 2006 Oki Software Co., Ltd.
u"""Tiny Prolog in Python

この処理系で項 (term) とは，
1. 定数 (数や文字列など) であるか，
2. 変数 (Var のインスタンス) であるか，
3. 述語項であるか，
4. 項を要素とする tuple または list である。
項での定数の等価性は == 演算で判定される。 
      変数の等価性は is 演算で判定される。
      tuple および list の等価性は各要素の等価性で判定される。

この処理系で述語項 (predication) とは，
0 個以上の項を引数とした述語の呼出しである。
述語 (Pred のインスタンス) の等価性は is 演算で判定される。

この処理系で節 (clause) の定義とは，述語項を左辺とする << 演算である。
左辺が頭部を，右辺が本体を表す。
右辺は述語項，CUT，またはタプル (ただし各要素は述語項または CUT) である。
空の本体は空のタプルで表す。

たとえば，標準的な Prolog での

man(adam).
parent(adam, cain).
father(F, C) :- man(F), parent(F, C).

は次のように表現される。

man, parent, father = Pred('man'), Pred('parent'), Pred('father')
F, C = Var('F'), Var('C')

man('adam') << ()
parent('adam', 'cain') << ()
father(F, C) << (man(F), parent(F, C))
"""

__date__ = "13 July 2006"
__version__ = "1.3"
CUT = "!"


# Prolog 構文を構成するための公開クラス

class Var:
    u"変数 (variable)"
    def __init__(self, name):
        u"name は repr() による表示にだけ使用される。"
        self.name = name

    def __repr__(self):
        return self.name

class Pred:
    u"述語 (predicate)"
    def __init__(self, name):
        u"name は repr() による表示にだけ使用される。"
        self.name = name
        self.__defs = []

    def __repr__(self):
        return self.name

    def __call__(self, *args):
        u"述語項を構成する。"
        return _Goal(self, args)

    def defs(self):
        u"節 (head と body からなるタプル) からなるリスト"
        return self.__defs

    def add_def(self, head, body):
        u"節 (head と body) を追加する。"
        self.__defs.append((head, body))


# 処理系内部でインスタンスが構築されるクラス

class _Goal:
    u"述語項"
    def __init__(self, pred, args):
        assert isinstance(args, tuple)
        self.pred = pred
        self.args = args

    def __lshift__(self, rhs):
        u"節を定義する。self が節の頭部，rhs が節の本体となる。"
        if not isinstance(rhs, tuple):
            rhs = rhs,
        if __debug__:
            for t in rhs:
                assert t is CUT or isinstance(t, _Goal)
        self.pred.add_def(self, pair(rhs))

    def calls(self, callback):
        u"""コールバックを定義する。
        self が unify されたとき，それに対する CallbackEnv インスタンス
        を引数として関数 callback が呼び出されるようにする。
        callback は True (成功) か False (失敗) を返す。
        """
        assert callable(callback)
        self.pred.add_def(self, callback)

    def __repr__(self):
        if len(self.args) == 1:
            return "%s(%r)" % (self.pred, self.args[0])
        else:
            return "%s%s" % (self.pred, self.args)

class Env:
    u"環境 (environment)"
    def __init__(self):
        self.__table = {}       #  {Var: (term, Env)}

    def put(self, x, (t, env)):
        u"変数 x を，項 t とその環境 env のペアに束縛する。"
        assert isinstance(x, Var)
        assert isinstance(env, Env)
        self.__table[x] = (t, env)

    def get(self, x):
        u"変数 x が束縛されている項とその環境のペア (なければ None) を返す。"
        return self.__table.get(x)

    def delete(self, x):
        u"変数 x の束縛を取り消す。"
        del self.__table[x]

    def clear(self):
        u"束縛をすべて取り消す。"
        self.__table.clear()

    def dereference(self, t):
        u"""非変数または未束縛の変数が得られるまで項 t の値を参照する。
        得られた値とその環境のペアを返す。
        """
        env = self
        while isinstance(t, Var):
            p = env.get(t)
            if p is None:
                break
            (t, env) = p
        return (t, env)

    def __getitem__(self, t):
        u"項 t に含まれる変数を再帰的にできる限り展開し，その値を返す。"
        (t, env) = self.dereference(t)
        if isinstance(t, _Goal):
            return _Goal(t.pred, env[t.args])
        elif isinstance(t, list):
            return [env[a] for a in t]
        elif isinstance(t, tuple):
            return tuple([env[a] for a in t])
        else:
            return t

class CallbackEnv:
    u"コールバック用の環境 (実体は節の環境)"
    def __init__(self, env, trail):
        self.__env = env
        self.__trail = trail

    def __getitem__(self, t):
        u"項 t に含まれる変数を再帰的にできる限り展開し，その値を返す。"
        return self.__env[t]

    def unify(self, t, u):
        u"この環境で項 t, u を unify する。"
        return _unify(t, self.__env, u, self.__env, self.__trail, self.__env)


# 公開関数

def pair(x):
    u"x1,..,xN の列から，入れ子のペア (x1, (...(xN, None))) を作る。"
    x = list(x)
    x.reverse()
    return reduce(lambda a, b: (b, a), x, None)

def resolve(*goals):
    u"述語項 (の並び) を解決した変数束縛からなる環境をかえすジェネレータ"
    if __debug__:
        for t in goals:
            assert t is CUT or isinstance(t, _Goal)
    env = Env()
    for r in _resolve_body(pair(goals), env, [False]):
        yield env

def query(*goals):
    u"""述語項 (の並び) に対するすべての解を印字する便宜関数。
    解の通番 (失敗ならば 0) を，各解決結果の前につけて印字する。
    """
    g = (len(goals) == 1) and goals[0] or goals
    count = 0
    for env in resolve(*goals):
        count += 1
        print count, env[g]
    if count == 0:
        print 0, g

_trace = False
def trace(flag):
    u"flag が真ならば unify した結果を表示するようにする。"
    global _trace
    _trace = flag


# 処理系内部関数

def _resolve_body(body, env, cut):
    if body is None:
        yield None
    else:
        (goal, rest) = body
        if goal is CUT:
            for r in _resolve_body(rest, env, cut):
                yield None
            cut[0] = True
        else:
            d_env = Env()
            d_cut = [False]
            for (d_head, d_body) in goal.pred.defs():
                if d_cut[0] or cut[0]:
                    break
                trail = []
                if _unify_(goal, env, d_head, d_env, trail, d_env):
                    if callable(d_body):
                        if d_body(CallbackEnv(d_env, trail)):
                            for s in _resolve_body(rest, env, cut):
                                yield None
                    else:
                        for r in _resolve_body(d_body, d_env, d_cut):
                            for s in _resolve_body(rest, env, cut):
                                yield None
                            if cut[0]:
                                d_cut[0] = True
                for (x, x_env) in trail:
                    x_env.delete(x)
                d_env.clear()

def _unify_(x, x_env, y, y_env, trail, tmp_env):
    if _trace:
        lhs, rhs = str(x_env[x]), str(y)
    unified = _unify(x, x_env, y, y_env, trail, tmp_env)
    if _trace:
        print "\t", lhs, ((unified) and "~" or "!~"), rhs
    return unified

def _unify(x, x_env, y, y_env, trail, tmp_env):
    u"""x_env 下の x を y_env 下の y と unify する。バックトラックに備えて，
    その過程でおこなった変数束縛を trail に記録する。ただし，最適化のため
    tmp_env への束縛は記録しない。
    """
    while True:
        if isinstance(x, Var):
            xp = x_env.get(x)
            if xp is None:   #  x が未束縛ならば x を y の値に束縛する
                (y, y_env) = y_env.dereference(y)
                if not (x is y and x_env is y_env): # 自己代入チェック
                    x_env.put(x, (y, y_env))
                    if x_env is not tmp_env:
                        trail.append((x, x_env)) # 束縛を記録する
                return True
            else:               # X の束縛値を取り出す
                (x, x_env) = xp
                (x, x_env) = x_env.dereference(x)
        elif isinstance(y, Var):
            x, x_env, y, y_env = y, y_env, x, x_env
        else:
            break

    if isinstance(x, _Goal) and isinstance(y, _Goal):
        if x.pred is not y.pred:
            return False
        x, y = x.args, y.args
        assert isinstance(x, tuple) and isinstance(y, tuple)

    if ((isinstance(x, list) and isinstance(y, list)) or
        (isinstance(x, tuple) and isinstance(y, tuple))):
        if len(x) != len(y):
            return False
        for i in range(len(x)):
            if not _unify(x[i], x_env, y[i], y_env, trail, tmp_env):
                return False
        return True
    else:
        return x == y
# ----------------------------------------------------------------------
