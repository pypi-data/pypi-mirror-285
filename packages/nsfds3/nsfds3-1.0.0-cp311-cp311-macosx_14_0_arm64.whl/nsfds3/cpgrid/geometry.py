#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright © 2016-2023 Cyril Desjouy <cyril.desjouy@univ-lemans.fr>
#
# This file is part of nsfds3
#
# nsfds3 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# nsfds3 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with nsfds3. If not, see <http://www.gnu.org/licenses/>.
#
# Creation Date : 2023-04-06 - 09:45:13
"""
The `geometry` module provides objects to describe elements of geometry :

    * :py:class:`Obstacle` : describes an obstacle with its faces
    * :py:class:`Domain` : describes a portion of the computation domain
    * :py:class:`ObstacleSet` : Collection of Obstacle objects
    * :py:class:`DomainSet` : Collection of Domain objects
"""

import warnings
import itertools
import functools
import numpy


class Box:
    """Elementary object to describe Cuboids or Faces."""

    _axnames = 'x', 'y', 'z'

    def __init__(self, origin, size, env, bc=None, inner=False, tag=None):

        self.origin = origin
        self.size = size
        self.bc = bc
        self.env = env
        self.inner = inner
        self.tag = tag
        self.ndim = len(origin)

        self._set_bc()
        self._check_args()
        self._set_rn()
        self._set_sn()
        self._set_cn()
        self._set_rin()
        self._set_sin()

        self.vertices = self._get_vertices()
        m = itertools.product(*[(s, range(s.start, s.start + 1), range(s.stop - 1, s.stop)) for s in self.rn])
        self.edges = tuple(set([s for s in m if [len(c) for c in s].count(1) == self.ndim - 1]))

    @classmethod
    def from_slices(cls, slices, env, bc=None, inner=False, tag=None):
        """Instanciate Box from a list of slices."""
        origin = tuple(s.start for s in slices)
        size = tuple(s.stop - s.start for s in slices)
        return cls(origin=origin, size=size, env=env, bc=bc, inner=inner, tag=tag)

    @functools.cached_property
    def indices(self):
        """Return a set of all indexes contained in the Box."""
        return set(itertools.product(*self.rn))

    def _get_vertices(self):
        vertices = self.sort_vertices([tuple(i) for i in itertools.product(*self.cn)])
        return numpy.array(vertices, dtype=numpy.int16).T

    @staticmethod
    def sort_vertices(values):
        """Sort vertices."""
        sort = [values[0], ]
        vertices = values[1:]

        n = 0
        while len(vertices):
            for v in vertices:
                if numpy.count_nonzero((numpy.array(v)
                                      - numpy.array(sort[-1])) == 0) == len(values[0]) - 1:
                    sort.append(v)
                    vertices.remove(v)
                    break
            n += 1
            if n > len(values)**2:
                sort = values[:]
                break
        # append first value to the end to be able to plot all contour...
        sort.append(sort[0])
        return sort

    @staticmethod
    def _fix_vertices(values):
        """Fix flat cuboids."""
        axis = numpy.where([v.min() == v.max() for v in values])[0]
        if axis.any():
            axis = axis[0]
            if axis == 0:
                idx = (4, 5, 6, 7)
            elif axis == 1:
                idx = (2, 3, 6, 7)
            elif axis == 2:
                idx = (1, 3, 5, 7)
            values = values.astype('float64')
            values[axis] = [v + 0.1 if i in idx else v
                                    for i, v in enumerate(values[axis])]
        return values

    def slice_from_edge(self, edge):
        s = tuple()
        for i, r in enumerate(edge):
            if len(r) == 1:
                if i == self.axis:
                    s += (r.start, )
                elif self.cn[i][0] == r.start:
                    s += (r.start if r.start == 0 else r.start + 1, )
                elif self.cn[i][1] == r.start:
                    s += (r.start if r.stop == self.env[i] else r.start - 1, )
            else:
                s += (slice(r.start if r.start == 0 else r.start + 1, r.stop if r.stop == self.env[i] else r.stop - 1), )
        return s

    def inner_slices(self, ax=None):
        """Return inner slices except along axis (int)."""
        sn = list(self.sin)
        if ax is not None:
            sn[ax] = self.sn[ax]
        return tuple(sn)

    def inner_indices(self, ax=None):
        """Return indices. inner points except along axis (int)"""
        rn = list(self.rin)
        if ax is not None:
            rn[ax] = self.rn[ax]
        return set(itertools.product(*rn))

    def center(self, transform=None, ax=None):
        """Return physical coordinates of the center of the box along ax."""
        if isinstance(transform, (tuple, list)) and isinstance(ax, (tuple, list)):
            start = tuple(c[0] for i, c in enumerate(self.cn) if i in ax)
            stop = tuple(c[1] for i, c in enumerate(self.cn) if i in ax)
            center = tuple((a[stop] + a[start]) / 2 for a in transform)
        else:
            center = tuple((c[1] + c[0]) / 2 for c in self.cn)
            if isinstance(ax, (tuple, list)):
                center = tuple(c for i, c in enumerate(center) if i in ax)

        return center

    def intersection(self, other):
        """Return intersection (point coordinate) between self and other."""
        c = [set(rs).intersection(ro) for rs, ro in zip(self.rn, other.rn)]
        return tuple(itertools.product(*c))

    def intersects(self, other):
        """Report whether self intersects other."""
        for s, o in zip(self.cn, other.cn):
            if s[1] < o[0] or s[0] > o[1]:
                return False
        return True

    def issubset(self, other):
        """Report whether other contains self."""
        out = []
        for s, o in zip(self.rn, other.rn):
            out.append(set(s).issubset(o))
        return all(tuple(out))

    def issuperset(self, other):
        """Report whether self contains other."""
        out = []
        for s, o in zip(self.rn, other.rn):
            out.append(set(s).issuperset(o))
        return all(tuple(out))

    def contains(self, coordinate):
        """Report whether coordinate is in self."""
        return all(c in r for c, r in zip(coordinate, self.rn))

    def _check_args(self):
        """Check input arguments."""
        if any(len(self.bc) != 2 * len(s) for s in [self.origin, self.size, self.env]):
            raise ValueError('origin, size, env and bc must have coherent dimensions')

        if any(s == 0 for s in self.size):
            raise ValueError('Size of the object must be at least 1')

        if any(self.origin[i] < 0 for i in range(self.ndim)) or \
           any(self.origin[i] + self.size[i] - 1 > self.env[i] - 1 for i in range(self.ndim)):
            raise ValueError('Object must be into the domain')

    def _set_bc(self):
        """Set bc. Will be len(origin) * 'W' by default."""
        self.bc = '..' * self.ndim if not self.bc else self.bc.upper()

    def _set_rn(self):
        """Set ranges (rx, ry [, rz])."""
        self.rn = ()
        for n, i in zip(self._axnames, range(self.ndim)):
            setattr(self, f'r{n}', range(self.origin[i], self.origin[i] + self.size[i]))
            self.rn += (getattr(self, f'r{n}'), )

    def _set_rin(self):
        """Set inner ranges (rix, riy [, riz])."""
        self.rin = ()
        for n, i in zip(self._axnames, range(self.ndim)):
            if self.size[i] <= 1:
                setattr(self, f'ri{n}', range(self.origin[i], self.origin[i] + self.size[i]))
            else:
                setattr(self, f'ri{n}', range(self.origin[i] + 1, self.origin[i] + self.size[i] - 1))
            self.rin += (getattr(self, f'ri{n}'), )

    def _set_sn(self):
        """Set slices (sx, sy [, sz])."""
        self.sn = ()
        for n, i in zip(self._axnames, range(self.ndim)):
            setattr(self, f's{n}', slice(self.origin[i], self.origin[i] + self.size[i]))
            self.sn += (getattr(self, f's{n}'), )

    def _set_sin(self):
        """Set inner slices (six, siy [, siz])."""
        self.sin = ()
        for n, i in zip(self._axnames, range(self.ndim)):
            if self.size[i] <= 1:
                setattr(self, f'si{n}', slice(self.origin[i], self.origin[i] + self.size[i]))
            else:
                setattr(self, f'si{n}', slice(self.origin[i] + 1, self.origin[i] + self.size[i] - 1))
            self.sin += (getattr(self, f'si{n}'), )

    def _set_cn(self):
        """Set coordinates (cx, cy [, cz])."""
        self.cn = ()
        for n, r in zip(self._axnames, self.rn):
            setattr(self, f'c{n}', (r[0], r[-1]))
            self.cn += (getattr(self, f'c{n}'), )

    def __contains__(self, other):
        return other.issubset(self)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            raise ValueError(f'Can only compare {type(self).__name__} together')
        attrs = ['origin', 'size', 'env', 'bc', 'inner', 'tag']
        return all(getattr(self, attr, None) == getattr(other, attr, None) for attr in attrs)

    def __hash__(self):
        """Mandatory because of the definition of __eq__. If not, self is not hashable."""
        return id(self)

    def __fargs__(self):
        return f"origin={self.origin}, size={self.size}, bc={self.bc}"

    def __str__(self):
        """Custom __str__ following dataclass style."""
        if getattr(self, '__fargs__', None):
            return f"{type(self).__name__}({self.__fargs__()})"

        return f"{type(self).__name__}"

    def __repr__(self):
        return self.__str__()


