import numpy as np

G = 6.67430e-11
M_earth = 5.972e24
R_earth = 6371e3
omega = 7.292115e-5
r_geo = (G * M_earth / omega**2)**(1/3)
geo_alt_km = (r_geo - R_earth) / 1000
GEO_ALT_KM = geo_alt_km
TETHER_TOP_KM = 100_000.0  # counterweight altitude in km

rho_cnt = 1300      # kg/m³
sigma_cnt = 50e9    # Pa (conservative)

def effective_accel(r):
    return omega**2 * r - G * M_earth / r**2

def taper_ratio(r):
    exponent = (rho_cnt / sigma_cnt) * (G * M_earth * (1/R_earth - 1/r) - 0.5 * omega**2 * (r**2 - R_earth**2))
    return np.exp(exponent)