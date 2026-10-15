"""Analyst-side measurements of stones, pieces and cracks (step 5).

Not a physics module: the agent world of round 2 must not import it (api.md).
Nothing here feeds back into fracture; it only reads geometry and damage.

Conventions (2D sections made by ``stone.make_core``): the platform is the
top face (outward normal +y), the platform edge is at ``meta["edge_m"]`` and
the exterior face leaves the edge downward on the +x side.

Dibble measures (02 sec. 5.1):

- PD, platform depth: distance on the platform from the point of percussion
  to the exterior platform edge (Dibble & Rezek 2009; the flake attribute
  ``platthick`` in the Li et al. 2023 data).
- EPA, exterior platform angle: angle between the platform and the exterior
  face at the edge, measured through the stone.
- AOB, angle of blow: angle between the hammer trajectory and the
  perpendicular of the platform; 0 = perpendicular blow, positive = the
  trajectory leans outward, toward the exterior face (Dibble & Rezek 2009 as
  summarised by Li et al. 2022, JAMT, doi:10.1007/s10816-022-09586-2; the
  data hold -20..50 deg). The sign convention was taken from that summary,
  not from the primary text (02 sec. 5.1).
"""
from __future__ import annotations

from dataclasses import dataclass
import math

import contourpy
import numpy as np

from .stone import Stone


# ---------------------------------------------------------------- Dibble set
def platform_depth_m(core: Stone, contact_point_m) -> float:
    """PD of a planned blow: edge x minus contact x along the platform."""
    edge_x = float(core.meta["edge_m"][0])
    return edge_x - float(np.asarray(contact_point_m, dtype=float)[0])


def flake_platform_depth_m(flake: Stone, core: Stone) -> float:
    """PD measured on a detached piece: length of the unbroken run of original
    platform surface it carries, starting at the platform edge and going
    inward (0 if the piece does not carry the edge cell). Uses the cells of
    the piece in the top row of the original core. V2 uses the planned PD
    (``platform_depth_m``), as Dibble's controlled experiments did; this one
    is for reporting only."""
    h = core.cell_size_m
    top_row = core.cells.shape[0] - 1
    top_y = core.origin_m[1] + (top_row + 1) * h  # upper face of the top row
    rows = np.argwhere(flake.cells > 0)
    y_top = flake.origin_m[1] + (rows[:, 0] + 1) * h
    on_top = np.abs(y_top - top_y) < 0.5 * h
    if not on_top.any():
        return 0.0
    # core column index of each top-row cell of the piece
    cols = np.round((flake.origin_m[0] - core.origin_m[0]) / h).astype(int) + rows[on_top, 1]
    core_top = np.flatnonzero(core.cells[top_row] > 0)
    edge_col = int(core_top.max())
    have = set(cols.tolist())
    if edge_col not in have:
        return 0.0
    c = edge_col
    while c - 1 in have:
        c -= 1
    edge_x = float(core.meta["edge_m"][0])
    return max(0.0, edge_x - (core.origin_m[0] + c * h))


def exterior_platform_angle_deg(stone: Stone, window_m: float) -> float:
    """EPA of a core (before a blow; not meant for broken pieces, whose right
    boundary may be a fracture surface): x of the right boundary of each row within
    ``window_m`` below the top face, fitted x = a + k y; EPA = acos(k / sqrt(1 + k^2))
    (k = cot EPA for ``make_core``)."""
    h = stone.cell_size_m
    ny = stone.cells.shape[0]
    n_rows = max(2, int(round(window_m / h)))
    ys, xs = [], []
    for r in range(ny - 1, max(-1, ny - 1 - n_rows), -1):
        cols = np.flatnonzero(stone.cells[r] > 0)
        if cols.size:
            ys.append(stone.origin_m[1] + (r + 0.5) * h)
            xs.append(stone.origin_m[0] + (cols.max() + 1) * h)
    if len(ys) < 2:
        raise ValueError("window holds fewer than 2 rows")
    k = np.polyfit(ys, xs, 1)[0]
    return math.degrees(math.acos(k / math.sqrt(1.0 + k * k)))


def angle_of_blow_deg(direction, platform_normal=(0.0, 1.0), outward=(1.0, 0.0)) -> float:
    """Signed AOB of a hammer moving along ``direction`` (into the stone).
    ``platform_normal`` points out of the platform, ``outward`` along the
    platform toward the exterior edge. AOB = atan2(v.outward, -v.normal)."""
    v, n, e = (np.asarray(a, dtype=float) for a in (direction, platform_normal, outward))
    norms = [float(np.linalg.norm(a)) for a in (v, n, e)]
    if min(norms) == 0.0:
        raise ValueError("zero vector")
    v, n, e = v / norms[0], n / norms[1], e / norms[2]
    if abs(float(n @ e)) > 1e-9:
        raise ValueError("outward must lie in the platform (perpendicular to its normal)")
    if float(v @ n) >= 0.0:
        raise ValueError("the hammer must move into the platform")
    return math.degrees(math.atan2(float(v @ e), -float(v @ n)))


