import sys, time, math
import numpy as np
from lithics import indentation as ind, phasefield as pf
from lithics.materials import load_material
G = load_material("glass_soda_lime")
gc, ell = pf.material_constants(G, "axisymmetric")
R = float(sys.argv[1]); budget = float(sys.argv[2]); hfac = float(sys.argv[3]); split = sys.argv[4]
fine = float(sys.argv[5])
m = ind.indentation_mesh(G, ell * hfac, fine, fine, float(sys.argv[6]), float(sys.argv[6]))
print("elements", len(m.elements), flush=True)
t = time.time()
r = ind.indent_with_budget(m, 0.0, -float(sys.argv[6]), R, budget, gc, ell, split=split, n_steps=10, max_iter=int(sys.argv[7]) if len(sys.argv)>7 else 100, progress=lambda k,dl,f,w,ok: print(k, '%.3g um %.4g N %.4g J %.1fs' % (dl*1e6, f, w, time.time()-t), ok, flush=True))
print("time", time.time() - t)
print("steps", r.steps, "conv", r.converged)
print("delta um", np.round(r.approach_m * 1e6, 2))
print("P N", np.round(r.force_n, 1))
print("W", np.round(r.work_j, 4), "Efrac", r.fracture_energy_j, "Eel", r.elastic_energy_j)
print("a mm", np.round(r.contact_radius_m * 1e3, 3))
# damage geometry
de = r.d[m.elements].mean(1); c = m.nodes[m.elements].mean(1)
br = de > 0.9
print("broken elements", br.sum())
if br.sum():
    rr, zz = c[br, 0], c[br, 1]
    print("r range mm", rr.min() * 1e3, rr.max() * 1e3, "z range mm", zz.min() * 1e3, zz.max() * 1e3)
    # top-most broken r, and fit angle of broken band with depth
    for zc in np.linspace(0, zz.min(), 8):
        sel = np.abs(zz - zc) < ell
        if sel.any(): print(" z %.3f mm: r %.3f..%.3f" % (zc * 1e3, rr[sel].min() * 1e3, rr[sel].max() * 1e3))
np.savez("worklog/2026-10-15-physics-loop-r1/scratch/probe.npz", d=r.d, nodes=m.nodes, el=m.elements)
