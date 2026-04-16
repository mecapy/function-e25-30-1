"""
Bolted joint calculator per NF E25-030-1.

Pure functional approach: simple functions, nothing else.
"""

import math
from typing import TypedDict


# Tightening tool dispersion classes (Table C.5)
TIGHTENING_DISPERSIONS = {
    "C10": 0.10,
    "C15": 0.15,
    "C20": 0.20,
    "C30": 0.30,
    "C50": 0.50,
}


class Bolt(TypedDict):
    d: float  # Nominal diameter (mm)
    p: float  # Thread pitch (mm)
    As: float  # Stress area (mm²)
    Re_min: float  # Minimum yield strength (MPa)
    quality_class: str  # Property class (e.g. "10.9")


class Joint(TypedDict):
    dh: float  # Clearance hole diameter (mm)
    do: float  # Outer diameter of bearing surface (mm)
    Rc: float  # Bearing resistance (MPa)
    mu_p_min: float  # Minimum friction coefficient at joint interface


class Loads(TypedDict):
    FA_max: float  # Maximum axial force (N)
    Ft_max: float  # Maximum transverse force (N)


class Tightening(TypedDict):
    mu_tot_min: float  # Minimum total friction coefficient
    mu_tot_max: float  # Maximum total friction coefficient
    precision_class: str  # Tightening precision class (e.g. "C20")


def F0_min(
    bolt: Bolt,
    assembly: Joint,
    loads: Loads,
    tightening: Tightening,
) -> float:
    """
    Minimum required preload to ensure no separation and no slip.

    Args:
        bolt: Bolt parameters
        assembly: Joint parameters
        loads: Applied loads
        tightening: Tightening parameters
    """
    Fa = loads["FA_max"]
    Ft = loads["Ft_max"]
    fmin = assembly["mu_p_min"]
    return Fa + Ft / fmin


def F0_max(
    bolt: Bolt,
    assembly: Joint,
    loads: Loads,
    tightening: Tightening,
) -> float:
    """
    Maximum allowable preload (90% of yield strength).

    Args:
        bolt: Bolt parameters
        assembly: Joint parameters
        loads: Applied loads
        tightening: Tightening parameters
    """
    d2 = bolt["d"] - 0.6495 * bolt["p"]
    deq = bolt["d"] - 0.9382 * bolt["p"]
    rm = (assembly["do"] + assembly["dh"]) / 4

    A = bolt["p"] / (2 * math.pi) + tightening["mu_tot_min"] * (0.577 * d2 + rm)

    sigma_target = 0.9 * bolt["Re_min"]
    term1 = (1 / (A * bolt["As"])) ** 2
    term2 = (
        3
        * (16 / (math.pi * deq**3)) ** 2
        * (1 - (tightening["mu_tot_min"] * rm) ** 2 / A)
    )

    Tmax = sigma_target / math.sqrt(term1 + term2)

    return Tmax / A


def tightening_torques(
    bolt: Bolt,
    assembly: Joint,
    loads: Loads,
    tightening: Tightening,
) -> dict:
    """
    Tightening torques (Table C.5).
    """
    d2 = bolt["d"] - 0.6495 * bolt["p"]
    deq = bolt["d"] - 0.9382 * bolt["p"]
    rm = (assembly["do"] + assembly["dh"]) / 4

    A = bolt["p"] / (2 * math.pi) + tightening["mu_tot_min"] * (0.577 * d2 + rm)

    sigma_target = 0.9 * bolt["Re_min"] * 1e-3
    term1 = (1 / (A * bolt["As"])) ** 2
    term2 = (
        3
        * (16 / (math.pi * deq**3)) ** 2
        * (1 - (tightening["mu_tot_min"] * rm) ** 2 / A)
    )

    Tmax = sigma_target / math.sqrt(term1 + term2)

    tool_class = tightening.get("precision_class", "C20")
    disp = TIGHTENING_DISPERSIONS.get(tool_class, 0.20)

    T_nom = Tmax / (1 + disp)

    return {
        "T_nominal": round(T_nom, 1),
        "T_min": round(T_nom * (1 - disp), 1),
        "T_max": round(Tmax, 1),
    }


def check_preload(
    bolt: Bolt,
    assembly: Joint,
    loads: Loads,
    tightening: Tightening,
) -> dict:
    """
    Checks F0^min <= F0^max (Section 5.2.5).
    """
    F_min = F0_min(bolt, assembly, loads, tightening)
    F_max = F0_max(bolt, assembly, loads, tightening)

    return {
        "valid": F_min <= F_max,
        "F0_min": round(F_min, 1),
        "F0_max": round(F_max, 1),
        "margin": round(F_max - F_min, 1),
    }


def check_bearing(
    bolt: Bolt,
    assembly: Joint,
    loads: Loads,
    tightening: Tightening,
) -> dict:
    """
    Checks no bearing failure: sigma_p^max <= Rc (Section 5.2.6).
    """
    F_max = F0_max(bolt, assembly, loads, tightening)
    S = math.pi * (assembly["do"] ** 2 - assembly["dh"] ** 2) / 4

    sigma_p = F_max / S if S > 0 else float("inf")
    Rc = assembly["Rc"]

    return {
        "valid": sigma_p <= Rc,
        "sigma_p_max": round(sigma_p, 1),
        "Rc": round(Rc, 1),
        "margin": round(Rc - sigma_p, 1),
    }


def bolt_stresses(
    bolt: Bolt,
    assembly: Joint,
    loads: Loads,
    tightening: Tightening,
) -> dict:
    """
    Bolt stresses (Annex A).

    sigma_b (tension), tau_b (torsion), sigma_b_eq (Von Mises)
    """
    F_max = F0_max(bolt, assembly, loads, tightening)

    d2 = bolt["d"] - 0.6495 * bolt["p"]
    deq = bolt["d"] - 0.9382 * bolt["p"]

    sigma_b = F_max / bolt["As"]
    MTb = F_max * (bolt["p"] / (2 * math.pi) + 0.577 * tightening["mu_tot_min"] * d2)
    tau_b = (16 * MTb) / (math.pi * deq**3)
    sigma_eq = math.sqrt(sigma_b**2 + 3 * tau_b**2)

    sigma_adm = 0.9 * bolt["Re_min"]

    return {
        "sigma_b_max": round(sigma_b, 1),
        "tau_b_max": round(tau_b, 1),
        "sigma_b_eq": round(sigma_eq, 1),
        "sigma_adm": round(sigma_adm, 1),
        "valid": sigma_eq <= sigma_adm,
        "margin": round(sigma_adm - sigma_eq, 1),
    }


def check(
    bolt: Bolt,
    assembly: Joint,
    loads: Loads,
    tightening: Tightening,
) -> dict:
    """
    Full verification report.
    """
    preload = check_preload(bolt, assembly, loads, tightening)
    bearing = check_bearing(bolt, assembly, loads, tightening)
    stresses = bolt_stresses(bolt, assembly, loads, tightening)
    torques = tightening_torques(bolt, assembly, loads, tightening)

    return {
        "valid": preload["valid"] and bearing["valid"] and stresses["valid"],
        "preload": preload,
        "bearing": bearing,
        "stresses": stresses,
        "torques": torques,
    }
