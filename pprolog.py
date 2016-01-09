# -*- coding: utf-8 -*-

CUT = "!"


class Var:
    u"""変数 (vaiable)

    prologにおいては大文字から始まる。
    """
    def __init__(self, name):
        u"nameは repr()による表示にだけ使用される"
        self.name = name

    def __repr__(self):
        return self.name


class Pred:
    u"""述語 (predicate)
    関係性を示す。
    """
    def __init__(self, name):
        u"nameは repr()による表示にだけ使用される"
        self.name = name
        self.__defs = []

    def __repr__(self):
        return self.name

    def __call__(self, *args):
        u"述語項を構成する。"
        return _Goal(self, args)

    def defs(self):
        u"節 (head と body からなるタプル)からなるリスト"
        return self.__defs

    def add_def(self, head, body):
        u"節 (headとbody)を追加する"
        self.__defs.append((head, body))


class _Goal:
    u"述語項"
    def __init__(self, pred, args):
        assert isinstance(args, tuple)
        self.pred = pred
        self.args = args

    def __lshift__(self, rhs):
        u"""節を定義する。
        selfが節の頭部、rhsが節の本体となる。
        """
        if not isinstance(rhs, tuple):
            rhs = rhs
        if __debug__:
            for t in rhs:
                assert t is CUT or isinstance(t, _Goal)
        self.pred.add_def(self, pair(rhs))

    def __repr__(self):
        if len(self.args) == 1:
            return "%s(%r)" % (self.pred, self.args[0])
        else:
            return "%s%s" % (self.pred, self.args)


def pair(x):
    u"x1,...,xN の列から、入れ子のペア (x1, (...(xN, None))) を作る。"
    x = list(x)
    x.reverse()
    return reduce(lambda a, b: (b, a), x, None)


class Env:
    u"""環境 (environment"""
    def __init__(self):
        # {Var: (term, Env)}
        self.__table = {}

    def put(self, x, (t, env)):
        u"""変数xを、項tとその環境envのペアに束縛する。"""
        assert isinstance(x, Var)
        assert isinstance(env, Env)
        self.__table[x] = (t, env)

    def get(self, x):
        u"""変数xが束縛されているこうとその環境のペア。

        なければNoneを返す。
        """
        return self.__table.get(x)

    def delete(self, x):
        u"""変数xの束縛をとりけす。"""
        del self.__table[x]

    def clear(self):
        u"""束縛をすべて取り消す。"""
        self.__table.clear()

    def dereference(self, t):
        u"""非変数または非束縛の変数が得られるまで
        項tの値を参照する。
        得られた値とその環境ペアを返す。
        """
        env = self
        while isinstance(t, Var):
            p = env.get(t)
            if p is None:
                break
            (t, env) = p
        return (t, env)

    def __getitem__(self, t):
        u"""項tに含まれる変数を再帰的に出来る限り展開し、
        その値を返す。
        """
        (t, env) = self.dereference(t)
        if isinstance(t, _Goal):
            return _Goal(t.pred, env[t.args])
        elif isinstance(t, list):
            return [env[a] for a in t]
        elif isinstance(t, tuple):
            return tuple([env[a] for a in t])
        else:
            return t


def _unify(x, x_env, y, y_env, trail, tmp_env):
    u"""x_envの下のxをy_env下のyとunifyする。
    バックトラックに備えてその過程でおこなった変数束縛をtrailに記録する
    ただし、最適化のためtmp_envへの束縛は記録しない。
    """
    while True:
        if isinstance(x, Var):
            xp = x_env.get(x)
            # xが未束縛ならばxをyの値に束縛する
            if xp is None:
                (y, y_env) = y_env.dereference(y)
                #自己代入チェック
                if not (x is y and x_env is y_env):
                    x_env.put(x, (y, y_env))
                    if x_env is not tmp_env:
                        #束縛を記録する
                        trail.append((x, x_env))
                return True
           #xの束縛値を取り出す
            else:
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

    if ((isinstance(x, list) and isinstance(y, list))
            or (isinstance(x, tuple) and isinstance(y, tuple))):
        if len(x) != len(y):
            return False
        for i in range(len(x)):
            if not _unify(x[i], x_env, y[i], y_env, trail, tmp_env):
                return False
        return True
    else:
        return x == y


_trace = False
def trace(flag):
    u"flagが真ならばunifyした結果を表示するようにする。"
    global _trace
    _trace = flag


def _unify_(x, x_env, y, y_env, trail, tmp_env):
    if _trace:
        lhs, rhs = str(x_env[x]), str(y)
    unified = _unify(x, x_env, y, y_env, trail, tmp_env)
    if _trace:
        print "\t", lhs, ((unified) and "~" or "!~"), rhs
    return unified


def resolve(*goals):
    u"""述語項（の並び）を解決した変数束縛からなる環境を
    返すジェネレータ"""
    if __debug__:
        for t in goals:
            assert t is CUT or isinstance(t, _Goal)
    env = Env()
    for r in _resolve_body(pair(goals), env, [False]):
        yield env


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


def query(*goals):
    u"""述語項（の並び）に対するすべての解を印字する便宜関数。
    解の連番（失敗ならば0）を、各解決結果の前につけて印字する。
    """
    g = (len(goals) == 1) and goals[0] or goals
    count = 0
    for env in resolve(*goals):
        count += 1
        print count, env[g]
    if count == 0:
        print 0, g


def calls(self, callback):
    u"""コールバックを定義する。
    selfがunifyされた時、それに対するCallbackEnvインスタンス
    を引数として関数callbackが呼び出されるようにする。
    callbackはTrue（成功）かFalse（失敗）を返す。
    """
    assert callable(callback)
    self.pred.add_def(self, callback)


class CallbackEnv:
    u"""コールバック用の環境（実態は節の環境）"""
    def __init__(self, env, trail):
        self.__env = env
        self.__trail = trail

    def __getitem__(self, t):
        u"""項tに含まれる変数を再帰的にできる限り展開し、
        その値を返す。"""
        return self.__env[t]

    def unify(self, t, u):
        u"""この環境で項t, uをunifyする。"""
        return _unify(t, self.__env, u, self.__env, self.__trail, self.__env)