class Cuboid(Box):
    """Specialization of Box objects to describe a cuboid and its faces.
        See :py:class:`nsfds3.cpgrid.geometry.Box` for further details."""

    count = 0

    @classmethod
    def count_reset(cls):
        """Reset the count."""
        cls.count = 0

    def __init__(self, origin, size, env, bc=None, inner=False, tag=None):

        super().__init__(origin, size, env, bc=bc, inner=inner, tag=tag)

        self.sid = self.__class__.count
        self.__class__.count += 1

        self.face_left = Face(self, side='left')
        self.face_right = Face(self, side='right')
        self.face_front = Face(self, side='front')
        self.face_back = Face(self, side='back')
        self.faces = (self.face_left, self.face_right,
                      self.face_front, self.face_back)

        if self.ndim == 3:
            self.face_bottom = Face(self, side='bottom')
            self.face_top = Face(self, side='top')
            self.faces += (self.face_bottom, self.face_top)

    @property
    def description(self):
        """Return a brief description of the object."""
        attributes = dict(clamped='c', bounded='b',
                          free='f', colinear='I',
                          overlapped='o', covered='0',
                          periodic='p')

        chars = [''.join([attributes[c] for c in attributes.keys() if getattr(f, c)])
                 for f in self.faces]
        return '/'.join(chars)

    def flatten(self, axis):
        """Return a flat version of the object."""
        cls = type(self)
        if self.ndim == 2:
            warnings.warn(f'{cls.__name__} already flat')
            return None

        origin = tuple(o for i, o in enumerate(self.origin) if i != axis)
        size = tuple(s for i, s in enumerate(self.size) if i != axis)
        env = tuple(s for i, s in enumerate(self.env) if i != axis)
        bc = ''.join([v for i, v in enumerate(self.bc) if i not in [2*axis, 2*axis + 1]])
        obj = cls(origin, size, env=env, bc=bc)
        if "V" in obj.bc:
            for face in [f for f in obj.faces if f.bc == 'V']:
                old_face = getattr(self, f'face_{face.side}')
                face.set_source(old_face.source_function, old_face.source_profile)

        return obj

