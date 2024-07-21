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
# Creation Date : 2022-06-09 - 22:15:26
"""
Some helper classes and functions to represent meshes graphically.

    * `MeshViewer` : Graphical tool to visualize Mesh objects graphically.
    * `CPViewer` : MeshViewer specialization adapted to ComputationDomains.
    * `MPLViewer` : MeshViewer specialization adapted to libfds.cFdtd or hdf5 files.
    * `PlyViewer` : Mesh/ComputationDomain viewer using Plotly.
"""

import os
import sys
import pathlib
import time
import numpy as _np
import scipy.signal as _signal
import matplotlib.pyplot as _plt
import matplotlib.animation as _ani
import plotly.graph_objects as _go

from plotly.subplots import make_subplots
from matplotlib import patches as _patches, path as _path
from matplotlib.collections import PatchCollection
from matplotlib.image import PcolorImage
from mpl_toolkits.axes_grid1 import make_axes_locatable

from rich.progress import track
from rich import print
from nsfds3.utils.data import Hdf5Wrapper, FieldWrapper, parse_decimate
from nsfds3.graphics.utils import MidPointNorm, cmap_jet, cmap_mask, dict_update, fig_scale
from libfds.cfdtd import cFdtd2d, cFdtd3d


cmap = cmap_jet()


class ViewerError(Exception):
    """Exception raised from the viewer."""


