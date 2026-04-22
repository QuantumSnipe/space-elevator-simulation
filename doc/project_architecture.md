# Space Elevator Simulator UI Specification

## 1. Goal

Build an interactive desktop UI that makes the simulation controllable and transparent:

- Users can configure physics and controller parameters.
- Users can run/pause/step/reset the model.
- Users can see exactly how values are computed at runtime.
- Users can compare multiple simulation runs.

This spec is designed for the current Python stack (`numpy`, `scipy`, `matplotlib`), with optional future migration to VPython or a web front end.

## 2. Current Codebase Mapping

- `constants.py`
  - Physical constants, GEO calculations, taper model (`effective_accel`, `taper_ratio`).
- `climber_dynamics.py`
  - ODE model (`climber_ode`) and trajectory solve via `solve_ivp`.
  - Plotting for altitude, velocity, and effective acceleration.

UI should be a thin layer around a refactored simulation service extracted from `climber_dynamics.py`.

## 3. Architecture

### 3.1 Layers

1. Core Physics Layer
- Pure functions for physics and controller logic.
- No UI imports.

2. Simulation Engine Layer
- State machine: idle/running/paused/completed/error.
- Step integration over fixed `dt`.
- Captures time-series outputs and diagnostics.

3. UI Layer
- Renders controls, live scene, plots, and transparency panel.
- Sends user actions as events to the engine.

### 3.2 Proposed Files

- `sim/physics.py` (from `constants.py` + model helpers)
- `sim/engine.py` (simulation state, stepping, run lifecycle)
- `sim/types.py` (dataclasses for config/state/results)
- `ui/app.py` (main window + layout)
- `ui/panels/controls.py`
- `ui/panels/transparency.py`
- `ui/panels/plots.py`
- `ui/panels/scene.py`
- `ui/panels/compare.py`

## 4. Primary UI Layout

Desktop layout (single window):

- Left column (25% width): `Controls` + `Validation` + `Presets`.
- Center (45% width): `Live Scene` (2D radial view initially).
- Right column (30% width): `How It Works` transparency panel.
- Bottom full-width strip: `Time-Series Plots` with tabbed charts.

Mobile/small-window fallback:
- Vertical stacking in this order: Controls -> Scene -> Transparency -> Plots.

## 5. Panel Specifications

### 5.1 Controls Panel

Inputs:
- `start_altitude_km` (default `100`)
- `target_velocity_mps` (default `55.6`)
- `payload_mass_kg` (default `10000`)
- `kp_velocity` (default `0.5`)
- `sim_duration_hr` (default `192`)
- `dt_sec` (default `10`)
- `integrator` (`RK45`, `DOP853`)
- `tether_top_km` (default from constants: `100000`)

Buttons:
- `Run`
- `Pause`
- `Step` (advance by 1 `dt_sec`)
- `Reset`
- `Save Run`
- `Export CSV`
- `Export JSON`

Validation rules:
- `dt_sec > 0`
- `target_velocity_mps >= 0`
- `start_altitude_km >= 0`
- `sim_duration_hr > 0`
- Warning if `dt_sec > 120` (coarse integration)
- Warning if `start_altitude_km > tether_top_km`

### 5.2 Live Scene Panel

Phase 1 (Matplotlib 2D):
- Earth as circle.
- Tether as radial line.
- GEO ring marker.
- Climber marker moving over time.
- Counterweight marker at tether top.
- Optional color map on tether for normalized tension.

HUD overlay:
- Sim time
- Altitude
- Radial velocity
- Effective acceleration
- Distance to GEO
- Engine status

### 5.3 Transparency Panel ("How It Works")

Sections:
1. Equations (static rendered text)
- `g_eff(r) = omega^2 * r - G*M/r^2`
- `a_cmd = kp * (v_target - v_r)`
- `dv_r/dt = g_eff + u_motor` (with current control decomposition)

2. Runtime values (updates each frame)
- `r`, `altitude_km`, `v_r`, `g_eff`, `a_cmd`, `u_motor`, `dv_r/dt`

