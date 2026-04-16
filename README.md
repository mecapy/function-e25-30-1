# NF E25-030-1 - Pre-loaded Bolted Joints

## Description

This function implements the French standard **NF E25-030-1 (August 2014)** for the calculation and verification of pre-loaded mechanical bolted joints using the simplified approach.

## Normative Reference

- **Standard**: NF E25-030-1
- **Title**: Bolted assemblies with ISO metric threading - Design rules for pre-loaded assemblies - Simplified approach
- **Date**: August 2014
- **Organization**: AFNOR

## Available Functions

| Function             | Description |
|----------------------|-------------|
| `check`              | Full assembly verification (all checks) |
| `min_preload`        | Minimum required preload F0^min (Section 5.2.3) |
| `max_preload`        | Maximum allowable preload F0^max (Section 5.2.4) |
| `tightening_torques` | Tightening torques (nominal, min, max) per Annex C |
| `check_preload`      | Verification of criterion F0^min ≤ F0^max (Section 5.2.5) |
| `check_bearing`      | Verification of no bearing failure under head/nut (Section 5.2.6) |
| `bolt_stresses`      | Bolt stresses (tension, torsion, Von Mises) per Annex A |

## JSON Request Structure

```json
{
  "vis": {
    "d": 10,
    "p": 1.5,
    "As": 58,
    "Re_min": 940,
    "quality_class": "10.9"
  },
  "assemblage": {
    "dh": 11,
    "do": 14.63,
    "Rc": 400,
    "mu_p_min": 0.15
  },
  "sollicitations": {
    "FA_max": 5000,
    "Ft_max": 2000
  },
  "serrage": {
    "mu_tot_min": 0.12,
    "mu_tot_max": 0.18,
    "precision_class": "C20"
  }
}
```

## Parameter Description

### `vis` - Bolt Properties

| Parameter | Type | Unit | Description |
|-----------|------|------|-------------|
| `d` | float | mm | Nominal bolt diameter (e.g. 10 for M10) |
| `p` | float | mm | Thread pitch |
| `As` | float | mm² | Stress cross-section area |
| `Re_min` | float | N/mm² | Minimum yield strength |
| `quality_class` | string | - | Property class ("6.8", "8.8", "10.9", "12.9") |

### `assemblage` - Assembly Properties

| Parameter | Type | Unit | Description | Default |
|-----------|------|------|-------------|---------|
| `dh` | float | mm | Clearance hole diameter | - |
| `do` | float | mm | Outer bearing surface diameter (under head/nut) | - |
| `Rc` | float | N/mm² | Compressive strength of the clamped material | - |
| `mu_p_min` | float | - | Minimum friction coefficient at the joint interface | 0.15 |

### `sollicitations` - Applied Loads

| Parameter | Type | Unit | Description | Default |
|-----------|------|------|-------------|---------|
| `FA_max` | float | N | Maximum axial external force | 0.0 |
| `Ft_max` | float | N | Maximum transverse force | 0.0 |

### `serrage` - Tightening Conditions

| Parameter | Type | Unit | Description | Default |
|-----------|------|------|-------------|---------|
| `mu_tot_min` | float | - | Minimum overall friction coefficient | - |
| `mu_tot_max` | float | - | Maximum overall friction coefficient | - |
| `precision_class` | string | - | Tightening tool precision class | "C20" |

**Available precision classes**: "C10", "C15", "C20", "C30", "C50"

## Full Examples

### Example 1: M10 bolt class 10.9 with axial and transverse loads

```json
{
  "vis": {
    "d": 10,
    "p": 1.5,
    "As": 58,
    "Re_min": 940,
    "quality_class": "10.9"
  },
  "assemblage": {
    "dh": 11,
    "do": 14.63,
    "Rc": 400,
    "mu_p_min": 0.15
  },
  "sollicitations": {
    "FA_max": 5000,
    "Ft_max": 2000
  },
  "serrage": {
    "mu_tot_min": 0.12,
    "mu_tot_max": 0.18,
    "precision_class": "C20"
  }
}
```

### Example 2: M12 bolt class 8.8 with axial load only