#    def __eq__(self, other):
#        equal_boxes = super().__eq__(other)
#        equal_faces = all(f1 == f2 for f1, f2 in zip(self, other))
#        return equal_boxes and equal_faces

    def __iter__(self):
        return iter(self.faces)

    def __fargs__(self):
        return f"origin={self.origin}, size={self.size}, bc={self.bc}, sid={self.sid}"


class Obstacle(Cuboid):
    """Specialization of Cuboid objects to describe an Obstacle.
        See :py:class:`nsfds3.cpgrid.geometry.Box` and :py:class:`nsfds3.cpgrid.geometry.Cuboid` for further details."""


class Bounds(Cuboid):
    """Specialization of Cuboid objects to describe a global domain.
        See :py:class:`nsfds3.cpgrid.geometry.Box` and :py:class:`nsfds3.cpgrid.geometry.Cuboid` for further details."""


class Domain(Cuboid):
    """Specialization of Cuboid objects to describe a portion of the computation domain.
        See :py:class:`nsfds3.cpgrid.geometry.Box` and :py:class:`nsfds3.cpgrid.geometry.Cuboid` for further details."""

    def __init__(self, origin, size, env, bc=None, inner=False, tag=None, axis=None):

        super().__init__(origin, size, env, bc=bc, inner=inner, tag=tag)
        self.axis = axis

    @property
    def scm_code(self):
        if self.tag == 'P':
            return 0
        elif self.tag == 'p':
            return 5
        elif self.tag == 'm':
            return -5
        return 11

    def __fargs__(self):
        return f"origin={self.origin}, size={self.size}, bc={self.bc}, sid={self.sid}, tag={self.tag} ({self.scm_code}), axis={self.axis}"


