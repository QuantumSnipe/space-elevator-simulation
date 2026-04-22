import numpy as np
import matplotlib.pyplot as plt

from constants import R_earth, r_geo, TETHER_TOP_KM, taper_ratio


def radial_profile(top_alt_km: float = TETHER_TOP_KM, n_points: int = 2000):
    """Return radial grid and taper ratio A(r)/A_base from Earth surface to top altitude."""
    r_top = R_earth + top_alt_km * 1000.0
    r = np.linspace(R_earth, r_top, n_points)
    ratio = taper_ratio(r)
    return r, ratio


def normalized_linear_density(
    r: np.ndarray,
    area_ratio: np.ndarray,
    base_linear_density: float = 1.0,
):
    """
    Linear density profile normalized by base value.
    base_linear_density is kg/m at Earth surface.
    """
    _ = r  # reserved for future non-uniform material models
    return base_linear_density * area_ratio


def analyze_taper(top_alt_km: float = TETHER_TOP_KM, n_points: int = 2000):
    r, area_ratio = radial_profile(top_alt_km=top_alt_km, n_points=n_points)
    mu = normalized_linear_density(r, area_ratio, base_linear_density=1.0)

    geo_idx = np.argmin(np.abs(r - r_geo))
    peak_idx = np.argmax(area_ratio)

    summary = {
        "surface_ratio": float(area_ratio[0]),
        "geo_ratio": float(area_ratio[geo_idx]),
        "peak_ratio": float(area_ratio[peak_idx]),
        "peak_alt_km": float((r[peak_idx] - R_earth) / 1000.0),
        "top_ratio": float(area_ratio[-1]),
        "top_alt_km": float(top_alt_km),
    }
    return r, area_ratio, mu, summary


def plot_taper_analysis(r: np.ndarray, area_ratio: np.ndarray, mu: np.ndarray):
    alt_km = (r - R_earth) / 1000.0
    geo_alt_km = (r_geo - R_earth) / 1000.0

    fig, axs = plt.subplots(2, 1, figsize=(10, 9), sharex=True)

    axs[0].plot(alt_km, area_ratio, color="tab:blue", lw=2, label="A(r)/A_surface")
    axs[0].axvline(geo_alt_km, color="tab:red", ls="--", label="GEO")
    axs[0].set_ylabel("Area Ratio")
    axs[0].set_yscale("log")
    axs[0].grid(True, alpha=0.3)
    axs[0].legend()
    axs[0].set_title("Tether Taper Profile (CNT Ribbon)")

    axs[1].plot(alt_km, mu, color="tab:green", lw=2, label="mu(r)/mu_surface")
    axs[1].axvline(geo_alt_km, color="tab:red", ls="--", label="GEO")
    axs[1].set_xlabel("Altitude (km)")
    axs[1].set_ylabel("Normalized Linear Density")
    axs[1].set_yscale("log")
    axs[1].grid(True, alpha=0.3)
    axs[1].legend()

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    r, area_ratio, mu, summary = analyze_taper()

    print("Taper summary:")
    for k, v in summary.items():
        if "alt_km" in k:
            print(f"  {k}: {v:,.1f} km")
        else:
            print(f"  {k}: {v:,.3f}")

    plot_taper_analysis(r, area_ratio, mu)