class MeshViewer:
    """Graphical tool to visualize Mesh instances graphically.

    Parameters
    ----------
    mesh: CartesianGrid or CurvilinearGrid
        Mesh object
    figsize: tuple, optional
        Size of the figure
    dpi: int, optional
        Resolution of the figure
    grid: bool, optional
        If True, display the grid.
    buffer: bool, optional
        If True, display the buffer zones.
    obstacles: bool, optional
        If True, display the obstacles
    domains: bool, optional
        If True, diplay the computation domains
    N: int, optional
        Grid step
    slice: tuple, (x0, y0[, z0])
        Position of the cross sections for 3d views
    """

    dkwargs = dict(figsize=(10, 10), dpi=100,
                   grid=True, buffer=True, obstacles=True, domains=False, N=1,
                   slices = None,
                   kwargs_grid=dict(zorder=5),
                   kwargs_obstacles=dict(facecolor='k', alpha=0.2, hatch='x', zorder=100, annotate=False, rasterized=True),
                   kwargs_domains=dict(facecolor='y', alpha=0.2, zorder=100, annotate=False, rasterized=True),
                   kwargs_buffer=dict(linewidth=3, edgecolor='k', facecolor='none', alpha=0.2, zorder=100))

    def __init__(self, msh):

        self.msh = msh
        self.ndim = len(msh.shape)
        self.axis = self.msh.paxis

        for name, ax in zip(('x', 'y', 'z'), self.axis):
            setattr(self, name, ax)

    def show(self, **kwargs):

        kwargs = dict_update(self.dkwargs, kwargs)

        if self.ndim == 3:
            fig, *_ = self._frame3d(**kwargs)
        else:
            fig, *_ = self._frame2d(**kwargs)

        fig.show()

    def _frame3d(self, cbar=False, **kwargs):

        slices = self._get_slices(kwargs.get('slices'))
        fig, ax_xy = _plt.subplots(figsize=kwargs.get('figsize'), dpi=kwargs.get('dpi'), tight_layout=True)

        # Size fig. & Limits
        width, height = fig.get_size_inches()
        limits = self.msh.domain_limits if kwargs.get('buffer') else self.msh.buffer_limits
        size_x = _np.diff(limits[0])[0]
        size_y = _np.diff(limits[1])[0]
        size_z = _np.diff(limits[2])[0]

        # Axes
        divider = make_axes_locatable(ax_xy)
        ax_xz = divider.append_axes("top", height * size_z / (size_y + size_z), pad=0., sharex=ax_xy)
        ax_zy = divider.append_axes("right", 0.95 * width * size_z / (size_x + size_z), pad=0., sharey=ax_xy)

        for ax in fig.get_axes():
            ax.set_aspect(1.)

        if cbar:
            ax_bar = divider.append_axes("right", size="5%", pad=0.1)
        else:
            ax_bar = None

        # Labels
        ax_xy.set_xlabel(r'$x$ [m]')
        ax_xy.set_ylabel(r'$y$ [m]')

        ax_xz.xaxis.set_tick_params(labelbottom=False)
        ax_xz.set_ylabel(r'$z$ [m]')

        ax_zy.yaxis.set_tick_params(labelleft=False)
        ax_zy.set_xlabel(r'$z$ [m]')

        # Cross section lines
        ax_xy.plot(self.x[:, self.i_xz, self.i_xy], self.y[:, self.i_xz, self.i_xy], color='gold', linewidth=1)
        ax_xy.plot(self.x[self.i_zy, :, self.i_xy], self.y[self.i_zy, :, self.i_xy], color='green', linewidth=1)
        ax_xz.plot(self.x[:, self.i_xz, self.i_xy], self.z[:, self.i_xz, self.i_xy], color='gold', linewidth=1)
        ax_zy.plot(self.z[self.i_zy, :, self.i_xy], self.y[self.i_zy, :, self.i_xy], color='green', linewidth=1)

        # Grid, Buffer zones, Obstacles, and domains
        obs_xy = ([obs for obs in self.msh.obstacles if self.i_xy in obs.rz],
                  [obs for obs in self.msh.obstacles if self.i_xy not in obs.rz])
        obs_xz = ([obs for obs in self.msh.obstacles if self.i_xz in obs.ry],
                  [obs for obs in self.msh.obstacles if self.i_xz not in obs.ry])
        obs_zy = ([obs for obs in self.msh.obstacles if self.i_zy in obs.rx],
                  [obs for obs in self.msh.obstacles if self.i_zy not in obs.rx])

        for ax, indices, obs in zip([ax_xy, ax_xz, ax_zy], [(0, 1), (0, 2), (2, 1)], [obs_xy, obs_xz, obs_zy]):

            s = [slice(None) if i in indices else s for i, s in enumerate(slices)]
            args = ax, [v[tuple(s)] for v in self.axis], indices

            if kwargs.get('grid'):
                self.grid(*args, N=kwargs.get('N'), **kwargs.get('kwargs_grid'))

            if kwargs.get('obstacles'):
                self.objects(*args, obs[0], **kwargs.get('kwargs_obstacles'))
                self.objects(*args, obs[1], alpha=0.1, facecolor='k')

            self.objects(*args, self.msh.buffer, **kwargs.get('kwargs_buffer'))
            if not kwargs.get('buffer'):
                ax.set_xlim(self.msh.buffer_limits[indices[0]])
                ax.set_ylim(self.msh.buffer_limits[indices[1]])
            else:
                ax.set_xlim(self.msh.paxis[indices[0]].min(),
                            self.msh.paxis[indices[0]].max())
                ax.set_ylim(self.msh.paxis[indices[1]].min(),
                            self.msh.paxis[indices[1]].max())

        return fig, ax_xy, ax_xz, ax_zy, ax_bar

    def _frame2d(self, cbar=False, **kwargs):

        fig, ax = _plt.subplots(figsize=kwargs.get('figsize'), dpi=kwargs.get('dpi'), tight_layout=True)
        if cbar:
            divider = make_axes_locatable(ax)
            ax_bar = divider.append_axes("right", size="5%", pad=0.1)
        else:
            ax_bar = None

        args = ax, self.axis, (0, 1)

        if kwargs.get('grid'):
            self.grid(*args, N=kwargs.get('N'), **kwargs.get('kwargs_grid'))

        if kwargs.get('obstacles'):
            self.objects(*args, self.msh.obstacles, **kwargs.get('kwargs_obstacles'))

        if kwargs.get('domains'):
            self.objects(*args, self.msh.domains, **kwargs.get('kwargs_domains'))

        if 'A' in self.msh.bc:
            self.objects(*args, self.msh.buffer, **kwargs.get('kwargs_buffer'))
        if not kwargs.get('buffer'):
            ax.set_xlim(self.msh.buffer_limits[0])
            ax.set_ylim(self.msh.buffer_limits[1])
        else:
            ax.set_xlim(self.msh.x.min(), self.msh.x.max())
            ax.set_ylim(self.msh.y.min(), self.msh.y.max())

        ax.set_xlabel(r'$x$ [m]')
        ax.set_ylabel(r'$y$ [m]')
        ax.set_aspect(1.)

        return fig, ax, ax_bar

    def _get_slices(self, slices):

        if slices:
            if all([a < b for a, b in zip(slices, self.msh.shape)]):
                self.i_zy, self.i_xz, self.i_xy = slices
            else:
                raise IndexError('Slices out of bounds')
        else:
            self.i_zy, self.i_xz, self.i_xy = [int(n/2) for n in self.msh.shape]

        return self.i_zy, self.i_xz, self.i_xy

    @staticmethod
    def objects(ax, axes, indices, obj, **kwargs):
        """Plot objects on ax.

        Parameters
        ----------
        ax : matplotlib.axes._subplots.AxesSubplot
            Axis where to draw the object
        axes : tuple of np.ndarray
            Grid axes (x, y [, z])
        indices : tuple of int
            Indices of the axes to use
        obj : sequence
            Sequence of objects that must be drawn
        **kwargs : dict
            Keyword Arguments of matplotlib.patches.Rectangle
        """
        dkwargs = dict(linewidth=3, edgecolor='k', facecolor=None,
                       alpha=1., hatch=None, annotate=False, rasterized=True)
        kwargs = dict_update(dkwargs, kwargs)
        annotate = kwargs.pop('annotate')

        if hasattr(obj, 'sid'):
            obj = (obj, )

        # Fix for when indices is (2, 1)
        if sorted(indices) == list(indices):
            u, v = axes[indices[0]], axes[indices[1]]
        else:
            u, v = axes[indices[0]].T, axes[indices[1]].T

        collection = []
        for sub in obj:
            b = [(u[i, sub.cn[indices[1]][0]], v[i, sub.cn[indices[1]][0]]) for i in sub.rn[indices[0]]][::-1]
            l = [(u[sub.cn[indices[0]][0], i], v[sub.cn[indices[0]][0], i]) for i in sub.rn[indices[1]]]
            t = [(u[i, sub.cn[indices[1]][1]], v[i, sub.cn[indices[1]][1]]) for i in sub.rn[indices[0]]]
            r = [(u[sub.cn[indices[0]][1], i], v[sub.cn[indices[0]][1], i]) for i in sub.rn[indices[1]]]
            verts = b + l + t + r
            codes = [_path.Path.MOVETO] + \
                    (len(verts)-2)*[_path.Path.LINETO] + \
                    [_path.Path.CLOSEPOLY]
            path = _path.Path(verts, codes)
            collection.append(_patches.PathPatch(path))
            if annotate:
                ax.annotate(f'{sub.sid}', sub.center(ax=indices, transform=(u, v)),
                            ha='center', va='center',
                            color='gray', weight='bold', style='italic', fontsize=8)

        # Adding the collection to ax is much more faster than adding sequentially the paths
        # This can be improved furthermore using PolyCollection :
        # https://stackoverflow.com/questions/54463269/avoid-slow-looping-when-plotting-irregular-raster-plot-using-patches-rectangle
        collection = PatchCollection(collection)
        collection.set(**kwargs)
        ax.add_collection(collection)

    @staticmethod
    def grid(ax, axes, indices, N, **kwargs):
        """Plot grid on ax.

        Parameters
        ----------
        ax : matplotlib.axes._subplots.AxesSubplot
            Axis where to draw the grid
        axes : tuple of np.ndarray
            Grid axes (x, y [, z])
        indices : tuple of int
            Indices of the axes to use
        N : int
            Plot a grid line every N points
        **kwargs : dict
            Keyword Arguments of ax.vlines/ax.hlines
        """

        dkwargs = dict(color='k', linewidth=0.1)
        kwargs = dict_update(dkwargs, kwargs)

        # Fix for when indices is (2, 1)
        if sorted(indices) == list(indices):
            u, v = axes[indices[0]], axes[indices[1]]
        else:
            u, v = axes[indices[0]].T, axes[indices[1]].T

        for i in _np.arange(0, v.shape[1], N):
            ax.plot(u[:, i], v[:, i], **kwargs)

        for i in _np.arange(0, u.shape[0], N):
            ax.plot(u[i, :], v[i, :], **kwargs)

        ax.plot(u[:, -1], v[:, -1], **kwargs)
        ax.plot(u[-1, :], v[-1, :], **kwargs)

    def __str__(self):
        s = f'{type(self).__name__}\n'
        return s

    def __repr__(self):
        return str(self)