3. Assumptions
- 1D radial motion
- Perfect motor authority in current control form
- No wind/aerodynamic drag
- Rigid radial tether representation for climber dynamics

4. Units legend
- SI base units, with displayed conversions (km, hr).

### 5.4 Plots Panel

Tabs:
- `Altitude vs Time`
- `Velocity vs Time`
- `Effective g vs Altitude`
- `Control Acceleration vs Time`
- `Safety Margin` (if tether stress model is enabled)

Features:
- Live cursor with synchronized time index.
- Toggle GEO reference line.
- Toggle linear/log y-scale where relevant.

### 5.5 Compare Runs Panel

Run management:
- Saved runs list with timestamp + key params.
- Select up to 3 runs for overlay.

Compare views:
- Altitude-time overlays.
- Velocity-time overlays.
- Summary table:
  - Time to GEO
  - Max radial velocity
  - Max |effective g|
  - Numerical warning count

## 6. Data Contracts

### 6.1 Config Dataclass

`SimulationConfig`:
- `start_altitude_km: float`
- `target_velocity_mps: float`
- `payload_mass_kg: float`
- `kp_velocity: float`
- `sim_duration_hr: float`
- `dt_sec: float`
- `integrator: str`
- `tether_top_km: float`

### 6.2 Runtime State Dataclass

`RuntimeState`:
- `status: Literal["idle","running","paused","completed","error"]`
- `t_sec: float`
- `r_m: float`
- `v_r_mps: float`
- `g_eff_mps2: float`
- `a_cmd_mps2: float`
- `u_motor_mps2: float`
- `dv_r_dt_mps2: float`
- `warnings: list[str]`

### 6.3 Result Dataclass

`SimulationResult`:
- `config: SimulationConfig`
- `time_sec: np.ndarray`
- `r_m: np.ndarray`
- `v_r_mps: np.ndarray`
- `g_eff_mps2: np.ndarray`
- `a_cmd_mps2: np.ndarray`
- `u_motor_mps2: np.ndarray`
- `status: str`
- `warnings: list[str]`

## 7. Event and Data Flow

1. User edits controls -> UI validates fields.
2. UI creates `SimulationConfig`.
3. UI sends `engine.reset(config)`.
4. `Run` -> engine enters `running`.
5. Timer loop calls `engine.step(dt)` repeatedly.
6. Engine computes new state via integrator and physics functions.
7. Engine appends data to buffers and emits `RuntimeState`.
8. UI panels subscribe to `RuntimeState` updates:
- Scene redraw
- Transparency values refresh
- Plots append points
9. On completion/error -> UI enables export/save actions.

## 8. Refactor Plan from Existing Code

Phase 1: Extract pure simulation API
- Move constants/functions into `sim/physics.py`.
- Convert `climber_ode` into engine-callable derivative function.
- Add dataclasses in `sim/types.py`.

Phase 2: Build minimal UI shell
- Matplotlib figure with subplots + controls using `matplotlib.widgets`.
- Implement Run/Pause/Step/Reset.

Phase 3: Add transparency and diagnostics
- Live equation/value panel.
- Validation and warnings surface.

Phase 4: Add saved-run compare and export
- Persist results in memory.
- CSV/JSON output for reproducibility.

Phase 5 (optional): richer rendering
- VPython scene integration or a web UI (e.g., Plotly Dash).

## 9. Acceptance Criteria

- User can run, pause, step, and reset without restarting app.
- Runtime values in transparency panel match engine state every frame.
- Charts update live and remain responsive for 8-day sim durations.
- At least one validation warning appears for intentionally bad inputs.
- Saved runs can be reloaded and overlaid.
- Exported JSON can reproduce the same run when re-imported.

## 10. Minimal MVP Scope (Recommended First Build)

- Controls: `start_altitude_km`, `target_velocity_mps`, `kp_velocity`, `dt_sec`, `sim_duration_hr`.
- Buttons: `Run/Pause/Step/Reset`.
- Scene: 2D radial climber visualization.
- Transparency: equation list + current numeric values.
- Plots: altitude-time and velocity-time.
- Export: JSON only.

This MVP gives immediate model observability with low implementation risk in the current stack.
