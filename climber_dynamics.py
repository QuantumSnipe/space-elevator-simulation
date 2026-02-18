import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

G = 6.67430e-11
M = 5.972e24
R = 6371e3
omega = 7.292115e-5
r_geo = (G * M / omega**2)**(1/3)

def effective_accel(r):
    return omega**2 * r - G * M / r**2   # + outward

def climber_ode(t, y, v_target=55.6):
    r, vr = y
    ge = effective_accel(r)
    kp = 0.5
    desired_a = kp * (v_target - vr)    # PD on velocity
    dvr_dt = ge + (-ge + desired_a)     # motor cancels ge + tracks speed
    return [vr, dvr_dt]

if __name__ == '__main__':
    y0 = [R + 100e3, 0.0]  # start 100 km up, vr=0
    t_span = [0, 8 * 24 * 3600]  # up to 8 days
    sol = solve_ivp(climber_ode, t_span, y0, args=(55.6,), method='RK45', rtol=1e-6, atol=1e-6, dense_output=True)

    t = np.linspace(0, sol.t[-1], 500)
    r_sol = sol.sol(t)[0]
    vr_sol = sol.sol(t)[1]
    alt = (r_sol - R) / 1000
    geo_alt = (r_geo - R) / 1000

    fig, axs = plt.subplots(3, 1, figsize=(10, 12))
    axs[0].plot(t / 3600, alt, 'b-', label='Climber altitude')
    axs[0].axhline(geo_alt, color='r', ls='--', label='GEO ~35,786 km')
    axs[0].set_xlabel('Time (hours)')
    axs[0].set_ylabel('Altitude (km)')
    axs[0].legend();
    axs[0].grid(True)

    axs[1].plot(alt, vr_sol, 'g-')
    axs[1].set_xlabel('Altitude (km)')
    axs[1].set_ylabel('Radial speed (m/s)')
    axs[1].grid(True)

    geff = effective_accel(r_sol)
    axs[2].plot(alt, geff, 'r-')
    axs[2].axhline(0, color='k', ls=':')
    axs[2].set_xlabel('Altitude (km)')
    axs[2].set_ylabel('Effective g (m/s², + = outward)')
    axs[2].grid(True)

    plt.tight_layout()
    plt.show()


