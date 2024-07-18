# ===============================================================================
# Copyright 2024 Jake Ross
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ===============================================================================
from backend.constants import (
    TDS,
    URANIUM,
    SULFATE,
    FLUORIDE,
    CHLORIDE,
    ARSENIC,
    NITRATE,
    CALCIUM,
    SODIUM,
    POTASSIUM,
    MAGNESIUM,
    CARBONATE,
    PH,
    BICARBONATE,
)

# DWB ===============================================================================
DWB_ANALYTE_MAPPING: dict = {
    ARSENIC: 3,
    BICARBONATE: None,
    CALCIUM: None,
    CARBONATE: None,
    CHLORIDE: 15,
    FLUORIDE: 19,
    MAGNESIUM: None,
    NITRATE: 35,
    POTASSIUM: None,
    SODIUM: None,
    SULFATE: 41,
    TDS: 90,
    # "Uranium-238": 386,
    URANIUM: 385,  # "Combined Uranium"
    PH: None,
}
# ISC Seven Rivers ===============================================================================
"""
pH
Specific Conductance
Temperature
Potassium
Magnesium
Hydroxide
Copper
Bromide
Sulfate
Total recoverable metals, Iron
Turbidity
Iron
Manganese
Electrical Conductance
Ion Balance
SiO2
Chloride
Calcium
Strontium
Bicarbonate (HCO3)
Nitrite
Ortho Phosphate
Boron
Anions total
Sodium
Carbonate (CO3)
Zinc
TDS calc
Nitrate
Silicon
Fluoride
Hardness
Alkalinity as CaCO3
Cations total
Barium"""
ISC_SEVEN_RIVERS_ANALYTE_MAPPING: dict = {
    ARSENIC: None,
    BICARBONATE: "Bicarbonate (HCO3)",
    CHLORIDE: "Chloride",
    CALCIUM: "Calcium",
    CARBONATE: "Carbonate (CO3)",
    FLUORIDE: "Fluoride",
    MAGNESIUM: "Magnesium",
    NITRATE: "Nitrate",
    POTASSIUM: "Potassium",
    SODIUM: "Sodium",
    SULFATE: "Sulfate",
    TDS: "TDS calc",
    URANIUM: None,
    PH: "pH",
}

# AMP ===============================================================================
"""
ALK
Ca
Ca(total)
Cl
CO3
CONDLAB
HCO3
HRD
IONBAL
K
K(total)
Mg
Mg(total)
Na
Na(total)
Na+K
OH
pHL
SO4
TAn
TCat
TDS
"""
NMBGMR_ANALYTE_MAPPING: dict = {
    ARSENIC: "As",  #  nmbgmr can't handle multiple analytes yet "As,As(total)",
    BICARBONATE: "HCO3",
    CALCIUM: "Ca",
    CARBONATE: "CO3",
    CHLORIDE: "Cl",
    FLUORIDE: "F",
    MAGNESIUM: "Mg",
    NITRATE: "NO3",
    POTASSIUM: "K",
    SODIUM: "Na",
    SULFATE: "SO4",
    TDS: "TDS",
    URANIUM: "Uranium",
    PH: "pHL",
}

# WQP ===============================================================================
WQP_ANALYTE_MAPPING: dict = {
    ARSENIC: ["Arsenic"],
    BICARBONATE: ["Bicarbonate"],
    CALCIUM: ["Calcium"],
    CARBONATE: ["Carbonate"],
    CHLORIDE: ["Chloride"],
    FLUORIDE: ["Fluoride"],
    MAGNESIUM: ["Magnesium"],
    NITRATE: ["Nitrate", "Nitrate-N", "Nitrate as N"],
    POTASSIUM: ["Potassium"],
    SODIUM: ["Sodium"],
    SULFATE: [
        "Sulfate",
        "Sulfate as SO4",
        "Sulfur Sulfate",
        "Sulfate as S",
        "Total Sulfate",
    ],
    TDS: ["Total dissolved solids"],
    URANIUM: ["Uranium", "Uranium-238"],
    PH: ["pH"],
}
# BOR ===============================================================================
"""
Temp
DO
ALK HCO3
ALK CO3
ALK OH
ALK
P ALK
pH
Color
Cond
Br
Cl
CN
F
TH
LSI
NO3
NO3 NO2
NO2
NH4
ClO4
Ortho P
TP
TDS
SO4
Turbidity
Al
As
Ba
B
Cd
Ca
Cr
Co
Cu
Fe aq
Fe tot
Pb
Mg
Mn aq
Mn tot
Hg
Mb
Ni
K
Se
SiO2
Ag
Na
St
U
Zn
"""
BOR_ANALYTE_MAPPING: dict = {
    ARSENIC: "As",
    BICARBONATE: "ALK HCO3",
    CALCIUM: "Ca",
    CARBONATE: "ALK CO3",
    CHLORIDE: "Cl",
    FLUORIDE: "F",
    MAGNESIUM: "Mg",
    NITRATE: "NO3",
    POTASSIUM: "K",
    SODIUM: "Na",
    SULFATE: "SO4",
    TDS: "TDS",
    URANIUM: "U",
    PH: "pH",
}


def get_var_name(var):
    for name, value in globals().items():
        if value is var:
            return name


for mapping in (
    DWB_ANALYTE_MAPPING,
    ISC_SEVEN_RIVERS_ANALYTE_MAPPING,
    NMBGMR_ANALYTE_MAPPING,
    WQP_ANALYTE_MAPPING,
    BOR_ANALYTE_MAPPING,
):

    for k in (
        ARSENIC,
        BICARBONATE,
        CALCIUM,
        CARBONATE,
        CHLORIDE,
        FLUORIDE,
        MAGNESIUM,
        NITRATE,
        POTASSIUM,
        SODIUM,
        SULFATE,
        TDS,
        URANIUM,
        PH,
    ):

        if k not in mapping:
            name = get_var_name(mapping)
            raise NotImplementedError(f"Mapping for {k} not implemented by {name}")
# ============= EOF =============================================
