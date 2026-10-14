"""Physics of stone fracture (physics-loop round 1).

Modules:
- ``materials``: physical constants loaded from ``physics-loop/spec/materials.json``.
- ``stone``: ``Stone`` (2D or 3D cell body) and ``make_core``.

Analyst-side measurement lives in ``lithics.measure`` and must never be
imported by the physics modules or by the round-2 agent world.
"""