class CPViewer(MeshViewer):
    """MeshViewer specialization adapted to ComputationDomains.

    Parameters
    ----------
    cpdomain: ComputationalDomain
        Computational domain object

    """

    def __init__(self, cpdomain):

        if not hasattr(cpdomain, '_mask'):
            raise ViewerError('Free must be False')

        self.cpdomain = cpdomain
        self.ndim = cpdomain.ndim

        self.mask = cpdomain._mask
        self.obstacles = cpdomain.obstacles
        self.xdomains = cpdomain.xdomains
        self.ydomains= cpdomain.ydomains
        if self.ndim == 3:
            self.zdomains = cpdomain.zdomains

        self.axis = tuple(_np.arange(0, n) for n in self.cpdomain.shape)
        self.axis = _np.meshgrid(*self.axis, indexing='ij')
        self.cmap, self.norm = cmap_mask(cpdomain.stencil)

    def _frame2d(self, **kwargs):

        fig, axs = _plt.subplots(1, self.ndim, figsize=(15, 8), tight_layout=True)
        for i in range(self.ndim):
            args = axs[i], self.axis, (0, 1)

            axs[i].imshow(self.mask[..., i].T, origin='lower', cmap=self.cmap, norm=self.norm)

            if kwargs.get('grid'):
                self.grid(*args, N=kwargs.get('N'), **kwargs.get('kwargs_grid'))

            if kwargs.get('obstacles'):
                self.objects(*args, self.obstacles, **kwargs.get('kwargs_obstacles'))

            if kwargs.get('domains') and i == 0:
                self.objects(*args, self.xdomains, **kwargs.get('kwargs_domains'))

            if kwargs.get('domains') and i == 1:
                self.objects(*args, self.ydomains, **kwargs.get('kwargs_domains'))

        return fig, axs

    def _frame3d(self, **kwargs):

        colorscales = {'p': ['blue', 'cyan'],
                       'm': ['red', 'magenta'],
                       'P': ['green', 'yellow']}

        fig = _go.Figure()
        data = []
        if kwargs['obstacles']:
            for sub in self.obstacles:
                data.append(_go.Mesh3d(x=sub.vertices[0],
                                    y=sub.vertices[1],
                                    z=sub.vertices[2],
                                    colorscale=['black', 'gray'],
                                    intensity=_np.linspace(0, 1, 8, endpoint=True),
                                    name=f'o{sub.sid}',
                                    opacity=1,
                                    alphahull=0,
                                    showscale=False,
                                    flatshading=True   # to hide the triangles
                                    ))
        if kwargs['domains']:
            domains = self.xdomains + self.ydomains + self.zdomains
            if not kwargs['bounds']:
                domains = domains.inner
            for sub in [s for s in domains if s.tag in ["p", "m"]]:
                data.append(_go.Mesh3d(x=sub.vertices[0],
                                    y=sub.vertices[1],
                                    z=sub.vertices[2],
                                    colorscale=colorscales[sub.tag],
                                    intensity=_np.linspace(0, 1, 8, endpoint=True),
                                    name=f'o{sub.sid}',
                                    opacity=1,
                                    alphahull=0,
                                    showscale=False,
                                    flatshading=True   # to hide the triangles
                                    ))

        fig.update_layout(width=800, height=600, font_size=11,  scene_aspectmode="data",
                        scene_camera_eye=dict(x=1.45, y=1.45, z=1), template="none")
        fig.add_traces(data)

        return fig, None