def blow_direction(aob_deg: float, platform_normal=(0.0, 1.0), outward=(1.0, 0.0)) -> np.ndarray:
    """Unit hammer direction for a given AOB (inverse of ``angle_of_blow_deg``)."""
    a = math.radians(aob_deg)
    return math.sin(a) * np.asarray(outward, dtype=float) - math.cos(a) * np.asarray(platform_normal, dtype=float)


# ----------------------------------------------------------- size and count
def section_area_m2(stone: Stone) -> float:
    """Area of a 2D section (filled cells x h^2)."""
    if stone.dim != 2:
        raise ValueError("section area is for 2D stones")
    return stone.n_cells * stone.cell_size_m ** 2


def flakes(pieces: list) -> list:
    """Detached pieces: all but the heaviest (``pieces`` heaviest first, as
    returned by ``strike``)."""
    return list(pieces[1:])


def count_pieces(pieces: list, min_mass_kg: float = 0.0) -> int:
    return sum(1 for p in pieces if p.mass_kg > min_mass_kg)


# --------------------------------------------------------------- cone angle
@dataclass(frozen=True)
class ConeFit:
    included_angle_deg: float  # 2 x angle between crack and axis
    half_angle_deg: float
    n_bins: int  # depth bins holding crack nodes, used in the fit
    rms_m: float  # rms lateral residual of the bin centres about the line
    depth_range_m: tuple


# measurement choice, fixed before any V1/V6 run: the ring crack leaves the
# surface steeply before it turns into the cone (Lawn 1993, Fracture of
# Brittle Solids, sec. 8.2), so the fit uses depths >= this fraction of the
# deepest crack node
CONE_MIN_DEPTH_FRACTION = 0.25
CONE_BINS = 20


def cone_angle(points_m, d, apex_m, axis, threshold: float = 0.95, side: float = 1.0,
               min_lateral_m: float = 0.0, min_depth_fraction: float = CONE_MIN_DEPTH_FRACTION,
               n_bins: int = CONE_BINS) -> ConeFit:
    """Fit the crack centre line from nodal damage ``d`` at ``points_m``.

    Depth t = (p - apex).axis, lateral s = side * (p - apex).perp with perp =
    axis rotated +90 deg (axisymmetric: apex on the axis at the surface,
    axis = (0, -1) and side = +1 give s = r). Crack nodes: d >= threshold and s
    > min_lateral_m. Depths from min_depth_fraction x max to max are cut into
    ``n_bins`` equal bins; in each bin the d-weighted mean (t, s) is one point
    (so mesh grading does not weight the fit); s = a + b t by least squares;
    half angle = atan(b). A negative angle means the crack runs back toward
    the axis (reported as is, not folded)."""
    p = np.asarray(points_m, dtype=float)
    ax = np.asarray(axis, dtype=float)
    ax = ax / np.linalg.norm(ax)
    perp = np.array([-ax[1], ax[0]])
    rel = p - np.asarray(apex_m, dtype=float)
    t = rel @ ax
    s = side * (rel @ perp)
    d = np.asarray(d, dtype=float)
    sel = (d >= threshold) & (s > min_lateral_m) & (t > 0)
    if sel.sum() < 2:
        raise ValueError("fewer than 2 crack nodes")
    t, s, w = t[sel], s[sel], d[sel]
    t_max = float(t.max())
    t_min = min_depth_fraction * t_max
    edges = np.linspace(t_min, t_max, n_bins + 1)
    tc, sc = [], []
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (t >= lo) & (t <= hi)
        if m.any():
            tc.append(float(np.average(t[m], weights=w[m])))
            sc.append(float(np.average(s[m], weights=w[m])))
    if len(tc) < 2:
        raise ValueError("crack spans fewer than 2 depth bins")
    tc, sc = np.array(tc), np.array(sc)
    b, a = np.polyfit(tc, sc, 1)
    half = math.degrees(math.atan(b))
    rms = float(np.sqrt(np.mean((sc - (a + b * tc)) ** 2)))
    return ConeFit(included_angle_deg=2.0 * half, half_angle_deg=half, n_bins=len(tc), rms_m=rms,
                   depth_range_m=(t_min, t_max))