class Face(Box):
    """Specialization of Box objects to describe a face.
        See :py:class:`nsfds3.cpgrid.geometry.Box` for further details."""

    _sides = {'right': (0, 1, 1), 'left': (0, -1, 0),    # (axis, normal, idx)
              'back': (1, 1, 3), 'front': (1, -1, 2),
              'top': (2, 1, 5), 'bottom': (2, -1, 4)}

    _opposites = {'right': 'left', 'left': 'right',
                  'back': 'front', 'front': 'back',
                  'top': 'bottom', 'bottom': 'top'}

    _attributes = ['clamped', 'bounded', 'free', 'colinear', 'overlapped', 'covered', 'periodic']

    def __init__(self, parent, side):

        self.parent = parent
        self.side = side
        self.opposite = self._opposites[side]
        self.axis, self.normal, self.index = self._sides[side]
        self.not_axis = tuple(set(range(parent.ndim)).difference((self.axis, )))

        origin = tuple(c[1] if i == self.axis and self.normal == 1 else c[0] for i, c in enumerate(parent.cn))
        size = tuple(1 if i == self.axis else s for i, s in enumerate(parent.size))

        super().__init__(origin, size, parent.env, bc=self.bc, inner=parent.inner)

        self.sid = parent.sid
        self.loc = self.cn[self.axis][0]
        if self.inner:
            self.normal = - self.normal

        self.clamped = False
        self.periodic = False
        self.bounded = False
        self.covered = []
        self.colinear = []
        self.overlapped = []
        self.uncentered = set()

    def set_source(self, func, profile='tukey', alpha=0.9):
        """Setup a wall source.

        Parameters
        ----------
        func : function
            Function that takes the time axis t as input arguments, which is calculated as follows::

                import numpy as np
                t = np.linspace(0, nt * dt, nt + 1)

            where nt is the number of time iterations and dt the timestep. set_source must return a
            1d ndarray containing nt + 1 points that describe the time evolution of the wall source.
        profile : str, 'tukey' by default.
            Spacial profile. must be "sine" or "tukey".
        """
        if not callable(func):
            raise ValueError('func must be callable')

        self.source_evolution = numpy.array([])
        self.source_function = func
        self.source_name = func.__name__
        self.source_alpha = alpha

        if profile.lower() not in ['sine', 'tukey']:
            self.source_profile = 'tukey'
        else:
            self.source_profile = profile.lower()

    @property
    def bc(self):
        return self.parent.bc[self.index]

    @bc.setter
    def bc(self, value):
        self.parent.bc = ''.join(value if i == self.index else s
                                 for i, s in enumerate(self.parent.bc))

    @property
    def free(self):
        """Report whether the face is free or not."""
        return all(not getattr(self, attr) for attr in self._attributes if attr != 'free')

    @property
    def description(self):
        """Return a brief description of the object."""
        return '/'.join([c for c in self._attributes if getattr(self, c)])

    def _check_args(self):
        """Check input arguments.

        Note
        ----

        Overload _check_args from Box to impose bc to be 1-character string.
        """

        if any(len(self.size) != len(s) for s in [self.origin, self.env]):
            raise ValueError('origin, size, and env must have the same dimension')

        if len(self.bc) != 1:
            raise ValueError('bc must be a 1-character str')

        if any(s <= 0 for s in self.size):
            raise ValueError('Size of the object must be at least 1')

    @property
    @functools.lru_cache()
    def base_slice(self):
        if self.inner:
            return self.sn
        return tuple(slice(s.start - self.normal, s.stop - self.normal) if i == self.axis
                        else s for i, s in enumerate(self.sn))

    def corner_slices(self, corner):
        """Return inner slice taking account a corner."""
        sin = tuple()
        for i, (c, s) in enumerate(zip(corner, self.size)):
            if i == self.axis:
                sin += (self.sin[self.axis], )
            elif s == self.env[i] - 1:
                sin += (slice(0, self.env[i]), )
            elif c == 0:
                sin += (slice(0, s - 1), )
            else:
                sin += (slice(c + 2 - s, c + 1), )
        return sin

    def box(self, N=5):
        """Return a box extending N points ahead of the object."""

        if self.normal == -1:
            origin = [r.start - N + 1 if self.axis == i else r.start
                            for i, r in enumerate(self.rn)]
        else:
            origin = list(self.origin)

        if self.periodic:
            if self.normal == - 1:
                origin[self.axis] = self.env[self.axis] - N
            elif self.normal == 1:
                origin[self.axis] = 0

        origin = tuple(origin)
        size = tuple(N if i == self.axis else s for i, s in enumerate(self.size))
        bc = ['X'] * len(self.origin) * 2
        bc[self._sides[self.opposite][2]] = self.bc   #  BC Wrong ?

        return Box(origin=origin, size=size, env=self.env, bc=''.join(bc))