class MPLViewer(MeshViewer):
    """MeshViewer specialization adapted to exploit libfds.cFdtd isntances or hdf5 files.

    Parameters
    ----------
    cfg: nsfds3.solver.CfgSetup
        Configuration of the simulation
    data: libfds.cfdtd.cFdtd2d, libfds.cfdtd.cFdtd3d, pathlib.Path, str, optional
        Data can be provided as cFdtd2d/cFdtd3d or with the path to a hdf5 file.
        If data is not provided, the file pointed to by the cfg.files.data_path attribute is used if it exists.

    Note
    ----
    Until the MPLViewer instance is not closed with the close method, it keeps the hdf5 file open.
    This can cause problems when opening it in another process.
    It is strongly recommanded to use MPLViewer as a context manager :

    ::

        with MPLViewer(path_to_config_file.conf) as viewer:
            viewer.show(view='p', iteration=100)

    """

    dkwargs = dict(figsize=(10, 10), dpi=100, fps=24,
                   grid=False, buffer=False, obstacles=True, domains=False, probes=False,
                   N=1, slices = None,
                   kwargs_grid=dict(zorder=5),
                   kwargs_obstacles=dict(facecolor='k', alpha=0.2, zorder=100, annotate=False),
                   kwargs_domains=dict(facecolor='y', alpha=0.2, zorder=100, annotate=False),
                   kwargs_buffer=dict(linewidth=3, edgecolor='k', facecolor='none', alpha=0.2, zorder=100))

    def __init__(self, cfg, data=None):

        super().__init__(cfg.get_grid_backup())

        self.cfg = cfg
        self.closed = False

        if not data:
            if not cfg.files.data_path.is_file():
                raise FileNotFoundError('Unable to load hdf5 file.')
            else:
                data = cfg.files.data_path

        if isinstance(data, (cFdtd2d, cFdtd3d)):
            self.data = FieldWrapper(data)
        elif isinstance(data, (pathlib.Path, str)):
            self.data = Hdf5Wrapper(data)
        else:
            raise ViewerError('data can be cFdtd2d, cFdtd3d, or path to hdf5 file')

    def show(self, view='p', vmin=None, vmax=None, iteration=0, decimate=None, **kwargs):
        """Show view at a given iteration.

        Parameters
        ----------
        view: str
            Field to show. Default to 'p'
        vmin/vmax: float
            Limit values of field. Default to None.
        iteration: int
            Show field at given time iteration. Default to 0
        decimate: tuple
            Decimate factor for each direction. Default to None
        **kwargs: dict
            Keyword arguments.
        """

        kwargs = dict_update(self.dkwargs, kwargs)

        var = self.data.get(view=view, iteration=iteration)

        if not vmin:
            vmin = _np.nanmin(var)
        if not vmax:
            vmax = _np.nanmax(var)

        norm = MidPointNorm(vmin=vmin, vmax=vmax, midpoint=0)

        fig, ax = self._frame(var, norm, decimate=decimate, **kwargs)

        _plt.show()

    def _frame(self, var, norm, decimate=None, **kwargs):
        """Helper method to setup graphical frames. Prefer using show() method."""
        kwargs = dict_update(self.dkwargs, kwargs)

        if len(self.msh.shape) == 3:
            return self._fields3d(var, norm, decimate=decimate, **kwargs)
        else:
            return self._fields2d(var, norm, decimate=decimate, **kwargs)

    def _fields2d(self, var, norm, decimate=None, **kwargs):
        """Show 2d results."""

        fig, ax, ax_bar = self._frame2d(cbar=True, **kwargs)

        # Fill figure (im : matplotlib.image.QuadMesh)
        dx, dy = parse_decimate(decimate, 2)
        im = ax.pcolorfast(self.x[::dx, ::dy], self.y[::dx, ::dy], var[::dx, ::dy][:-1, :-1].T, cmap=cmap, norm=norm, animated=True)

        # Colorbar
        midpoint = _np.nanmean(var) if norm.vmin > 0 and norm.vmax > 0 else 0
        if norm.vmax == 0:
            ticks = []
        elif abs(norm.vmin - midpoint) / norm.vmax > 0.33:
            ticks = [norm.vmin, midpoint, norm.vmax]
        else:
            ticks = [midpoint, norm.vmax]
        _plt.colorbar(im, cax=ax_bar, ticks=ticks)

        # Nans & Probes
        if kwargs.get('nans'):
            nans =  _np.argwhere(_np.isnan(var.T))
            nans = _np.array([(self.x[ix, iy], self.y[ix, iy]) for ix, iy in nans]).T
            ax.plot(*nans, 'r.')

        if self.cfg.prb and kwargs.get('probes'):
            prbs = [(self.x[ix, iy], self.y[ix, iy]) for ix, iy in self.cfg.prb]
            for prb in prbs:
                ax.plot(*prb, 'ro')

        return fig, im

    def _fields3d(self, var, norm, decimate=None, **kwargs):
        """Show 3d results."""

        fig, ax_xy, ax_xz, ax_zy, ax_bar = self._frame3d(cbar=True, **kwargs)

        ims = []

        # Fill figure
        dx, dy, dz = parse_decimate(decimate, 3)
        ims.append(ax_xy.pcolorfast(self.x[::dx, ::dy, self.i_xy], self.y[::dx, ::dy, self.i_xy], var[::dx, ::dy, :][:-1, :-1, self.i_xy], cmap=cmap, norm=norm))
        ims.append(ax_xz.pcolorfast(self.x[::dx, self.i_xz, ::dz], self.z[::dx, self.i_xz, ::dz], var[::dx, :, ::dz][:-1, self.i_xz, :-1], cmap=cmap, norm=norm))
        ims.append(ax_zy.pcolorfast(self.z[self.i_zy, ::dy, ::dz], self.y[self.i_zy, ::dy, ::dz], var[:, ::dy, ::dz][self.i_zy, :-1, :-1], cmap=cmap, norm=norm))

        # Colorbar
        midpoint = _np.nanmean(var) if norm.vmin > 0 and norm.vmax > 0 else 0
        if abs(norm.vmin - midpoint) / norm.vmax > 0.33:
            ticks = [norm.vmin, midpoint, norm.vmax]
        else:
            ticks = [midpoint, norm.vmax]
        fig.colorbar(ims[0], cax=ax_bar, ticks=ticks)

        # Probes
        if self.cfg.prb and kwargs.get('probes'):
            prbs = [(self.x[ix, iy, iz], self.y[ix, iy, iz], self.z[ix, iy, iz]) for ix, iy, iz in self.cfg.prb]
            for c_prb, prb in zip(self.cfg.prb, prbs):
                color = 'r' if self.i_xy == c_prb[2] else 'grey'
                ax_xy.plot(*(c for c in prb[:2]), marker='o', color=color)

                color = 'r' if self.i_xz == c_prb[1] else 'grey'
                ax_xz.plot(*(c for i, c in enumerate(prb) if i != 1), marker='o', color=color)

                color = 'r' if self.i_zy == c_prb[0] else 'grey'
                ax_zy.plot(*(c for c in prb[1:][::-1]), marker='o', color=color)

        return fig, ims

    def _init_movie(self, view):

        title = os.path.basename(self.cfg.files.name).split('.')[0]
        views = {'p': r'$p_a$ [Pa]',
                 'e': r'$e$ [kg.m$^2$.s$^{-2}$]',
                 'rho': r'$\rho$ [kg.m$^3$]',
                 'vx': r'$v_x$ [m/s]',
                 'vy': r'$v_y$ [m/s]',
                 'vz': r'$v_y$ [m/s]',
                 'wx': r'$\omega_x$ [m/s]',
                 'wy': r'$\omega_y$ [m/s]',
                 'wz': r'$\omega_z$ [m/s]',
                 're': r'$\rho e$ [kg$^2$.m$^{-1}$.s$^{-2}$]',
                 'ru': r'$\rho v_x$ [kg.m$^{-2}$/s]',
                 'rv': r'$\rho v_y$ [kg.m$^{-2}$/s]',
                 'rw': r'$\rho v_y$ [kg.m$^{-2}$/s]'}

        metadata = dict(title=title, filename=f'{title}_{view}.mkv',
                        view=view, var=views[view], comment='Made with nsfds3')

        return metadata

    def movie(self, view='p', nt=None, ref=None, maxref=100, decimate=True, xlim=None, ylim=None, zlim=None, codec='libx264', **kwargs):
        """Make movie for a given view."""

        kwargs = dict_update(self.dkwargs, kwargs)

        if not isinstance(self.data, Hdf5Wrapper):
            print('movie method only available for Hdf5Wrapper')
            sys.exit(1)

        # Handle decimate options
        if decimate is True:
            decimate = tuple(max(1, int(s / 1080)) for s in self.msh.shape)
        decimate = parse_decimate(decimate, len(self.msh.shape))
        if self.msh.ndim == 3:
            dx, dy, dz = decimate
        else:
            dx, dy = decimate

        # Create Iterator and make 1st frame
        print('Searching reference...')
        ti = time.perf_counter()
        data = self.data.get_iterator(view=view, nt=nt)
        vmin, vmax = self.data.reference(view=view, ref=ref, decimate=decimate, maxref=maxref)
        norm = MidPointNorm(vmin=vmin, vmax=vmax, midpoint=0)
        print(f'Done in {time.perf_counter() - ti:.2f} s')
        i, var = next(data)
        fig, im = self._frame(var, norm, iteration=i, decimate=decimate, **kwargs)
        fig.canvas.manager.full_screen_toggle()

        # Movie parameters
        metadata = self._init_movie(view)
        writer = _ani.FFMpegWriter(fps=kwargs.get('fps'), metadata=metadata, bitrate=-1, codec=codec)
        with writer.saving(fig, self.cfg.files.directory / metadata['filename'], dpi=kwargs.get('dpi')):

            writer.grab_frame()

            for i, var in track(data, description='Making movie...', disable=self.cfg.quiet):
                axes = fig.get_axes()
                if self.msh.ndim == 3:
                    if isinstance(im[0], PcolorImage):    # Pcolorimage object if non-rectangle mesh elements
                        im[0].set_data(self.x[::dx, ::dy, :], self.y[::dx, ::dy, :], var[::dx, ::dy, :][:-1, :-1, self.i_xy])
                        im[1].set_data(self.x[::dx, :, ::dz], self.z[::dx, :, ::dz], var[::dx, :, ::dz][:-1, self.i_xz, :-1])
                        im[2].set_data(self.z[:, ::dy, ::dz], self.y[:, ::dy, ::dz], var[:, ::dy, ::dz][self.i_zy, :-1, :-1])
                    else:                                 # AxesImage otherwise
                        im[0].set_array(var[::dx, ::dy, :][:-1, :-1, self.i_xy])
                        im[1].set_array(var[::dx, :, ::dz][:-1, self.i_xz, :-1])
                        im[2].set_array(var[:, ::dy, ::dz][self.i_zy, :-1, :-1])
                    axes[1].set_title(metadata['var'] + f' (n={i})')
                else:
                    im.set_array(var[::dx, ::dy][:-1, :-1].T)
                    axes[0].set_title(metadata['var'] + f' (n={i})')

                # grab_frame() takes 90% of the time to make the animation.
                # the self.fig.canvas.draw() in writer.grab_frame() is responsible of this !
                # TODO: rewrite a FasterFFmpegWriter that uses blit (and multiprocessing ?)
                # Note: the time/iteration is the same as the time to execute fig.savefig('test.jpg') !
                # Note: Another way to gain some time is to decimate data... DOne.
                writer.grab_frame()

    def probes(self, figsize=(9, 4)):
        """Plot acoustic pressure at probe locations."""

        if not isinstance(self.data, Hdf5Wrapper):
            print('probes method only available for Hdf5Wrapper')
            sys.exit(1)

        locs = self.data.get_dataset('probe_locations').tolist()

        if not locs:
            raise ViewerError("No probes !")

        p = self.data.get_dataset('probe_values')
        t = _np.arange(self.cfg.sol.nt) * self.cfg.dt

        _, ax = _plt.subplots(figsize=figsize)
        for i, c in enumerate(locs):
            ax.plot(t, p[i, :] - self.cfg.tp.p0,
                    label=f'@{tuple([self.axis[i][tuple(c)] for i in range(len(p.shape))])}')
        ax.set_xlim(t.min(), t.max())
        ax.set_xlabel('Time [s]')
        ax.set_ylabel('Pressure [Pa]')
        ax.legend()
        ax.grid()
        _plt.show()

    def spectrogram(self, M=None, figsize=(9, 4)):
        """Plot spectograms at probe locations.

        Parameters
        ----------
        M : int
            Length of each segment
        """

        probes = self.data.get_dataset('probe_locations').tolist()

        if not probes:
            raise ViewerError("No probes !")

        if not M:
            M = min(int(self.cfg.sol.nt/20), 256)

        p = self.data.get_dataset('probe_values')

        fig, ax = _plt.subplots(p.shape[0], figsize=figsize, tight_layout=True)

        if p.shape[0] == 1:
            ax = _np.array([ax, ])

        for i, c in enumerate(probes):

            freqs, times, Sx = _signal.spectrogram(p[i, :] - self.cfg.tp.p0,
                                                   nperseg=M,
                                                   fs=1 / self.cfg.dt,
                                                   scaling='spectrum')
            Sx =  10 * _np.log10(abs(Sx))
            im = ax[i].pcolormesh(times, freqs / 1000, Sx, cmap="Greys")
            ax[i].set_ylabel('Frequency [kHz]')
            if i != len(probes) - 1:
                ax[i].set_xticks([])

            fig.colorbar(im, ax=ax[i], label=f'probe {i}')

        ax[-1].set_xlabel('Time [s]')
        ax[0].set_title('Square spectrum magitude')
        _plt.show()

    def close(self):
        """Close hdf5 file if one is open."""
        if isinstance(self.data, Hdf5Wrapper):
            self.data.close()
            self.closed = True

    def __enter__(self):
        return self

    def __exit__(self, mtype, value, traceback):
        self.close()


