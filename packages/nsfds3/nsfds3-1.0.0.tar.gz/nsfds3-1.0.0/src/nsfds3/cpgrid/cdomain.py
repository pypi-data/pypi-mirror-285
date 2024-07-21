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
# Creation Date : 2022-06-09 - 23:00:01
"""
The `cdomain` module provides :py:class:`ComputationDomains` class aiming at dividing the
grid into subdomains following the geometric configurations.
"""

import itertools as _it
import numpy
import rich.progress as _rp
from nsfds3.cpgrid.geometry import ObstacleSet, DomainSet, Domain
from nsfds3.cpgrid.cutils import get_2d_cuboids, get_3d_cuboids
from nsfds3.cpgrid.utils import buffer_kwargs
from nsfds3.graphics.graphics import CPViewer


class ComputationDomains:
    """Divide computation domain in several Subdomains based on obstacles in presence.

    Parameters
    ----------
    shape : tuple
        Size of the domain. Must be a tuple with 3 int objects.
    obstacles : list of nsfds3.cpgrid.geometry.Obstacle, :py:class:`nsfds3.cpgrid.geometry.ObstacleSet`, optional
        Obstacles in the computation domain.
    bc : {'[APW][APW][APW][APW]'}, optional
        Boundary conditions. Must be a 4 or 6 characters string corresponding to
        left, right, front, back, bottom, and top boundaries, respectively.
    bz_n : int, optional
        Size of the buffer zone
    stencil : int, optional
        Size of the finite difference stencil.
    free: bool, optional
        Free memory after the domains are found
    """

    _BC_U = ['W', 'A', 'V']
    _BC_C = ['P', ]

    def __init__(self, shape, obstacles=None, bc='WWWWWW', bz_n=20, stencil=11, free=True):

        self.shape = shape
        self.ndim = len(shape)
        self.bc = bc
        self.bz_n = bz_n
        self.stencil, self._midstencil = stencil, int((stencil - 1) / 2)

        if isinstance(obstacles, ObstacleSet):
            self.obstacles = obstacles
        else:
            self.obstacles = ObstacleSet(shape, bc=bc, subs=obstacles, stencil=stencil)

        self.corners = self.obstacles.corners
        self.bounds = self.obstacles.bounds
        self.buffer = Domain(**buffer_kwargs(self.bc, self.bz_n, self.shape))

        self.find_domains()

        if free:
            self._free()

    def _mask_init(self):
        """
        Initialize a mask that contains 0 at the location of obstacles and 1 elsewhere.
        """
        self._mask = numpy.ones(self.shape + (self.ndim, ), dtype=numpy.int8)
        sax = (slice(0, self.ndim), )

        for obs in self.obstacles:
            self._mask[obs.sin + sax] = 0

        # Fix covered faces
        for f in self.obstacles.covered:
            self._mask[f.sin + sax] = 0

        # Fix junction between face to face overlapped objects
        combs = []
        for o1, o2 in self.obstacles.overlapped_cuboids:
            combs += [(f1, f2) for f1, f2 in _it.product(o1.faces, o2.faces) if f1.side == f2.opposite]

        for f1, f2 in combs:
            if f1.intersects(f2):
                s = tuple(zip(*f1.inner_indices().intersection(f2.inner_indices())))
                self._mask[s + sax] = 0

        # Fix periodic and clamped faces
        for f in self.obstacles.periodic + self.obstacles.clamped:
            self._mask[f.sin + sax] = 0
            if f.colinear:
                fix = set()
                for fc in f.colinear:
                    fix |= set(f.intersection(fc))
                self._mask[tuple(zip(*fix)) + sax] = 0

        # Fix obstacle faces located at the corners (2d/3d), and also at the edges of the domain (in 3d)
        for f in self.obstacles.edged:
            # Fix corners in 2d/3d
            for c in self.corners:
                if f.contains(c):
                    s = f.corner_slices(c)
                    self._mask[s + sax] = 0
            if self.ndim == 3:
                for fedge, bedge in _it.product(f.edges, self.bounds.edges):
                    if [set(rf).intersection(re) for rf, re in zip(fedge, bedge)]:
                        self._mask[f.slice_from_edge(fedge) + sax] = 0

    def _mask_setup(self):
        """
        Fill a mask according to finite difference scheme to be applied on each point.
            - Obstacles        : 0
            - Centered schemes : 1
            - Forward scheme   : stencil
            - Backward scheme  : -stencil
        """
        self._mask_init()
        bounds = tuple(b for b in self.bounds.faces if b.bc in self._BC_U)

        for f in self.obstacles.uncentered + bounds:
            fbox = f.box(self._midstencil)
            base = numpy.zeros(fbox.size, dtype=numpy.int8)
            base[(slice(None), ) * self.ndim] = self._mask[f.base_slice + (f.axis, )] == 0
            if f.inner:
                base[self._mask[fbox.sn + (f.axis, )] == 1] = f.normal * self.stencil
                base[base == 1] = 0
            else:
                base[self._mask[fbox.sn + (f.axis, )] == 1] *= f.normal * self.stencil
                base[base == 0] = 1
            self._mask[fbox.sn + (f.axis, )] *= base

    def get_cuboids(self, mask, ax=-1, N=-1):
        """Return a list of dictionnaries containing cuboid parameters.

        Parameters
        ----------
            mask : numpy.array
                Search cuboids in mask
            ax : int, optional
                Direction of the search. Can be 0 (x), 1 (y), or other (center)
            N : int, optional
                Fix one dimension of the output cuboids. Only for ax=0 or ax=1.
        """
        if mask.ndim == 2:
            return get_2d_cuboids(mask, ax, N)

        elif mask.ndim == 3:
            return get_3d_cuboids(mask, ax, N)

        return []

    def find_domains(self):
        """
        Split the domain in rectangular/cubic subdomains
        """

        self._mask_setup()
        confs = [1, self.stencil, -self.stencil]
        domains = [[] for i in range(self.ndim)]

        with _rp.Progress(_rp.TextColumn("[bold blue]{task.description:<20}...", justify="right"),
                          _rp.BarColumn(bar_width=None),
                          _rp.TextColumn("[progress.percentage]{task.percentage:>3.1f}% •"),
                          _rp.TimeRemainingColumn(),
                          _rp.TextColumn("• {task.fields[details]}")) as pbar:

            task = pbar.add_task("[red]Building domains...",
                                 total=len(confs) * self.ndim, details='Starting...')

            for axname, n in zip('xyz', range(self.ndim)):
                for name, mid, c in zip('cpm', [-1, self._midstencil, self._midstencil], confs):
                    ti = pbar.get_time()

                    m = numpy.array((self._mask[..., n] == c), dtype=numpy.int8)                     # To optimize ?
                    cuboids = self.get_cuboids(m, ax=n, N=mid)
                    for cub in cuboids:
                        domains[n].append(Domain(cub['origin'], cub['size'], self.shape, tag=name, axis=n))

                    pbar.update(task, advance=1,
                                details=f'{axname} / {name} in {pbar.get_time() - ti:.2f} s')

            pbar.update(task, advance=0,
                        details=f'Total : {pbar.tasks[0].finished_time:.2f} s')
            pbar.refresh()

        self.domains = []
        for ax, domain in zip('xyz', domains):
            setattr(self, f'{ax}domains', DomainSet(self.shape, self.bc, subs=domain))
            self.domains.append(getattr(self, f'{ax}domains'))
        self.cdomains = min(domains, key=len)

        if not self.is_valid:
            print("Computation domain seems not to be valid.")

    def show(self, obstacles=True, domains=False, bounds=True, only_mesh=True, **kwargs):
        """Plot 3d representation of computation domain."""
        viewer = CPViewer(self)
        viewer.show(obstacles=obstacles, domains=domains, bounds=bounds, only_mesh=only_mesh, **kwargs)

    @property
    def is_valid(self):
        """Report whether computation domains seem valid or not."""
        for d in self.domains:
            m = numpy.ones(self.shape, dtype=numpy.int8)
            for obs in self.obstacles:
                m[*obs.sn] = 0
            for obs in d:
                m[*obs.sn] = 0
            if m.any():
                return False
        return True

    def _free(self):
        try:
            del self._mask
        except AttributeError:
            pass

    def __str__(self):
        s = ''
        for ax, _ in zip('xyz', range(self.ndim)):
            s += f"{ax}-{getattr(self, f'{ax}domains')}\n\n"
        return s

    def __repr__(self):
        return self.__str__()


if __name__ == "__main__":

    from nsfds3.cpgrid.templates import TestCases

    # Geometry
    shape = 512, 512, 512
    bc = 'WWWWWW'
    obstacles = TestCases.base(shape=shape)
    cp = ComputationDomains(shape, bc=bc, obstacles=obstacles, free=False)
    cp.show(domains=True, bounds=False)