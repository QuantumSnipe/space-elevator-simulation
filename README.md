# Space Elevator Simulator

A physics-based 3D simulation of space elevator, built in VPython. The climber ascends from 100 km altitude to geostationary orbit and beyond, driven by real orbital mechanics - not canned animations.

## What it simulates

- **Climber dynamics** - ODE-integrated trajectory with a PD velocity controller targeting 55.6 m/s (~200 km/h). Effective gravity transitions from downward (below GEO) through zero (at GEO) to outward (above GEO).
- **Coriolis tether waves** - Finite-difference wave propagation along the tether, driven by the Coriolis force the climbing mass exerts. Tapered mass density and tension from the CNT cross-section profile.
- **Tether tapering** - Cross-section follows the exponential taper ratio for a carbon nanotube ribbon under constant stress, thickest at GEO altitude.
- **Proper scale mapping** - A power-law visual compression (`alt^0.45`) keeps near-surface detail visible while still showing GEO and the 100,000 km counterweight.

## 3D Visualization

The main visualization (`space_elevator_3d.py`) shows:

- Textured spinning Earth with 23.44° axial tilt and atmosphere glow
- Tapered tether with physically-computed Coriolis wave deflections
- Climber box with trail, tracking the ODE solution
- GEO marker ring at 35,786 km
- Counterweight at 100,000 km
- Live HUD: altitude, velocity, effective-g, elapsed time, force-balance phase
- Time warp slider (10 min to 10 hours per visual second)
- Pause/resume control

## Project structure

- `constants.py` - Physical constants, GEO radius, effective gravity, taper ratio.
- `climber_dynamics.py` - Standalone climber ODE solver and plots.
- `taper_analysis.py` - Tether taper profile and summary metrics.
- `tether_waves.py` - Finite-difference tether wave simulation.
- `simulation_ui.py` - Integrated UI to run and compare all three model views.
- `UI_SPEC.md` - UI architecture and implementation specification.

## Run

Install dependencies:

```bash
pip install -r requirements.txt
```

Launch integrated UI:

```bash
python simulation_ui.py
```

Launch standalone scripts:

```bash
python climber_dynamics.py
python taper_analysis.py
python tether_waves.py
```

## Integrated UI Modes

- `Climber`:
  - Interactive run/pause/step/reset.
  - Live altitude/time and velocity/altitude plots.
  - Transparency panel with equations and runtime values.
- `Taper`:
  - Uses `taper_analysis.analyze_taper(...)`.
  - Shows area ratio and normalized linear density profiles.
  - Displays key taper metrics (GEO/peak/top ratios).
- `Waves`:
  - Uses `tether_waves.simulate_tether_waves(...)`.
  - Shows final tether deflection and amplitude-over-time.
  - Displays stability diagnostics (CFL estimate).