```json
{
  "vis": {
    "d": 12,
    "p": 1.75,
    "As": 84.3,
    "Re_min": 640,
    "quality_class": "8.8"
  },
  "assemblage": {
    "dh": 13,
    "do": 18.67,
    "Rc": 350,
    "mu_p_min": 0.15
  },
  "sollicitations": {
    "FA_max": 8000,
    "Ft_max": 0
  },
  "serrage": {
    "mu_tot_min": 0.10,
    "mu_tot_max": 0.16,
    "precision_class": "C15"
  }
}
```

## Response Structure

The `check` function returns a JSON dictionary with:

```json
{
  "valid": true,
  "preload": {
    "valid": true,
    "F0_min": 18333.3,
    "F0_max": 33814.7,
    "margin": 15481.4
  },
  "bearing": {
    "valid": true,
    "sigma_p_max": 250.0,
    "Rc": 400.0,
    "margin": 150.0
  },
  "stresses": {
    "sigma_b_max": 583.0,
    "tau_b_max": 234.4,
    "sigma_b_eq": 710.5,
    "sigma_adm": 846.0,
    "valid": true,
    "margin": 135.5
  },
  "torques": {
    "T_nominal": 45.5,
    "T_min": 36.4,
    "T_max": 54.6
  }
}
```

## Interpreting Results

### Global Validation
- `valid`: `true` if all checks pass, `false` otherwise

### Preload
- `F0_min`: Minimum preload required to prevent separation and sliding
- `F0_max`: Maximum preload the bolt can sustain without exceeding 90% of Re
- `margin`: Safety margin (F0_max - F0_min) — must be positive

### Tightening Torques
- `T_nominal`: Torque to apply with the torque wrench
- `T_min`: Minimum allowable torque (accounting for scatter)
- `T_max`: Maximum allowable torque

### Bearing Verification
- `sigma_p_max`: Maximum compressive stress under head/nut
- `Rc`: Compressive strength of the clamped material
- Criterion: `sigma_p_max ≤ Rc`

### Bolt Stresses
- `sigma_b_max`: Tensile stress due to preload
- `tau_b_max`: Torsional stress due to tightening
- `sigma_b_eq`: Von Mises equivalent stress
- `sigma_adm`: 90% of yield strength Re
- Criterion: `sigma_b_eq ≤ sigma_adm`

## Typical Values

### Bolt Property Classes

| Class | Re_min (N/mm²) | Rm_min (N/mm²) | Applications |
|-------|----------------|----------------|--------------|
| 6.8   | 480            | 600            | General use, low loads |
| 8.8   | 640            | 800            | Standard applications |
| 10.9  | 940            | 1040           | High-strength applications |
| 12.9  | 1100           | 1220           | Very high-strength applications |

### Typical Friction Coefficients

| Surface | μ_tot_min | μ_tot_max |
|---------|-----------|-----------|
| As-machined (untreated) | 0.12 | 0.18 |
| Oiled | 0.10 | 0.16 |
| Zinc-plated | 0.15 | 0.25 |
| Lubricated (MoS2) | 0.08 | 0.12 |

### Tightening Tool Precision Classes

| Class | Scatter | Tightening Tool |
|-------|---------|-----------------|
| C10   | ±10%    | Electronic torque wrench with display |
| C15   | ±15%    | Click-type torque wrench |
| C20   | ±20%    | Standard torque wrench |
| C30   | ±30%    | Adjustable wrench with extension |
| C50   | ±50%    | Standard wrench without control |

## References

- NF E25-030-1 (August 2014): Simplified approach
- NF E25-030-2: General approach (more detailed calculations)
- ISO 898-1: Mechanical properties of fasteners
- ISO 4014/4017: Hexagon head bolts

## Important Notes

1. **Scope**: This simplified approach applies to pre-loaded bolted assemblies with ISO metric threading.

2. **Assumptions**:
   - Symmetric assembly (identical head and nut)
   - Tightening by torque control
   - No dynamic loads (fatigue)

3. **Limitations**:
   - For complex cases (fatigue, variable loads), use NF E25-030-2
   - Friction coefficients must be measured or estimated with care

4. **Safety**:
   - Always respect the calculated tightening torques
   - Check the condition of contact surfaces
   - Use bolts compliant with ISO 898-1