class PlyViewer:
    """Legacy Mesh/ComputationDomain viewer using Plotly."""

    def __init__(self, obj):
        self.shape = obj.shape
        self.ndim = len(self.shape)
        self.obstacles = obj.obstacles
        self.traces = []

        self.x = getattr(obj, 'x', _np.arange(self.shape[0]))
        self.y = getattr(obj, 'y', _np.arange(self.shape[1]))

        self.xdomains = obj.xdomains
        self.ydomains = obj.ydomains

        if len(self.shape) == 3:
            self.z = getattr(obj, 'z', _np.arange(self.shape[1]))
            self.zdomains = obj.zdomains

    @staticmethod
    def _grid_traces(ax1, ax2):
        """Make grid traces."""
        traces = []
        kwargs = dict(mode='lines', line={'color': 'rgba(0,0,0,0.1)'})

        x = _np.ones_like(ax2)
        for ix in ax1:
            traces.append(_go.Scatter(x=ix * x, y=ax2, **kwargs))

        y = _np.ones_like(ax1)
        for iy in ax2:
            traces.append(_go.Scatter(x=ax1, y=iy * y, **kwargs))

        return traces

    def _object_traces(self, ax1, ax2, side=None, reverse=None, kind='obstacle', bounds=False):
        """Make obstacles traces."""
        traces = []

        if kind == 'domains':
            if bounds:
                obj = self.domains
            else:
                obj = self.domains.inner_objects
            kwargs = {'fill': "toself", 'fillcolor': 'rgba(0.39, 0.98, 0.75, 0.1)',
                      'line': {'color': 'rgba(0.39, 0,98, 0.75)'}}
        else:
            obj = self.obstacles
            kwargs = {'fill': "toself", 'fillcolor': 'rgba(0, 0, 0, 0.1)',
                      'fillpattern': {'shape': 'x'},
                      'line': {'color': 'rgba(0, 0, 0)'}}

        if self.ndim != 3:
            for obs in obj:
                ix, iy = obs.vertices
                traces.append(_go.Scatter(x=ax1[ix, ], y=ax2[iy, ],
                                          name=f'n{obs.sid} [{obs.tag}]',
                                          **kwargs
                                          ))
        elif side:
            for face in getattr(obj.faces, side):
                ix, iy = face.vertices[face.not_axis, :]
                if reverse == 'reversed':
                    ix, iy = iy, ix
                traces.append(_go.Scatter(x=ax1[ix], y=ax2[iy], name=f'obs{face.sid}', **kwargs))

        return traces

    def show(self, dpi=800, obstacles=True, domains=False, bounds=True, only_mesh=False):
        """Plot grid.

        todo :
            - BC profiles, figsize, Buffer Zone, probes, filename
            - Take one division over N(=4)
            - evolution of the (dx, dy, dz) steps
        """
        if self.ndim == 3:
            fig = self._grid3d(obstacles=obstacles, domains=domains, bounds=bounds,
                               only_mesh=only_mesh)
            width, height = fig_scale((self.x, self.z), (self.y, self.z), ref=dpi)
        else:
            fig = self._grid2d(obstacles=obstacles, domains=domains, bounds=bounds)
            width, height = fig_scale(self.x, self.y, ref=dpi)

        fig.update_layout(showlegend=False, height=height, width=width,
                          plot_bgcolor='rgba(0,0,0,0)')
        fig.show()

    def _grid2d(self, obstacles=True, domains=False, bounds=False):
        """Show 2d grid."""
        fig = _go.Figure()
        fig.add_traces(self._grid_traces(self.x, self.y))
        if self.obstacles and obstacles:
            fig.add_traces(self._object_traces(self.x, self.y, kind='obstacles'))
        if domains:
            fig.add_traces(self._object_traces(self.x, self.y, kind='domains', bounds=bounds))
        fig.update_xaxes(title=r'$x \, [m]$',
                         autorange=False, automargin=True,
                         range=[self.x.min(), self.x.max()],
                         )
        fig.update_yaxes(title=r'$y \, [m]$',
                         scaleanchor="x",
                         autorange=False, automargin=True,
                         range=[self.y.min(), self.y.max()],
                         )
        return fig

    def _grid3d(self, obstacles=True, domains=False, bounds=False, only_mesh=False):
        """Show 3d grid."""
        # Figure
        if only_mesh:
            fig = _go.Figure()
            fig.add_traces(self._mesh3d(obstacles=obstacles, domains=domains, bounds=True))
        else:
            fig = make_subplots(rows=2, cols=2,
                                horizontal_spacing=0.01, vertical_spacing=0.01,
                                subplot_titles=("(T)", "(R)", "(F)", ""),
                                shared_xaxes=True, shared_yaxes=True,
                                column_widths=fig_scale(self.x, self.z),
                                row_heights=fig_scale(self.y, self.z),
                                specs=[[{"type": "xy"}, {"type": "xy"}],
                                       [{"type": "xy"}, {"type": "scene"}]])

            axis = zip((1, 1, 2), (1, 2, 1),
                       ('top', 'right', 'front'),
                       (True, 'reversed', True),
                       ('x', 'x2', 'x3'),
                       ((r'', self.x),
                        (r'$z \, [m]$', self.z),
                        ('$x \, [m]$', self.x)),
                       ((r'$y \, [m]$', self.y),
                        (r'', self.y),
                        ('$z \, [m]$', self.z)))

            for row, col, side, rev, anchor, (ax1l, ax1), (ax2l, ax2) in axis:

                fig.add_traces(self._grid_traces(ax1, ax2), rows=row, cols=col)
                if self.obstacles and obstacles:
                    fig.add_traces(self._object_traces(ax1, ax2, side, rev,
                                   kind='obstacles'),
                                   rows=row, cols=col)
                if domains:
                    fig.add_traces(self._object_traces(ax1, ax2, side, rev,
                                   kind='domains', bounds=bounds),
                                   rows=row, cols=col)

                fig.update_xaxes(row=row, col=col,
                                 title=ax1l,
                                 autorange=rev, automargin=True,
                                 #range=[ax1.min(), ax1.max()],
                                 )
                fig.update_yaxes(row=row, col=col,
                                 title=ax2l,
                                 scaleanchor=anchor,
                                 autorange=True, automargin=True,
                                 #range=[ax2.min(), ax2.max()],
                                 )

            fig.add_traces(self._mesh3d(obstacles=obstacles, domains=domains, bounds=bounds),
                           rows=2, cols=2)

        return fig

    def _mesh3d(self, obstacles=True, domains=False, bounds=True):

        data = []

        if obstacles:
            for sub in self.obstacles:
                data.append(_go.Mesh3d(x=sub.vertices[0],
                                       y=sub.vertices[1],
                                       z=sub.vertices[2],
                                       intensity=_np.linspace(0, 1, 8, endpoint=True),
                                       name='y',
                                       opacity=1,
                                       alphahull=0,
                                       showscale=False,
                                       flatshading=True   # to hide the triangles
                                       ))

        if domains:
            if bounds:
                domains = self.domains
            else:
                domains = self.domains.inner_objects

            for sub in domains:
                data.append(_go.Mesh3d(x=sub.vertices[0],
                                       y=sub.vertices[1],
                                       z=sub.vertices[2],
                                       hovertext=str(sub.tag),
                                       #colorscale=[[0, 'gold'],
                                       #            [0.5, 'mediumturquoise'],
                                       #            [1, 'magenta']],
                                       intensity=_np.linspace(0, 1, 8, endpoint=True),
                                       # i, j and k give the vertices of triangles
                                       #i = [7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2],
                                       #j = [3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3],
                                       #k = [0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6],
                                       opacity=0.5,
                                       alphahull=1,
                                       showscale=True,
                                       flatshading=True   # to hide the triangles
                                       ))
        return data
