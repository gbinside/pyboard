#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# 
# (c) Roberto Gambuzzi
# Creato:          30/04/2014 18:54:21
# Ultima Modifica: 30/04/2014 18:54:38
# 
# v 0.0.1.0
# 
# file: C:\Dropbox\coding dojo\tabellone dnd\board.py
# auth: Roberto Gambuzzi <gambuzzi@gmail.com>
# desc: 
# 
# $Id: board.py 30/04/2014 18:54:38 Roberto $
# --------------


def distance(coord1, coord2):
    return ((coord1[0] - coord2[0]) ** 2 + (coord1[1] - coord2[1]) ** 2) ** 0.5


def minc(coords):
    if coords:
        return min((x[0] for x in coords)), min((x[1] for x in coords))
    else:
        return 0


def maxc(coords):
    if coords:
        return max((x[0] for x in coords)), max((x[1] for x in coords))
    else:
        return 0


def plot(coords, char='*'):
    offset = minc(coords)
    plot_coords = []
    for x, y in coords:
        plot_coords.append((y - offset[1], x - offset[0]))
    plot_coords.sort()
    if plot_coords:
        py, px = 0, 0
    line = ''
    for y, x in plot_coords:
        if y != py:
            print line
            line = ''
            py = y
            px = 0
        if x > px:
            line += ' ' * (x - px)
        line += char
        px = x + 1
    print line


class Pawn(object):
    def __init__(self, name, team=None):
        self._name = name
        self._team = team

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def team(self):
        return self._team

    @team.setter
    def team(self, value):
        self._team = value

    def __add__(self, other):
        return self.name[0] + other

    def __radd__(self, other):
        return other + self.name[0]


