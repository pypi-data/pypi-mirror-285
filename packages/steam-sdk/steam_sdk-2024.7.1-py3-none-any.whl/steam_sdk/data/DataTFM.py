import numpy as np
from dataclasses import dataclass, field
from typing import Optional

"""
    This class defines the TFM dataclasses, which contain the variables to be used in the TFM model.
"""


'''New code'''

@dataclass
class General:
    magnet_name: Optional[str] = None
    magnet_length: Optional[float] = None
    num_HalfTurns: Optional[int] = None
    I_magnet: Optional[float] = None
    groups: Optional[int] = None
    local_library_path: Optional[str] = None
    lib_path: Optional[str] = None
    new_lib_path: Optional[str] = None
    L_mag: Optional[float] = None
    C_ground: Optional[float] = None
    R_warm: Optional[float] = None
    apertures: Optional[int] = None

@dataclass
class Turns:
    turns_to_sections: np.ndarray = field(default_factory=lambda: np.array([]))
    turns_to_apertures: np.ndarray = field(default_factory=lambda: np.array([]))

@dataclass
class HalfTurns:
    HalfTurns_to_groups: np.ndarray = field(default_factory=lambda: np.array([]))
    HalfTurns_to_conductor: np.ndarray = field(default_factory=lambda: np.array([]))
    HalfTurns_to_sections: np.ndarray = field(default_factory=lambda: np.array([]))
    n_strands: np.ndarray = field(default_factory=lambda: np.array([]))
    rotation_ht: np.ndarray = field(default_factory=lambda: np.array([]))
    mirror_ht: np.ndarray = field(default_factory=lambda: np.array([]))
    alphaDEG_ht: np.ndarray = field(default_factory=lambda: np.array([]))
    bare_cable_width: np.ndarray = field(default_factory=lambda: np.array([]))
    bare_cable_height_mean: np.ndarray = field(default_factory=lambda: np.array([]))
    strand_twist_pitch: np.ndarray = field(default_factory=lambda: np.array([]))
    Nc: np.ndarray = field(default_factory=lambda: np.array([]))
    C_strand: np.ndarray = field(default_factory=lambda: np.array([]))
    Rc: np.ndarray = field(default_factory=lambda: np.array([]))
    RRR: np.ndarray = field(default_factory=lambda: np.array([]))
    diameter: np.ndarray = field(default_factory=lambda: np.array([]))
    fsc: np.ndarray = field(default_factory=lambda: np.array([]))
    f_rho_effective: np.ndarray = field(default_factory=lambda: np.array([]))
    R_warm: np.ndarray = field(default_factory=lambda: np.array([]))


@dataclass
class Strands:
    filament_diameter: np.ndarray = field(default_factory=lambda: np.array([]))
    diameter: np.ndarray = field(default_factory=lambda: np.array([]))
    d_filamentary: np.ndarray = field(default_factory=lambda: np.array([]))
    d_core: np.ndarray = field(default_factory=lambda: np.array([]))
    fsc: np.ndarray = field(default_factory=lambda: np.array([]))
    f_rho_effective: np.ndarray = field(default_factory=lambda: np.array([]))
    fil_twist_pitch: np.ndarray = field(default_factory=lambda: np.array([]))
    RRR: np.ndarray = field(default_factory=lambda: np.array([]))
    f_mag_X_Roxie: np.ndarray = field(default_factory=lambda: np.array([]))
    f_mag_Y_Roxie: np.ndarray = field(default_factory=lambda: np.array([]))
    f_mag_Roxie: np.ndarray = field(default_factory=lambda: np.array([]))
    f_mag_Comsol: np.ndarray = field(default_factory=lambda: np.array([]))
    f_mag_X_Comsol: np.ndarray = field(default_factory=lambda: np.array([]))
    f_mag_Y_Comsol: np.ndarray = field(default_factory=lambda: np.array([]))
    strands_to_conductor: np.ndarray = field(default_factory=lambda: np.array([]))

@dataclass
class Options:
    flag_SC: Optional[bool] = True
    flag_Wedge: Optional[bool] = False
    flag_CPS: Optional[bool] = False
    flag_CB: Optional[bool] = False
    flag_ED: Optional[bool] = False
    flag_ISCC: Optional[bool] = False
    flag_IFCC: Optional[bool] = False
    flag_BS: Optional[bool] = False

@dataclass
class PC:  # DataClass for persistent current
    L: np.ndarray = field(default_factory=lambda: np.array([]))  # Inductance for PC modelisation
    I: np.ndarray = field(default_factory=lambda: np.array([]))  # Current generator for PC modelisation
    M: np.ndarray = field(default_factory=lambda: np.array([]))  # Coupling factor for PC modelisation
    M_PC_IFCC: np.ndarray = field(default_factory=lambda: np.array([]))  # Coupling factor between PC currents and interfilament currents

@dataclass
class IFCC:
    L: np.ndarray = field(default_factory=lambda: np.array([]))
    R: np.ndarray = field(default_factory=lambda: np.array([]))
    M: np.ndarray = field(default_factory=lambda: np.array([]))
    P: np.ndarray = field(default_factory=lambda: np.array([]))
    I: np.ndarray = field(default_factory=lambda: np.array([]))
    tau: np.ndarray = field(default_factory=lambda: np.array([]))

@dataclass
class ISCC:
    L: np.ndarray = field(default_factory=lambda: np.array([]))
    R: np.ndarray = field(default_factory=lambda: np.array([]))
    M: np.ndarray = field(default_factory=lambda: np.array([]))
    P: np.ndarray = field(default_factory=lambda: np.array([]))
    I: np.ndarray = field(default_factory=lambda: np.array([]))
    tau: np.ndarray = field(default_factory=lambda: np.array([]))

@dataclass
class ED:
    L: np.ndarray = field(default_factory=lambda: np.array([]))
    R: np.ndarray = field(default_factory=lambda: np.array([]))
    M: np.ndarray = field(default_factory=lambda: np.array([]))
    P: np.ndarray = field(default_factory=lambda: np.array([]))
    I: np.ndarray = field(default_factory=lambda: np.array([]))
    tau: np.ndarray = field(default_factory=lambda: np.array([]))

@dataclass
class Wedge:
    RRR_wedges: np.ndarray = field(default_factory=lambda: np.array([]))
    L: np.ndarray = field(default_factory=lambda: np.array([]))
    R: np.ndarray = field(default_factory=lambda: np.array([]))
    M: np.ndarray = field(default_factory=lambda: np.array([]))
    I: np.ndarray = field(default_factory=lambda: np.array([]))
    P: np.ndarray = field(default_factory=lambda: np.array([]))
    tau: np.ndarray = field(default_factory=lambda: np.array([]))

@dataclass
class CB:
    L: np.ndarray = field(default_factory=lambda: np.array([]))
    R: np.ndarray = field(default_factory=lambda: np.array([]))
    M: np.ndarray = field(default_factory=lambda: np.array([]))
    I: np.ndarray = field(default_factory=lambda: np.array([]))
    P: np.ndarray = field(default_factory=lambda: np.array([]))
    tau: np.ndarray = field(default_factory=lambda: np.array([]))

@dataclass
class CPS:
    L: np.ndarray = field(default_factory=lambda: np.array([]))
    R: np.ndarray = field(default_factory=lambda: np.array([]))
    M: np.ndarray = field(default_factory=lambda: np.array([]))
    I: np.ndarray = field(default_factory=lambda: np.array([]))
    P: np.ndarray = field(default_factory=lambda: np.array([]))
    tau: np.ndarray = field(default_factory=lambda: np.array([]))