# ------------------------------------------------------- edge angle, tip radius
def outline(stone: Stone) -> np.ndarray:
    """Closed outer boundary of a 2D stone, (n, 2) in m, counter-clockwise:
    the 0.5 level line of the filled-cell indicator sampled at cell centres
    (marching squares, contourpy); the longest line is the outer boundary
    (inner holes, if any, are not part of it)."""
    if stone.dim != 2:
        raise ValueError("outline is for 2D stones")
    from scipy import ndimage

    if ndimage.label(stone.cells > 0, structure=np.ones((3, 3)))[1] != 1:
        raise ValueError("outline needs a single connected piece")
    return _mask_outline(stone.cells > 0, stone.cell_size_m, stone.origin_m[:2])


def _mask_outline(mask: np.ndarray, h: float, origin) -> np.ndarray:
    f = np.pad(mask.astype(float), 1)
    x = origin[0] + (np.arange(f.shape[1]) - 0.5) * h
    y = origin[1] + (np.arange(f.shape[0]) - 0.5) * h
    lines = contourpy.contour_generator(x, y, f).lines(0.5)
    line = max(lines, key=len)
    if np.allclose(line[0], line[-1]):
        line = line[:-1]
    area2 = float(np.sum(line[:, 0] * np.roll(line[:, 1], -1) - np.roll(line[:, 0], -1) * line[:, 1]))
    return line if area2 > 0 else line[::-1]


def _arc(line: np.ndarray) -> tuple[np.ndarray, float]:
    seg = np.linalg.norm(np.roll(line, -1, axis=0) - line, axis=1)
    return np.concatenate([[0.0], np.cumsum(seg)[:-1]]), float(seg.sum())


def _side_points(line, arc, total, i, lo_m, hi_m, sign):
    """Points at arc distance in [lo, hi] from vertex i going forward (+1) or back (-1)."""
    dist = (sign * (arc - arc[i])) % total
    m = (dist >= lo_m) & (dist <= hi_m)
    return line[m]


def _fit_direction(points: np.ndarray, tip: np.ndarray) -> np.ndarray:
    """Unit direction of the principal axis of ``points``, oriented away from ``tip``."""
    c = points.mean(axis=0)
    _, _, vt = np.linalg.svd(points - c, full_matrices=False)
    v = vt[0]
    return v if (c - tip) @ v > 0 else -v


@dataclass(frozen=True)
class EdgeFit:
    tip_m: np.ndarray  # outline vertex at the edge
    angle_deg: float  # included angle between the two faces (through the stone)
    tip_radius_m: float  # circle fitted to the outline within tip_window of the tip
    tip_fit_rms_m: float  # rms distance of those points from the fitted circle
    grid_limited: bool  # radius < GRID_LIMIT_FACTOR x the radius of an ideal sharp wedge on this grid
    grid_radius_m: float  # that ideal-wedge radius (``grid_tip_radius_m``)
    window_m: tuple  # (inner, outer) arc distance of the face fits


# numerical choice: a tip whose fitted radius is below twice the radius the
# grid gives an ideal (zero radius) wedge of the same angle is not resolved
GRID_LIMIT_FACTOR = 2.0


def edge_at(stone: Stone, tip_index: int, face_window_m: tuple, tip_window_m: float,
            line: np.ndarray | None = None) -> EdgeFit:
    """Edge angle and tip radius at outline vertex ``tip_index``.

    Each face is the principal line of the outline points at arc distance
    ``face_window_m = (inner, outer)`` from the tip on that side (inner > 0
    skips the rounded tip). Included angle = angle between the two face
    directions (both pointing away from the tip). Tip radius: algebraic circle
    fit (Kasa 1976, IEEE Trans. Instrum. Meas. 25:8) to outline points within
    ``tip_window_m`` of the tip; it cannot be smaller than the grid can show
    (02 sec. 5.4)."""
    line = outline(stone) if line is None else line
    arc, total = _arc(line)
    tip = line[tip_index]
    lo, hi = face_window_m
    a = _side_points(line, arc, total, tip_index, lo, hi, +1)
    b = _side_points(line, arc, total, tip_index, lo, hi, -1)
    if len(a) < 2 or len(b) < 2:
        raise ValueError("face window holds fewer than 2 outline points on a side")
    va, vb = _fit_direction(a, tip), _fit_direction(b, tip)
    angle = math.degrees(math.acos(float(np.clip(va @ vb, -1.0, 1.0))))
    near = np.concatenate([_side_points(line, arc, total, tip_index, 0.0, tip_window_m, +1),
                           _side_points(line, arc, total, tip_index, 0.0, tip_window_m, -1)])
    near = np.unique(near, axis=0)
    radius, rms = _circle_fit(near)
    grid_r = grid_tip_radius_m(angle, stone.cell_size_m, tip_window_m)
    return EdgeFit(tip_m=tip, angle_deg=angle, tip_radius_m=radius, tip_fit_rms_m=rms,
                   grid_limited=bool(radius < GRID_LIMIT_FACTOR * grid_r), grid_radius_m=grid_r,
                   window_m=(lo, hi))