class Board(object):
    def __init__(self):
        self._map = dict()

    def map(self, mapstring):
        for linenum, line in enumerate(mapstring.splitlines()):
            for x, char in enumerate(line):
                if char != ' ':
                    self._map[(x, linenum)] = char

    def topleft(self):
        return minc(self._map.keys())

    def bottomright(self):
        return maxc(self._map.keys())

    def reduce_positions(self):
        new_map = dict()
        offset = self.topleft()
        for k, v in self._map.items():
            new_map[(k[0] - offset[0], k[1] - offset[1])] = v
        self._map = new_map

    def put(self, x, y, obj_or_str):
        self._map[(x, y)] = obj_or_str

    def see(self, obj_or_x, y=None):  #@todo
        x = None
        if obj_or_x in self._map.values() and y is None:
            for k, v in self._map.items():
                if obj_or_x == v:
                    x, y = k
                    break
        else:
            x = obj_or_x
            assert y is not None
        assert x is not None
        obj = self._map[(x, y)]
        for (x2, y2), v in self._map.items():
            if v == obj:
                continue
                #print x2 - x, y2 - y

    def moves(self, coords, steps, halfstep=False, previous_steps=None, team=None):
        if steps < 1:
            return []
        object_passed = None
        if isinstance(coords, Pawn):
            for k, v in self._map.items():
                if coords == v:
                    object_passed = coords
                    team = object_passed.team
                    coords = k
                    break
        if previous_steps is None:
            previous_steps = []
        x, y = coords
        step = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        if halfstep:
            step.append((x + 1, y + 1))
            step.append((x - 1, y - 1))
            step.append((x - 1, y + 1))
            step.append((x + 1, y - 1))
        # non torniamo sui nostri passi, altrimenti l'algoritmo ci mette una vita
        step = [e for e in step if e not in previous_steps]
        # passaggio per caselle occupate da amici
        if steps > 1 and team:
            step = [e for e in step if e not in self._map or (
                isinstance(self._map[e], Pawn) and self._map[e].team == team)]
        else:  # se manca 1 solo passo non si puo sostare nemmeno nelle caselle occupate da amici
            step = [e for e in step if e not in self._map]
        ret = []
        for e in step:
            ret.extend(self.moves(e, steps - 1, not halfstep, previous_steps + step, team))
        return set(ret + step)

    def _find_obj_coord(self, obj):
        coords = None
        for k, v in self._map.items():
            if obj == v:
                coords = k
                break
        return coords

    def move(self, obj, x, y, absolute=False):
        coords = self._find_obj_coord(obj)
        assert coords is not None
        if not absolute:
            x += coords[0]
            y += coords[1]
        assert (x, y) not in self._map
        self._map[(x, y)] = obj
        del self._map[coords]

    def obj_to_coord(self, obj_or_coord):
        if isinstance(obj_or_coord, Pawn):
            c = self._find_obj_coord(obj_or_coord)
        else:
            c = obj_or_coord
        return c

    def cover(self, obj_or_coord1, obj_or_coord2):
        ret = 0.0
        l1 = self.between(obj_or_coord1, obj_or_coord2, (0, 0))
        l2 = self.between(obj_or_coord1, obj_or_coord2, (1, 0))
        l3 = self.between(obj_or_coord1, obj_or_coord2, (0, 1))
        l4 = self.between(obj_or_coord1, obj_or_coord2, (1, 1))

        for l in (l1, l2, l3, l4):
            if l:
                if l[0][0] == obj_or_coord1:
                    l.pop(0)
                if l[-1][0] == obj_or_coord2:
                    l.pop()
            if l:
                ret += 0.25
        return ret

    def between(self, obj_or_coord1, obj_or_coord2, offset=(0.5, 0.5), fillchar=None):
        c1 = self.obj_to_coord(obj_or_coord1)
        c2 = self.obj_to_coord(obj_or_coord2)
        x1, y1 = (float(i) for i in c1)
        x2, y2 = (float(i) for i in c2)
        x1 += offset[0]
        x2 += offset[0]
        y1 += offset[1]
        y2 += offset[1]
        dx = x2 - x1
        dy = y2 - y1
        steps = int(max(dx, dy))
        stepx = dx / steps
        stepy = dy / steps
        ret = []
        for s in xrange(steps + 1):
            x, y = int(x1 + s * stepx), int(y1 + s * stepy)
            if (x, y) in self._map:
                ret.append((self._map[(x, y)], (x, y),))
            elif fillchar is not None:
                self._map[(x, y)] = fillchar
        return ret

    def contapassi(self, obj_or_coord_from, obj_or_coord_to, limit=255):
        """absolute coords or Pawns"""
        if isinstance(obj_or_coord_to, Pawn):
            _to = self._find_obj_coord(obj_or_coord_to)
            return min(x for x in (self.contapassi(obj_or_coord_from, (_to[0] - 1, _to[1])),
                                   self.contapassi(obj_or_coord_from, (_to[0], _to[1] + 1)),
                                   self.contapassi(obj_or_coord_from, (_to[0], _to[1] - 1)),
                                   self.contapassi(obj_or_coord_from, (_to[0] + 1, _to[1]))
            ) if x) + 1
        else:
            _to = obj_or_coord_to
        _from = self.obj_to_coord(obj_or_coord_from)
        ret = int(((_from[0] - _to[0]) ** 2 + (_from[1] - _to[1]) ** 2) ** 0.5) - 1
        passi = ()
        plen = 0
        while _to not in passi and ret < limit:
            ret += 1
            passi = self.moves(obj_or_coord_from, ret)
            if plen == len(passi):
                break
            plen = len(passi)
        if _to not in passi:
            ret = None
        return ret

    def plot(self, steps_dict=None, _print=True):
        coords = self._map.keys()
        offset = minc(coords)
        plot_coords = []
        steps_map = {}
        for x, y in coords:
            plot_coords.append((y - offset[1], x - offset[0]))
        if steps_dict:
            steps_list = steps_dict.items()
            steps_list.sort(key=lambda item: -len(item[1]))
            for k, steps in steps_list:
                for x, y in steps:
                    c = (y - offset[1], x - offset[0])
                    steps_map[c[::-1]] = k
        plot_coords.extend((x[::-1] for x in steps_map.keys()))
        plot_coords = list(set(plot_coords))
        plot_coords.sort()

        py, px = 0, 0
        ret = ''
        line = ''
        for y, x in plot_coords:
            if y != py:
                ret += line + '\r\n'
                line = ''
                py = y
                px = 0
            if x > px:
                line += ' ' * (x - px)
            try:
                line += self._map[(x + offset[0], y + offset[1])]
            except KeyError, e:
                if (x, y) in steps_map:
                    line += steps_map[(x, y)]
                else:
                    raise e
            px = x + 1
        ret += line + '\r\n'
        if _print:
            print ret
        return ret

    def __str__(self):
        return self.plot(_print=False)


#  _____ ___ ___ _____
# |_   _| __/ __|_   _|
#   | | | _|\__ \ | |
#   |_| |___|___/ |_|


def test1():
    b = Board()

    b.map("""
    **************************
    *                 *      *
    *                 D      *
    ***D************  *      *
          *        *  ********
          *        *  *      *
          *        *  *      *
          *        S  *      *
          *        *  *      *
          **D*******  D      *
          *           *      *
          *           *      *
          ********************
    """)
    assert b.topleft() == (4, 1)
    b.reduce_positions()
    assert b.topleft() == (0, 0)
    assert b.bottomright() == (25, 12)


def test2():
    b = Board()

    b.map("""
    **************************
    *                 *      *
    *                 D      *
    ***D************  *      *
          *        *  ********
          *        *   *   * *
          *        *     *   *
          *        S  ********
          *        *  *      *
          **D*******  D      *
          *           *      *
          *           *      *
          ********************
    """)
    b.reduce_positions()
    p1 = Pawn('1Player1')
    b.put(1, 1, p1)
    p2 = Pawn('2Player2')
    b.put(1, 2, p2)

    assert {(2, 1)} == b.moves((1, 1), 1)
    assert {(3, 2), (3, 1), (2, 1), (2, 2)} == b.moves((1, 1), 2)
    assert len(b.moves((1, 1), 1)) == 1
    assert len(b.moves(p1, 2)) == 4
    assert len(b.moves((1, 1), 25)) == 64