#    def __eq__(self, other):
#        if not isinstance(other, type(self)):
#            raise ValueError(f'Can only compare {type(self).__name__} together')
#        attrs = ['origin', 'size', 'env', 'bc', 'inner',
#                 'source_profile', 'source_alpha', 'source_name']
#        return all(getattr(self, attr, None) == getattr(other, attr, None) for attr in attrs)

    def intersects(self, other):
        """Report whether self intersects other."""
        if self.loc not in other.rn[self.axis]:
            return False
        return super().intersects(other)

    def issubset(self, other):
        """Report whether other contains self."""
        if self.loc not in other.rn[self.axis]:
            return False
        return super().issubset(other)

    def is_likely_to_interfere_with(self, other):
        if self.side != other.opposite:
            return False
        if self.covered or other.covered:
            return False
        if self.clamped or other.clamped:
            return False
        if self.periodic or other.periodic:
            return False
        if self.loc * self.normal + other.loc * other.normal >= 0:
            return False
        return all(set(self.rn[ax]).intersection(other.rn[ax]) for ax in self.not_axis)

    def __fargs__(self):

        s = f"origin={self.origin}, size={self.size}, "
        s += f"bc={self.bc}, side={self.side}, sid={self.sid}, [{self.description}]"

        return s

    def __getstate__(self):
        """
        Note
        ----
        can't picke external function, so delete it from instance...
        """
        attributes = self.__dict__.copy()
        if hasattr(self, 'source_function'):
            del attributes['source_function']
        return attributes


class BoxSet:
    """Elementary object to describe a collection of Cuboids."""

    def __init__(self, shape, bc, subs=None, stencil=11):

        self.shape = shape
        self.ndim = len(shape)
        self.bc = bc
        self.subs = subs if subs else []
        self.stencil = stencil

        self.faces = tuple(itertools.chain(*[sub.faces for sub in subs]))
        self.corners = tuple(itertools.product(*zip((0, ) * len(shape), tuple(s - 1 for s in shape))))
        self.bounds = Bounds(origin=(0, ) * len(shape), size=shape, env=shape, bc=self.bc, inner=True)
        self.sids = {obs.sid:obs for obs in self.subs}

    def get_sub_by_coordinate(self, c):
        """Return subdomain containing point of coordinates c."""
        subs = []
        for s in self:
            if s.contains(c):
                subs.append(s)
        return subs

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            raise ValueError(f'Can only compare {type(self).__name__} together')
        return all(o1 == o2 for o1, o2 in zip(self, other))

    def __getitem__(self, n):
        return self.subs[n]

    def __iter__(self):
        return iter(self.subs)

    def __len__(self):
        return len(self.subs)

    def __add__(self, other):
        if self.stencil != other.stencil or self.shape != other.shape or self.bc != other.bc:
            raise ValueError(f'{type(self)} not compatible')
        return type(self)(shape=self.shape, bc=self.bc, subs=self.subs + other.subs, stencil=self.stencil)

    def __fargs__(self):
        s = f'shape={self.shape} -- {len(self)} elements:'
        for edge in self.subs:
            s += f'\n\t- {edge}'
        return s

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        """Custom __str__ following dataclass style."""
        if getattr(self, '__fargs__', None):
            return f"{type(self).__name__}({self.__fargs__()})"

        return f"{type(self).__name__}"

    def __fargs__(self):
        s = f'shape={self.shape} -- {len(self)} elements:'
        for edge in self.subs:
            s += f'\n\t- {edge}'
        return s


