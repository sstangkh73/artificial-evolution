import numpy as np
from lithics import phasefield as pf
orig = pf.solve_bounded
def wrap(A, b, lo, up, x0=None, max_iter=100, kkt_tol=1e-5):
    r = orig(A, b, lo, up, x0, max_iter, kkt_tol)
    if not r.converged:
        print("FAIL kkt", pf.kkt_residual(A, b, r.d, lo, up), "it", r.iterations, flush=True)
    return r
pf.solve_bounded = wrap
import runpy, sys
sys.argv = ['x'] + sys.argv[1:]
runpy.run_path('worklog/2026-10-15-physics-loop-r1/scratch/indent_probe.py', run_name='__main__')