def test_plot():
    b = Board()

    b.map("""
    **************************
    *                 *      *
    *                 D      *
    ****************  *      *
          *        *  ********
          *        *   *   * *
          *        *     *   *
          *        S  ********
          *        *  *      *
          **D*******  D      *
          *           *      *
          *           *      *
          ********************
    """)
    b.plot()
    print '-' * 79
    b.reduce_positions()
    p1 = Pawn('1Player1', 1)
    b.put(1, 1, p1)
    p2 = Pawn('2Player2', 1)
    b.put(1, 2, p2)
    p3 = Pawn('3Player3', 1)
    b.put(3, 2, p3)
    p4 = Pawn('4Player4', 1)
    b.put(3, 1, p4)
    enemy = Pawn('Enemy')
    b.put(16, 4, enemy)

    b.plot({'.': b.moves(p4, 18), 'o': b.moves(p4, 9)})
    print '-' * 79
    assert len(b.moves(p1, 9)) == 20
    b.plot({'.': b.moves(p1, 18), 'o': b.moves(p1, 9)})

    b.move(p1, +8, 0)
    print '-' * 79
    b.plot({'.': b.moves(p1, 10), 'o': b.moves(p1, 1)})

    assert b.contapassi(p1, (17, 4)) == 9
    assert b.contapassi(enemy, (17, 4)) == 1
    assert b.contapassi(p1, enemy) == 9


def test_see():
    b = Board()

    b.map("""
    **************************
    *                 *      *
    *                 D      *
    ****************  *      *
          *        *  ********
          *        *   *   * *
          *        *     *   *
          *        S  ********
          *        *  *      *
          **D*******  D      *
          *           *      *
          *           *      *
          ********************
    """)
    b.reduce_positions()
    p1 = Pawn('1Player1', 1)
    b.put(9, 1, p1)
    p2 = Pawn('2Player2', 1)
    b.put(1, 2, p2)
    p3 = Pawn('3Player3', 1)
    b.put(3, 2, p3)
    p4 = Pawn('4Player4', 1)
    b.put(3, 1, p4)
    enemy = Pawn('Enemy', 2)
    b.put(16, 3, enemy)
    enemy2 = Pawn('Enemy2', 2)
    b.put(17, 4, enemy2)

    assert '*' in (x[0] for x in b.between(p1, enemy))
    assert '*' in (x[0] for x in b.between(p1, enemy2))
    b.move(p1, +4, 0)
    assert enemy in (x[0] for x in b.between(p1, enemy2))
    assert '*' in (x[0] for x in b.between(p1, enemy2))

    b.move(p1, -4, 0)
    assert int(b.cover(p1, enemy) * 10) == 5
    assert int(b.cover(p1, enemy2) * 10) == 10
    assert ('*', (15, 3)) in b.between(p1, enemy)
    b.plot()


def test_ememy_and_steps():
    b = Board()

    b.map("""
    **************************
    *                 *      *
    *                 D      *
    ****************  *      *
          *        *  ********
          *        *   *   * *
          *        *     *   *
          *        S  ********
          *        *  *      *
          **D*******  D      *
          *           *      *
          *           *      *
          ********************
    """)
    b.plot()
    print '-' * 79
    b.reduce_positions()
    p1 = Pawn('1Player1', 1)
    b.put(1, 1, p1)
    p2 = Pawn('2Player2', 1)
    b.put(1, 2, p2)
    p3 = Pawn('3Player3', 1)
    b.put(3, 2, p3)
    p4 = Pawn('4Player4', 1)
    b.put(3, 1, p4)
    enemy = Pawn('Enemy', 2)
    b.put(16, 4, enemy)
    enemy2 = Pawn('Enemy2', 2)
    b.put(17, 4, enemy2)

    b.plot({'.': b.moves(p4, 18), 'o': b.moves(p4, 9)})
    print '-' * 79
    assert len(b.moves(p1, 9)) == 20
    b.plot({'.': b.moves(p1, 18), 'o': b.moves(p1, 9)})

    b.move(p1, +8, 0)
    print '-' * 79
    b.plot({'.': b.moves(p1, 10), 'o': b.moves(p1, 1)})

    assert b.contapassi(p1, (17, 3)) == 8
    assert b.contapassi(p1, enemy) == 9


def main(argv):
    import inspect

    my_name = inspect.stack()[0][3]
    for f in argv:
        globals()[f]()
    if not argv:
        fs = [globals()[x] for x in globals() if
              inspect.isfunction(globals()[x]) and x.startswith('test') and x != my_name]
        for f in fs:
            print f.__name__
            f()


if __name__ == "__main__":
    import sys

    main(sys.argv[1:])