# grid phases tried by ``grid_tip_radius_m``: bisector directions (deg) and
# sub-cell apex offsets (in h); the largest radius over all of them is used
GRID_ORIENTATIONS_DEG = (0.0, 15.0, 30.0, 45.0)
GRID_OFFSETS = ((0.0, 0.0), (0.37, 0.29), (0.5, 0.5), (0.81, 0.13))


def grid_tip_radius_m(angle_deg: float, h: float, tip_window_m: float) -> float:
    """Tip radius that ``edge_at`` measures on an ideal sharp wedge of
    ``angle_deg`` rasterised on cells of size h: the largest over the bisector
    directions and apex offsets above (the grid can hide a tip at least this
    round, whatever its phase)."""
    return max(_ideal_wedge_radius(angle_deg, h, tip_window_m, phi, off)
               for phi in GRID_ORIENTATIONS_DEG for off in GRID_OFFSETS)


def _ideal_wedge_radius(angle_deg, h, tip_window_m, bisector_deg, offset):
    half = math.radians(angle_deg) / 2.0
    reach = 4.0 * tip_window_m + 4.0 * h
    n = int(math.ceil(2.0 * reach / h)) + 4
    apex = (0.5 * n + np.asarray(offset, dtype=float)) * h
    c = (np.arange(n) + 0.5) * h
    X, Y = np.meshgrid(c, c)
    b = math.radians(bisector_deg)
    along = (X - apex[0]) * math.cos(b) + (Y - apex[1]) * math.sin(b)
    across = -(X - apex[0]) * math.sin(b) + (Y - apex[1]) * math.cos(b)
    # sector of radius ~reach/2, far side cut flat: the other corners are >= 90 deg
    far = 0.5 * reach * math.cos(min(half, math.radians(60.0)))
    mask = (along >= 0) & (along <= far) & (np.abs(across) <= along * math.tan(half))
    line = _mask_outline(mask, h, (0.0, 0.0))
    i = int(np.argmin(np.linalg.norm(line - apex, axis=1)))
    arc, total = _arc(line)
    near = np.concatenate([_side_points(line, arc, total, i, 0.0, tip_window_m, +1),
                           _side_points(line, arc, total, i, 0.0, tip_window_m, -1)])
    return _circle_fit(np.unique(near, axis=0))[0]


def _circle_fit(p: np.ndarray) -> tuple[float, float]:
    """(radius, rms residual) of the Kasa fit x^2 + y^2 + D x + E y + F = 0
    by least squares; (inf, inf) for fewer than 3 points or a line."""
    if len(p) < 3:
        return math.inf, math.inf
    c = p.mean(axis=0)
    scale = max(float(np.abs(p - c).max()), 1e-300)
    q = (p - c) / scale
    A = np.column_stack([q[:, 0], q[:, 1], np.ones(len(q))])
    rhs = -(q[:, 0] ** 2 + q[:, 1] ** 2)
    sol, *_ = np.linalg.lstsq(A, rhs, rcond=None)
    r2 = (sol[0] ** 2 + sol[1] ** 2) / 4.0 - sol[2]
    if r2 <= 0:
        return math.inf, math.inf
    r = math.sqrt(r2)
    centre = -0.5 * sol[:2]
    rms = float(np.sqrt(np.mean((np.linalg.norm(q - centre, axis=1) - r) ** 2)))
    return r * scale, rms * scale


def sharpest_edge(stone: Stone, face_window_m: tuple, tip_window_m: float) -> EdgeFit:
    """Edge at the outline vertex with the smallest included angle, judged by
    the chords to the points at arc distance ``face_window_m[1]`` on each side
    (convex corners only: the stone lies inside the angle)."""
    line = outline(stone)
    arc, total = _arc(line)
    hi = face_window_m[1]
    fwd = np.searchsorted(arc, (arc + hi) % total)
    back = np.searchsorted(arc, (arc - hi) % total)
    fwd %= len(line)
    back %= len(line)
    u = line[fwd] - line
    v = line[back] - line
    cosang = np.einsum("ij,ij->i", u, v) / (np.linalg.norm(u, axis=1) * np.linalg.norm(v, axis=1) + 1e-300)
    convex = (u[:, 0] * v[:, 1] - u[:, 1] * v[:, 0]) > 0  # ccw outline: stone left of the forward path
    score = np.where(convex, cosang, -np.inf)
    return edge_at(stone, int(np.argmax(score)), face_window_m, tip_window_m, line=line)