class DomainSet(BoxSet):
    """Specialization of BoxSet objects to describe a collection of Domain objects.
        See :py:class:`nsfds3.cpgrid.geometry.BoxSet` for further details.
    """

    def __init__(self, shape, bc, subs=None, stencil=11):

        super().__init__(shape, bc=bc, subs=subs, stencil=stencil)

        if len(shape) == 3:    # outer/inner for 3d visualization
            self.outer = []
            for bound in self.bounds.faces:
                for face in [f for f in self.faces if f.loc == bound.loc and f.side == bound.side]:
                    if face.parent.tag in ('p', 'm') and face.parent.axis == bound.axis:
                        self.outer.append(face.parent)
            self.inner = [o for o in self if o not in self.outer]


    def __add__(self, other):
        """Override BoxSet.__add__."""
        if self.stencil != other.stencil or self.shape != other.shape or self.bc != other.bc:
            raise ValueError(f'{type(self)} not compatible')
        return type(self)(shape=self.shape, bc=self.bc, subs=self.subs + other.subs, stencil=self.stencil)


class ObstacleSet(BoxSet):
    """Specialization of BoxSet objects to describe a collection of Obstacle objects.
        See :py:class:`nsfds3.cpgrid.geometry.BoxSet` for further details.

        Note
        ----
        ObstacleSet provides several useful sequences of faces :

            - overlapped_cuboids : cuboids that overlap
            - overlapped : faces that are partially overlapped by an obstacle
            - periodic : faces located on a periodic boundary of the domain
            - colinear : faces that are colinear with other obstacle faces
            - covered : faces that are entirely covered by an obstacle
            - clamped : faces located on a boundary (not periodic) of the domain
            - bounded : faces that are bounded by at least one boundary of the domain
            - edged : faces that are located on a boundary of the domain and bounded by at least another one
            - free : free face
            - uncentered : faces that need an uncentered scheme
    """

    def __init__(self, shape, bc, subs=None, stencil=11):

        super().__init__(shape, bc=bc, subs=subs, stencil=stencil)

        self._update_face_description()

        self.periodic = tuple(f for f in self.faces if f.periodic)
        self.colinear = tuple(f for f in self.faces if f.colinear)
        self.covered = tuple(f for f in self.faces if f.covered)
        self.overlapped = tuple(f for f in self.faces if f.overlapped)
        self.clamped = tuple(f for f in self.faces if f.clamped)
        self.bounded = tuple(f for f in self.faces if f.bounded)
        self.edged = tuple(f for f in self.faces if f.clamped and f.bounded)
        self.free = tuple(f for f in self.faces if f.free)
        self.uncentered = tuple(f for f in self.faces if not f.clamped and not f.covered)

        if self.subs:
            self.check_boxes()
            self.check_collision()

    def check_boxes(self):
        """Check that :
            - all boxes have same dimension and envelop,
            - there is not collision between obstacles and bounds
        """
        if not len(set([s.env for s in self])) == 1:
            raise ValueError('All boxes must have same envelop')

        if not len(set([s.ndim for s in self])) == 1:
            raise ValueError('All boxes must have same number of dimensions')

        for obs in self:
            if self.is_out_of_bounds(obs):
                raise ValueError(f'{obs} is out of bounds')

    def check_collision(self):
        """Warn if obstacles interfere."""
        # Check collision
        n = int(self.stencil // 2)
        for obs in self:
            obs.extended_cn = tuple((max(0, obs.cn[ax][0] - n), 
                                     min(size - 1, obs.cn[ax][1] + n)) for size, ax in zip(obs.env, range(obs.ndim)))

        # Obstacles that are likely to interfere
        combs = [(o1, o2) for o1, o2 in itertools.combinations(self, r=2) \
            if self.is_extended_overlap(o1, o2) and not o1.intersects(o2)]

        # Warn for obstacles that are too close
        for o1, o2 in combs:
            for f1, f2 in itertools.product(o1.faces, o2.faces):
                if f1.is_likely_to_interfere_with(f2):
                    warnings.warn(f'{o1} and {o2} too close')
                    break

        # Warn for obstacles that are too close to bounds
        for obs in self:
            if any(0 < obs.origin[i] < self.stencil - 1 for i in range(obs.ndim)):
                warnings.warn(f'{obs} too close to the bound')
                continue
            if any(obs.env[i] - self.stencil < obs.origin[i] + obs.size[i] - 1 < obs.env[i] - 1 for i in range(obs.ndim)):
                warnings.warn(f'{obs} too close to the bound')

    def is_out_of_bounds(self, obs):
        """Check if subdomain is out of bounds."""
        return any(s.start < 0 or s.stop - 1 >= n for s, n in zip(obs.sn, self.shape))

    @staticmethod
    def is_extended_overlap(o1, o2):
        """Report whether obstacle o1 and o2 share extended coordinates."""
        for s, o in zip(o1.extended_cn, o2.extended_cn):
            if s[1] <= o[0] or s[0] >= o[1]:
                return False
        return True

    def get_obstacle_by_face(self, f):
        """Return the Obstacle object containing the face f."""
        for obs in self:
            if obs.sid == f.sid:
                return obs

    def get_obstacle_by_sid(self, sid):
        """Return Obstacle whose identity is sid."""
        for obs in self:
            if obs.sid == sid:
                return obs

    def _update_face_description(self):
        """Set attributes for each face.

        Note
        ----
        Can be slow for a large number of faces.

        """

        self.overlapped_cuboids = [(o1, o2) for o1, o2 in itertools.combinations(self, r=2) if o1.intersects(o2)]
        faces_vs_subs = []
        for o1, o2 in self.overlapped_cuboids:
            faces_vs_subs += [(f, o2) for f in o1.faces if f.intersects(o2)]
            faces_vs_subs += [(f, o1) for f in o2.faces if f.intersects(o1)]
        #faces_vs_subs = [(f, o) for f, o in itertools.product(self.faces, self) if f.sid != o.sid]

        # Faces clamped to global domain (handle periodic condition)
        for f, b in itertools.product(self.faces, self.bounds.faces):
            if f.side == b.side:
                if f in b:
                    if b.bc != 'P':
                        f.clamped = b
                    if b.bc == 'P':
                        f.periodic = b

        # Face fully covered by an obstacle
        for f, o in faces_vs_subs:
            if f in o:
                f.covered.append(o)

        # Faces normally bounded by global domain
        for f in self.faces:
            bounded = [(r.start == 0, r.stop == s) for i, (r, s) in enumerate(zip(f.rn, self.shape))
                        if i != f.axis]
            if any(itertools.chain(*bounded)):
                f.bounded = True

        # Face Overlapped by another obstacle, or colinear to another obstacle
        for f, o in [(_f, _o) for _f, _o in faces_vs_subs if not _f.covered]:
            if f.intersects(o):
                if f.intersects(o.faces[2*f.axis + max(0, f.normal)]):
                    f.colinear.append(o)
                else:
                    f.overlapped.append(o)

        # Bounds covered by an obstacle
        for f, o in itertools.product(self.bounds.faces, self):
            if f.intersects(o):
                f.overlapped.append(o)

    def flatten(self, axis, index=0):
        """Return a flat version of the object."""
        if self.ndim != 3:
            warnings.warn('Already flat')
            return None

        subs = []
        for obs in self:
            if index in obs.rn[axis]:
                subs.append(obs.flatten(axis))

        bc = ''.join([v for i, v in enumerate(self.bc) if i not in [2*axis, 2*axis + 1]])
        shape = tuple(o for i, o in enumerate(self.shape) if i != axis)
        obsset = ObstacleSet(shape=shape, bc=bc, subs=subs, stencil=self.stencil)
        obsset.__volumic = self

        return obsset

    def unflatten(self):
        """Return a volumic version of flattened object."""
        instance = getattr(self, f'_{type(self).__name__}__volumic', None)
        if not instance:
            warnings.warn('The object does not have a volumic version')
            return self
        return instance