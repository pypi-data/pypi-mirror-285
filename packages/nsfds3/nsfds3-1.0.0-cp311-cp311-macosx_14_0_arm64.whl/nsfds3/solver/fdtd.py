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
# Creation Date : 2022-07-11 - 22:25:34
# pylint: disable=redefined-builtin
# pylint: disable=redefined-outer-name
# pylint: disable=protected-access
"""
The `fdtd` module provides the `FDTD` (Finite Difference Time Domain) class that
setup and run the simulation.
"""

import sys
import pickle
import h5py
import numpy
from time import perf_counter as _pc
import pathlib as _pathlib

from libfds.cfdtd import cFdtd
from libfds.cmaths import nan_check

from rich import print
from rich.panel import Panel
from rich.progress import track

from nsfds3.graphics import MPLViewer
from nsfds3.utils import misc
from nsfds3.solver import CfgSetup, CustomInitialConditions


class FDTD:
    """Solve Navier-Stokes equations using Finite Difference Time Domain (FDTD) technique.

    Parameters
    ----------
    cfg: CfgSetup
        Configuration of the simulation
    msh: CartesianGrid, CurvilinearGrid
        Grid used for the simulation
    ics: CustomInitialConditions
        Custom Initial conditions
    quiet: bool
        If True, display informations on the standard output
    timings: bool
        If True, display complete timings during the simulation
    overwrite: bool
        If True, automatically overwrite files
    nan_check: bool
        If True, exit simulation when nan are encountered. This option may degrade computation time.

    Notes
    -----
    When the simulation is complete, one can use the `show` method to display the desired field
    at the last iteration, or inspect the `csolver` object that gathers all conservative variables
    at the last iteration.

    Finite differences schemes, Runge-Kutta algorithm and selective filter are applied using
    the technique described in [1]_. The shock capturing procedure is applied using the technique
    described in [2]_. Curvilinear viscous fluxes are calculated following [3]_.

    References
    ----------

    .. [1] C. Bogey, C. Bailly, "A family of low dispersive and low dissipative explicit schemes for
           flow and noise computations", Journal of Computational Physics, Volume 194, Issue 1, 2004,
           Pages 194-214.

    .. [2] C. Bogey, N. de Cacqueray, C. Bailly, "A shock-capturing methodology based on adaptative
           spatial filtering for high-order non-linear computations", Journal of Computational Physics,
           Volume 228, Issue 5, 2009, Pages 1447-1465.

    .. [3] Marsden, Olivier. « Calcul direct du rayonnement acoustique de profils par une 
           approche curviligne d’ordre élevé », 2005.
    """

    def __init__(self, cfg, msh, ics=None, quiet=None, timings=None, overwrite=None, nan_check=None):

        # Initialize configuration & mesh (slow because of pickle loading)
        self.cfg = cfg
        self.msh = msh
        self.save_objects()

        # ICS : Here CustomInitialCondition can take time because of loading pickles
        self.ics = ics if ics is not None else CustomInitialConditions(cfg, msh)

        # Arguments
        self.quiet = quiet if isinstance(quiet, bool) else self.cfg.quiet
        self.timings = timings if isinstance(timings, bool) else self.cfg.sol.timings
        self.overwrite = overwrite if isinstance(overwrite, bool) else self.cfg.files.overwrite
        self.nan_check = nan_check if isinstance(nan_check, bool) else self.cfg.sol.nan_check

        # Initialize timer
        self._timings = {}

        # Initialize sources (boundaries and domain)
        time = numpy.linspace(0, cfg.sol.nt * cfg.dt, cfg.sol.nt + 1)
        for face in [f for f in msh.obstacles.faces if f.bc == "V"]:
            face.source_evolution = face.source_function(time)

        for source in self.cfg.src.tes:
            source.set_evolution(time)

        # Initialize solver ()
        self.csolver = cFdtd(self.cfg, self.msh, ics=self.ics)
        if self.cfg.prb:
            self.probes = numpy.zeros((len(cfg.prb), cfg.sol.ns))
            for n, c in enumerate(self.cfg.prb):
                self.probes[n, 0] = self.csolver.p[tuple(c)]

        # Initialize save
        self._init_save()

    @classmethod
    def from_cfg(cls, cfg):
        if isinstance(cfg, (str, _pathlib.Path)):
            cfg = CfgSetup(cfg)
        elif not isinstance(cfg, CfgSetup):
            raise ValueError('cfg must be str, pathlib.Path, or CfgSetup instance')
        msh = build_mesh(cfg)
        return cls(cfg, msh)

    def _log(self):
        """Display informations about the simulation."""

        res = None

        if self.timings:
            desc, time_per_iteration = misc.unload_timings(self._timings)
            if not self.quiet:
                res = self.csolver.residual()
                txt = f"Iteration: [red]{self.cfg.sol.it:>6}\t[/]|\t"
                txt += f"Residuals: [green]{res:>.4f}\t[/]|\t"
                txt += f"Time: {time_per_iteration:>.4f}"
                print(Panel(txt))
                print(f"{desc}")

        if self.nan_check:
            if res is None:
                res = self.csolver.residual()
            if not isinstance(res, float):
                print('[bold bright_magenta]NaN encountered : exiting simulation')
                print(nan_check(self.csolver.p))
                sys.exit(0)

    def run(self):
        """Run simulation."""
        ti = _pc()
        try:
            self.sfile = h5py.File(self.cfg.files.data_path, 'a')
            for self.cfg.sol.it in track(range(self.cfg.sol.it + 1, self.cfg.sol.nt + 1),
                                         disable=self.quiet):
                self._eulerian_fluxes()
                self._viscous_fluxes()
                self._selective_filter()
                self._shock_capture()
                self._vorticity()
                if not self.cfg.sol.it % self.cfg.sol.ns:
                    self._save()
                    self._log()
                self._p_update_probes()

            if not self.quiet:
                msg = 'Simulation completed in [bold bright_cyan]{}[/].\n'
                msg += 'Final residuals of [bold bright_cyan]{:>.4f}[/].\n'
                msg += 'End at physical time [bold bright_cyan]t = {:.4f} sec.'
                print(Panel(msg.format(misc.secs_to_dhms(_pc() - ti),
                                       self.csolver.residual(),
                                       self.cfg.dt * self.cfg.sol.it)))
        except OSError:
            # Raised if no space left on hard drive
            # del last iteration
            if self.cfg.sol.save:
                del self.sfile[f'r_it{self.cfg.sol.it - self.cfg.sol.ns}']
                del self.sfile[f'ru_it{self.cfg.sol.it - self.cfg.sol.ns}']
                del self.sfile[f'rv_it{self.cfg.sol.it - self.cfg.sol.ns}']
                del self.sfile[f're_it{self.cfg.sol.it - self.cfg.sol.ns}']
                if self.msh.ndim == 3:
                    del self.sfile[f'rw_it{self.cfg.sol.it - self.cfg.sol.ns}']
            if self.cfg.sol.save_p and not self.cfg.sol.save:
                for i in range(1, 6):
                    del self.sfile[f'p_it{self.cfg.sol.it - i * self.cfg.sol.ns}']

        finally:
            self.save_objects()
            # Save at least the last fields in case of resume
            if not self.cfg.sol.save:
                self._save_main_fields()
            self.sfile.close()

    @misc.timer
    def _eulerian_fluxes(self):
        """Compute Eulerian fluxes."""
        self.csolver.efluxes_integrate()

    @misc.timer
    def _viscous_fluxes(self):
        """Compute viscous fluxes."""
        self.csolver.vfluxes_integrate()

    @misc.timer
    def _selective_filter(self):
        """Apply selective filter."""
        self.csolver.sf_apply()

    @misc.timer
    def _shock_capture(self):
        """Apply shock capture procedure."""
        self.csolver.sc_apply()

    @misc.timer
    def _vorticity(self):
        """Compute vorticity """
        self.csolver.vrt_update()

    @misc.timer
    def _p_update_probes(self):
        """Update probes."""
        if self.cfg.prb:
            for n, c in enumerate(self.cfg.prb):
                self.probes[n, self.cfg.sol.it % self.cfg.sol.ns] = self.csolver.p[tuple(c)]

    @misc.timer
    def _save(self, force=False):
        """Save data."""

        self.cfg.sol.itmax = self.cfg.sol.it
        self.sfile.attrs['itmax'] = self.cfg.sol.it

        # Save fields
        if self.cfg.sol.save:
            self._save_main_fields()

            if self.cfg.sol.vrt:
                self.sfile.create_dataset(f'wz_it{self.cfg.sol.it}', data=self.csolver.wz)
                if self.msh.ndim == 3:
                    self.sfile.create_dataset(f'wx_it{self.cfg.sol.it}', data=self.csolver.wx)
                    self.sfile.create_dataset(f'wy_it{self.cfg.sol.it}', data=self.csolver.wy)

        if self.cfg.sol.save_p:
            self.sfile.create_dataset(f'p_it{self.cfg.sol.it}', data=self.csolver.p)

        # Unload probe values
        if self.cfg.prb:
            self.sfile['probe_values'][:, self.cfg.sol.it - self.cfg.sol.ns:self.cfg.sol.it] = self.probes

    def _save_main_fields(self):
        self.sfile.create_dataset(f'r_it{self.cfg.sol.it}', data=self.csolver.r)
        self.sfile.create_dataset(f'ru_it{self.cfg.sol.it}', data=self.csolver.ru)
        self.sfile.create_dataset(f'rv_it{self.cfg.sol.it}', data=self.csolver.rv)
        self.sfile.create_dataset(f're_it{self.cfg.sol.it}', data=self.csolver.re)
        if self.msh.ndim == 3:
            self.sfile.create_dataset(f'rw_it{self.cfg.sol.it}', data=self.csolver.rw)

    def save_objects(self):
        """Save cfg and msh objects."""

        with open(self.cfg.files.data_path.with_suffix('.cfg'), 'wb') as pkl:
            pickle.dump(self.cfg, pkl, protocol=pickle.HIGHEST_PROTOCOL)

        with open(self.cfg.files.data_path.with_suffix('.msh'), 'wb') as pkl:
            pickle.dump(self.msh, pkl, protocol=pickle.HIGHEST_PROTOCOL)

    def _init_save(self):
        """Init save file."""
        if self.ics.has_old_fields:
            self._init_save_old()
        else:
            self._init_save_new()

    def _init_save_old(self):
        """Init old save file."""
        if not self.overwrite:
            overwrite = misc.Confirm.ask(f'[blink]Confirm appending results to {self.cfg.files.data_path}[/] ?')
            if not overwrite:
                sys.exit(0)

        with h5py.File(self.cfg.files.data_path, 'r+') as self.sfile:
            self.sfile.attrs['nt'] = self.cfg.sol.nt
            self.cfg.sol.it = self.sfile.attrs['itmax']
            probes = numpy.zeros((len(self.cfg.prb), self.cfg.sol.nt))
            probes[:, :self.cfg.sol.it] = self.sfile['probe_values'][:, :self.cfg.sol.it]
            del self.sfile['probe_values']
            self.sfile.create_dataset('probe_values', data=probes)

    def _init_save_new(self):
        """Init new save file."""
        if self.cfg.files.data_path.is_file() and not self.overwrite:
            msg1 = f'[bold red]{self.cfg.files.data_path}[/] already exists. \n'
            msg2 = f'[blink]Overwrite to start new simulation ?'
            overwrite = misc.Confirm.ask(msg1 + msg2)
            if not overwrite:
                sys.exit(0)

        with h5py.File(self.cfg.files.data_path, 'w') as self.sfile:
            self.sfile.attrs['vorticity'] = self.cfg.sol.vrt
            self.sfile.attrs['ndim'] = self.msh.ndim
            self.sfile.attrs['dt'] = self.cfg.dt
            self.sfile.attrs['nt'] = self.cfg.sol.nt
            self.sfile.attrs['ns'] = self.cfg.sol.ns
            self.sfile.attrs['p0'] = self.cfg.tp.p0
            self.sfile.attrs['gamma'] = self.cfg.tp.gamma

            probes = numpy.zeros((len(self.cfg.prb), self.cfg.sol.nt))
            self.sfile.create_dataset('probe_locations', data=self.cfg.prb.locs)
            self.sfile.create_dataset('probe_values', data=probes)

            # Save initial fields
            self._save()

    def show(self, view='p', vmin=None, vmax=None, **kwargs):
        """Show results."""
        viewer = MPLViewer(self.cfg, data=self.csolver)
        viewer.show(view=view, vmin=vmin, vmax=vmax, **kwargs)


if __name__ == '__main__':

    from nsfds3.cpgrid import build_mesh

    config = CfgSetup()
    mesh = build_mesh(config)
    fdtd = FDTD(config, mesh)
    fdtd.run()
    fdtd.show()
