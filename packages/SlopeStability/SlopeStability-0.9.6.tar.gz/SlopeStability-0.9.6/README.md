# Slope Stability Analysis

## Description

This package determines the stability of a slope by calculating the factor of safety for the critical slip surface using the stability charts developed by Janbu (1954). The package provides four functions: `CHI_PHI_SOIL`, `INFINITE_SLOPE`, `PURELY_COHESIVE_SOIL`, and `PURELY_COHESIVE_SOIL_WITH_INCREASING_SHEAR_STRENGTH`. Inputs for these functions must be in either SI units (m, kN/m², kN/m³) or FPS units (feet, pcf, psf).

## Installation

This package can be installed using:

```sh
pip install SlopeStability

## Usage
The following functions can be used:

###PURELY_COHESIVE_SOIL(beta, H, Hw, Hwdash, D, c, lw, l, Ht, q)
    beta: Slope Angle
    H: Height of slope above toe (feet/m)
    Hw: Height of external water level above toe (feet/m)
    Hwdash: Height of internal water level above toe (feet/m)
    D: Depth from the toe of the slope to the lowest point on the slip circle
    c: Average shear strength (kN/m² or psf)
    lw: Unit weight of water (kN/m³ or pcf)
    l: Unit weight of soil (kN/m³ or pcf)
    Ht: Depth of tension crack (feet/m)
    q: Surcharge (kN/m² or psf)

####Applicable for soil with a friction angle (phi=0).

###CHI_PHI_SOIL(beta, H, Hw, Hc, Hwdash, c, phi, l, lw, q, Ht)
    beta: Slope Angle
    H: Height of slope above toe (feet/m)
    Hw: Height of external water level above toe (feet/m)
    Hwdash: Height of internal water level above toe (feet/m)
    Hc: Height of internal water level measured beneath the crest of the slope to the lowest point on the slip circle
    c: Average shear strength (kN/m² or psf)
    phi: Frictional angle of slope (degree)
    lw: Unit weight of water (kN/m³ or pcf)
    l: Unit weight of soil (kN/m³ or pcf)
    Ht: Depth of tension crack (feet/m)
    q: Surcharge (kN/m² or psf)
#### Applicable for soil with both friction angle and cohesion non-zero. 
#### Assumption: For phi>0, the critical circle passes through the toe of the slope.

####INFINITE_SLOPE(beta, theeta, H, c, phi, cdash, phdash, l, lw, X, T)
    beta: Slope Angle (degree)
    H: Height of slope above toe (feet/m)
    theeta: Angle of seepage measured from the horizontal direction (degree)
    c: Cohesion for total stress analysis (kN/m² or psf)
    phi: Frictional angle for total stress analysis (degree)
    cdash: Cohesion for effective stress analysis (kN/m² or psf)
    phdash: Frictional angle for effective stress analysis (degree)
    lw: Unit weight of water (kN/m³ or pcf)
    l: Unit weight of soil (kN/m³ or pcf)
    X: Distance from the depth of sliding to the surface of seepage, measured normal to the surface of the slope (feet/m)
    T: Distance from the depth of sliding to the surface of the slope, measured normal to the surface of the slope (feet/m)
#### Applicable for cohesionless materials (c=0) where the critical failure mechanism is shallow sliding or slopes in residual soils, where a relatively thin layer of soil overlies firmer soil or rock, and the critical failure mechanism is sliding along a plane parallel to the slope, at the top of the firm layer.

###PURELY_COHESIVE_SOIL_WITH_INCREASING_SHEAR_STRENGTH(beta, H, H0, Cb, l, lb)
    beta: Slope angle
    H: Height of the slope above toe (feet/m)
    H0: Height at which the straight line of shear strength intersects zero
    Cb: Strength at the elevation of the toe of the slope
    l: Weighted average unit weight for partly submerged slopes
    lb: Buoyant unit weight for submerged slopes
##Contributing
####Contributions are welcome! Please feel free to submit a pull request.

##License
This project is licensed under the MIT License. See the LICENSE file for details.

##Contact
Name: [Piyush Jangid]
Email: [xyz@gmail.com]
GitHub: yourusername