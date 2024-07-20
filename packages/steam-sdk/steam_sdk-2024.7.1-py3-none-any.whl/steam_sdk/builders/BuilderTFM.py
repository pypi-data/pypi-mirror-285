import time
from typing import Tuple, Any
import sys
import numpy as np
import pandas as pd
import os
from pathlib import Path
from dataclasses import asdict
from scipy.interpolate import RegularGridInterpolator
from scipy.signal import find_peaks
from scipy.interpolate import interp1d
from scipy.ndimage import gaussian_filter1d
from scipy.signal import savgol_filter
from scipy.interpolate import make_interp_spline

import steammaterials
from steam_sdk.data.DataTFM import General
from steam_sdk.data.DataTFM import Turns
from steam_sdk.data.DataTFM import HalfTurns
from steam_sdk.data.DataTFM import Strands
from steam_sdk.data.DataTFM import PC
from steam_sdk.data.DataTFM import Options
from steam_sdk.data.DataTFM import IFCC
from steam_sdk.data.DataTFM import ISCC
from steam_sdk.data.DataTFM import ED
from steam_sdk.data.DataTFM import Wedge
from steam_sdk.data.DataTFM import CB
from steam_sdk.data.DataTFM import CPS
from steam_sdk.data.DataModelCircuit import Component
from steam_sdk.parsers.ParserXYCE import ParserXYCE
from steammaterials.STEAM_materials import STEAM_materials
matpath: str = os.path.dirname(steammaterials.__file__)
import matplotlib.pyplot as plt
import time

class BuilderTFM:
    """
           Class to generate TFM models
    """


    def __init__(self, builder_LEDET= None, flag_build: bool = True,
                  output_path: str = None, local_library_path: str = None, TFM_inputs=None, magnet_data=None ):
        """
             Object is initialized by defining TFM variable structure and default parameter descriptions, starting from
             the magnet_name and the builder_LEDET model. The class can also calculate various passive effects, depending on the flag values.

            :param magnet_name: name of the analyzed magnet
            :param builder_LEDET: builderLEDET object corresponding to that magnet
            :param flag_build: defines whether the model has to be build
            :param output_path: path to save the generated lib file
            :param TFM_inputs: TFMClass from DataModelCircuit.py in steam_sdk.data, includes:
                   - flag_PC, flag_ISCC, flag_IFCC, flag_ED, flag_Wedge, flag_CB, flag_BS: Flag effects.
                   - flag_T: If True, the Magnet circuit in the .lib file is subdivided into one L per turn.
                             If False, the Magnet circuit in the .lib file has only one L per aperture.
                   - M_CB_wedge: Value of the mutual coupling between ColdBore and Wedge.
                   - T: Simulation temperature.
            :param Magnet_data: Magnet class from DataModelCircuit.py in steam_sdk.data, includes:
                    - name: Magnet name.
                    - L_mag: Total inductance of the magnet.
                    - C_ground: Total capacitance to ground of the magnet circuit.
                    - field_interp_value: If not None, specifies the parameter value for which to find f_mag,
                                          differentiating field files extracted from Comsol by a parameter other than temperature.
                                          If None the field_interp_value used is the T
        """
        self.General = General()
        self.Turns = Turns()
        self.HalfTurns = HalfTurns()
        self.Strands = Strands()
        self.Options = Options()
        self.PC = PC()
        self.IFCC = IFCC()
        self.ISCC = ISCC()
        self.ED = ED()
        self.Wedge = Wedge()
        self.CB = CB()
        self.CPS = CPS ()
        self.magnet_name = magnet_data.name
        self.local_library_path = local_library_path

        if flag_build:
            if not builder_LEDET or not self.magnet_name:
                 raise Exception('Cannot build model without providing BuilderLEDET object with Inputs dataclass and magnet_name')

            # Translate the Inputs dataclass of BuilderLEDET in a dictionary
            ledet_inputs = asdict(builder_LEDET.Inputs)
            self.ledet_inputs = ledet_inputs
            self.ledet_auxiliary = builder_LEDET.Auxiliary
            self.ledet_options = builder_LEDET.Options
            self.TFM_inputs = TFM_inputs
            self.magnet_data = magnet_data

            self.current = TFM_inputs.current
            self.temperature = TFM_inputs.temperature
            self.flag_T = TFM_inputs.flag_T
            self.output_path = output_path
            self.flag_debug = TFM_inputs.flag_debug

            # TODO: HardCoded values
            self.Wedge.RRR_wedges = np.array([TFM_inputs.RRR_Wedge])
            
            self.conductor_to_group = np.array(builder_LEDET.model_data.CoilWindings.conductor_to_group)
            self.assignTurnsToSections()
            self.translateModelDataToTFMGeneral()
            self.translateModelDataToTFMHalfTurns()
            self.translateModelDataToTFMStrands()
            self.setOptions()

            self.generate_library(output_path=output_path)
            self.change_coupling_parameter(output_path=output_path)


    ####################################################################################################################
    ######################################## TFM DATACLASSES ATTRIBUTE SETTING ########################################

    def assignTurnsToSections(self):
        '''
        This function assigns the value to turns_to_sections vector in the Turns dataclass attributes.
        This function assigns the value to turns_to_apertures vector in the Turns dataclass attributes.
        This function assigns the value to HalfTurns_to_sections vector in the HalfTurns dataclass attributes.

        turns_to_sections is a vector long as the number of turns and each element contains the id of the section to which it is assigned
        A section is a LRC circuit inside the magnet circuit in the generated lib file 
        '''
        flag_T = self.flag_T
        nT = self.ledet_inputs['nT']
        n_Turns = np.sum(nT)// 2
        elPair_grouped = self.ledet_auxiliary.elPairs_GroupTogether
        HalfTurns_to_groups = np.repeat(np.arange(len(nT)) + 1, nT)

        if flag_T and self.magnet_data.turn_to_section is not None and self.magnet_data.section_to_aperture is not None:
            # If turn_to_section is not none, the turns_to_section vector is the one specified as input of the yaml file
            turns_to_sections = np.array(self.magnet_data.turn_to_section).astype(int)
            section_to_aperture = self.magnet_data.section_to_aperture
            HalfTurns_to_sections = np.repeat(turns_to_sections, 2)  # Repeats each element of the vector twice, in order to get the corresponding Halfturns_to_sections vector
            self.setAttribute(self.HalfTurns, 'HalfTurns_to_sections', HalfTurns_to_sections)
            # Create turns_to_apertures by mapping sections to apertures
            turns_to_apertures = np.array([section_to_aperture[section - 1] for section in turns_to_sections])

        else:
            conductor_to_group = self.conductor_to_group
            # turn_to_aperture not provided -> we assume two aperture
            # the first half of elPairs_GroupTogether will be assigned to the first aperture, the second half to the second aperture
            idx = 0
            turns_to_apertures = np.zeros(n_Turns, dtype=int)
            for ap in range(1, 2 + 1):
                for i in range(idx, idx + len(elPair_grouped) // 2):
                    idx_group = elPair_grouped[i][0] if elPair_grouped[i][0] < elPair_grouped[i][1] else elPair_grouped[i][1]
                    idx_T = np.where(HalfTurns_to_groups == idx_group)[0]
                    turns_to_apertures[np.ix_(idx_T)] = ap
                idx = idx + len(elPair_grouped) // 2

            if flag_T: # If flag_T is set but no turn_to_section or no turn_to_aperture, then the section = groups (condcutor number from LEDET)
                HalfTurns_to_sections = conductor_to_group[HalfTurns_to_groups - 1]
                turns_to_sections = HalfTurns_to_sections[::2]  # To get turns_to_section from Halfturns_to_sections we take one element every two elements
            else:  # If flag_T is not set, it means we just have one section per Aperture
                turns_to_sections = np.ones(n_Turns, dtype=int)
                # Checking if turn_to_section and turn_to_aperture in the circuit yaml file are not empty
                # -> if they are not empty but flag_T = 0, it means that this list has to be used in the group_to_components function

        self.setAttribute(self.Turns, 'turns_to_sections', turns_to_sections)
        self.setAttribute(self.Turns, 'turns_to_apertures', turns_to_apertures)

    def translateModelDataToTFMGeneral(self):
        '''
        This function saves the appropriate BuilderLEDET Inputs dataclass values for the General dataclass attributes.

        L_mag instead is set in the function calculate_Inductance_Sections
        '''
        self.setAttribute(self.General, 'magnet_name', self.magnet_name)
        self.setAttribute(self.General, 'magnet_length', self.ledet_inputs['l_magnet'])
        self.setAttribute(self.General, 'I_magnet', self.current)
        self.setAttribute(self.General, 'local_library_path', self.local_library_path)
        nT = self.ledet_inputs['nT']
        self.setAttribute(self.General, 'num_HalfTurns', np.sum(nT))
        if not self.flag_T: # If not flag_T, then the number of groups is taken from Ledet since we have just one section per aperture
            n_groups = max(self.conductor_to_group)
        else: # If flag_T, then the number of groups is the highest number of sections in the magent circuit
            n_groups = max(self.Turns.turns_to_sections)
        self.setAttribute(self.General, 'groups', n_groups)
        self.setAttribute(self.General, 'apertures', max(self.Turns.turns_to_apertures))
        C_ground = self.magnet_data.C_ground
        self.setAttribute(self.General, 'C_ground', C_ground)
        self.setAttribute(self.General, 'lib_path', self.output_path)

    def calculate_warm_resistance(self): # Utility function to calculate R_warm in self.General and self.HalfTurns
        '''
            Function to calculate the warm resistance, both per cable and per magnet
            It saves the R_warm_cable n the HalfTurns dataclass and the R_warm in the General dataclass
        '''

        if self.Options.flag_SC:
            # If the Magnet is in SC state, let's set by default a warm resistance of 1nOhm
            R_warm = 1e-9
            R_warm_cable = np.repeat(R_warm, self.General.num_HalfTurns)
        else:
            RRR = self.HalfTurns.RRR
            T = self.temperature
            fsc = self.Strands.fsc
            dws = self.Strands.diameter
            l = self.General.magnet_length
            I = self.General.I_magnet
            HT_to_Strands = self.HalfTurns.n_strands

            B = self.Strands.f_mag_Roxie * I
            B = B[:, 0]
            # Area of the strands
            Area_strands = (1-fsc) * np.pi * (dws/2) ** 2

            cont = 0
            A_cable = []
            B_cable = []

            # For each HalfTurns, calculates the total Area as the sum of the Areas of each strand corresponding to that HalfTurn
            # For each HalfTurns, calculates the total B as the average of the B of each strand corresponding to that HalfTurn
            for i in range(self.General.num_HalfTurns):
                n_strand_cable = HT_to_Strands[i]
                A_cable_HT = np.sum(Area_strands[cont: cont+n_strand_cable])
                B_cable_HT = np.mean(B[cont: cont+n_strand_cable])
                A_cable.append(A_cable_HT)
                B_cable.append(B_cable_HT)
                cont += n_strand_cable

            rho = self.rhoCu_nist(T=T, RRR= np.repeat(RRR, self.General.num_HalfTurns), B=np.array(B_cable))
            # Calculates the R_warm for each HalfTurn as R_HT = rho_HT * l_mag / A_HT
            R_warm_cable = rho * l / (np.array(A_cable))
            # Calculates the total R_warm as the sum of R_warm_HT
            R_warm = np.sum(R_warm_cable)

        self.setAttribute(self.HalfTurns, 'R_warm', R_warm_cable)
        self.setAttribute(self.General, 'R_warm', R_warm)

    def translateModelDataToTFMHalfTurns(self):
        '''
        This function saves the appropriate BuilderLEDET Inputs dataclass values for the HalfTurns dataclass attributes.
        The saved data are arrays with len equal to the total number of HalfTurns
        '''
        # Values that can't be directly obtained from the Inputs dataclass
        nT = self.ledet_inputs['nT']
        HalfTurns_to_group = np.repeat(np.arange(len(nT)) + 1, nT)
        self.setAttribute(self.HalfTurns, 'HalfTurns_to_group', HalfTurns_to_group)
        HalfTurns_to_conductor = self.conductor_to_group[HalfTurns_to_group - 1]
        self.setAttribute(self.HalfTurns, 'HalfTurns_to_conductor', HalfTurns_to_conductor)
        turns_to_condutc = HalfTurns_to_conductor[::2]
        nc = np.repeat(nT, nT)
        self.setAttribute(self.HalfTurns, 'Nc', nc)

        # Values that can be directly obtained from the Inputs dataclass
        for keyInputData, value in self.ledet_inputs.items():
            keyTFM = lookupModelDataToTFMHalfTurns(keyInputData)
            if keyTFM in self.HalfTurns.__annotations__:
                if isinstance(value, list):
                    self.setAttribute(self.HalfTurns, keyTFM, np.array(value))
                else:
                    self.setAttribute(self.HalfTurns, keyTFM, value[HalfTurns_to_group - 1])

        # Fitting value for ISCL, varying between C=1 (Ns=8) and C=1.15 (Ns=40) [-]
        # Reference: Arjan's Thesis, Chapter 4, Page 78, Equation 4.31
        C_strand = 0.0046875 * self.HalfTurns.n_strands + 0.9625
        self.setAttribute(self.HalfTurns, 'C_strand', C_strand)


    def translateModelDataToTFMStrands(self):
        '''
        This function saves the appropriate BuilderLEDET Inputs dataclass values for the Strands dataclass attributes.
        The saved data are arrays with len equal to the total number of Strands
        '''
        self.calculate_field_contributions()
        strands_to_conductor = np.repeat(self.HalfTurns.HalfTurns_to_conductor, self.HalfTurns.n_strands)
        self.setAttribute(self.Strands, 'strands_to_conductor', strands_to_conductor)
        for keyLedetData, value in self.ledet_inputs.items():
            keyTFM = lookupModelDataToTFMStrands(keyLedetData)
            if keyTFM in self.Strands.__annotations__:
                repeated_value = np.repeat(value[self.HalfTurns.HalfTurns_to_group - 1], self.HalfTurns.n_strands)
                self.setAttribute(self.Strands, keyTFM, repeated_value)

    def calculate_field_contributions(self):  # Utility function to calculate f_mag in translateModelDataToTFMStrands
        '''
        Calculates the field in each filament of the MB magnet.
        It saves in the Strands dataclass vectors of shape [len(freq), n_strands]
        : f_mag, f_mag_X and f_mag_Y taken from Roxie
        : f_mag, f_mag_X and f_mag_Y taken from the magnet Comsol Model with no effects included
        '''

        f_mag_Roxie, f_mag_X_Roxie, f_mag_Y_Roxie = self.retrieve_field_contributions_Roxie()

        if self.General.magnet_name != 'MB_2COILS':
            local_library_path = os.path.join(Path(self.General.local_library_path).resolve(), 'TFM_input')
            name = self.General.magnet_name
            mapping = np.vectorize(lambda t: complex(t.replace('i', 'j')))

            # Taking the excel file containing the field values of the Comsol Model without any effect
            full_file_Comsol = Path(os.path.join(local_library_path, f'Field_Map_{name}.csv')).resolve()
            df_Comsol = pd.read_csv(full_file_Comsol, header=None, dtype=str, na_filter=False)
            # Extracting the frequency values from the file
            frequency = np.array(df_Comsol.iloc[1, 2::2]).astype(float)
            # Transforming the values in the files in the format (Re + i*Im) to  (Re + j*Im) -> correct complex format for Python
            df_Comsol = mapping(df_Comsol.values[2:, 2:]).T
            f_mag_X_Comsol = np.sqrt(np.real(df_Comsol[::2, :] * np.conjugate(df_Comsol[::2, :]))) * np.sign(f_mag_X_Roxie)
            f_mag_Y_Comsol = np.sqrt(np.real(df_Comsol[1::2, :] * np.conjugate(df_Comsol[1::2, :]))) * np.sign(f_mag_Y_Roxie)
            f_mag_Comsol = np.sqrt(f_mag_X_Comsol ** 2 + f_mag_Y_Comsol ** 2)

            self.frequency = frequency

        self.setAttribute(self.Strands, 'f_mag_X_Roxie', f_mag_X_Roxie)
        self.setAttribute(self.Strands, 'f_mag_Y_Roxie', f_mag_Y_Roxie)
        self.setAttribute(self.Strands, 'f_mag_Roxie', f_mag_Roxie)

        if self.General.magnet_name != 'MB_2COILS':
            self.setAttribute(self.Strands, 'f_mag_X_Comsol', f_mag_X_Comsol)
            self.setAttribute(self.Strands, 'f_mag_Y_Comsol', f_mag_Y_Comsol)
            self.setAttribute(self.Strands, 'f_mag_Comsol', f_mag_Comsol)

    def setOptions(self):
        '''
        This function sets to the Option DataClass the flags to know which effects should be included in the magnet model

        :attribute flag_PC: if True includes the Persistent Current effect
        :attribute flag_IFCC: if True includes the Inter Filament Coupling Current effect
        :attribute flag_ISCC: if True includes the Inter Strands Coupling Current effect
        :attribute flag_Wedge: if True includes the Wedge effect
        :attribute flag_CB: if True includes the Cold Bore effect
        :attribute flag_ED: if True includes the Eddy Currents effect in the Copper Sheath
        :attribute flag_BS: if True includes the BeamScreen effect in the Copper Sheath
        :attribute flag_SC: set to True depending on the T (indicates if a magnet is in Superconducting state)
        '''
        if self.temperature <  min(self.ledet_inputs['Tc0_NbTi_ht_inGroup']):
            flag_SC = True
        else:
            flag_SC = False

        self.setAttribute(self.Options, 'flag_SC', flag_SC)
        self.calculate_warm_resistance()

        Effects = {}
        for keyTFMData, value in self.TFM_inputs.__dict__.items():
            if keyTFMData.startswith('flag') and keyTFMData != 'flag_T' and keyTFMData != 'flag_debug':
                self.setAttribute(self.Options, keyTFMData, value)

                # Saving in a Dictionary the effects names and the flag values (no BS because not implemented yet)
                if keyTFMData != 'flag_BS':
                    eff = keyTFMData.split('_')[-1]
                    Effects[eff] = value
        self.Effects = Effects



    ####################################################################################################################
    ############################################### LIBRARY GENERATION ###############################################

    def generate_library(self, output_path: str):
        '''
        This function generates a suitable lib file for the magnet simulation in XYCE.
        It follows this structure:
         - Calculation of the magnet inductance values using the 'calculate_Inductance_Turn' function.
         - Initialization of the magnet circuit through the 'generate_magnet_circuit_library' function.
         - Setting up the '.FUNC' parameter for each effect using the 'generate_function_library' function.
         - Defining the circuit parameters for each effect and each loop via the 'generate_loop_library' function.
         - Establishing the mutual coupling between each effect with the 'generate_coupling_library' function.
         - Computing the mutual coupling between the inductance of different loops through the 'calculate_MutualInductance_Turns' function.

         :param output_path: directory where the lib file must be saved
        '''
        # The lib file is build using a Dictionary of components
        Netlist = {}
        apertures = self.General.apertures
        groups = self.General.groups
        # These nodes are the ones used in the circuit yaml file as magnet nodes
        Nodes = ['EE_AP1_IN', 'EE_AP_MID', 'EE_AP2_OUT', '1_GND']

        # Comments initialization
        Comm_newline = Component(type='comment', nodes=[], value=' ')  # Introduces an empty line in the file
        Netlist['Comment_newline_b_Magnet'] = Comm_newline

        Comm = Component(type='comment', nodes=[], value='* If flag_T = 0, the magnet circuit is made of just one Section per Aperture')
        Netlist['Comm_func1'] = Comm
        Comm = Component(type='comment', nodes=[], value='* If flag_T = 1, the magnet circuit is made of multiple Sections per Aperture')
        Netlist['Comm_func2'] = Comm
        Comm = Component(type='comment', nodes=[], value='* Each section has a C_GND and a V_tap, R_warm and L in series')
        Netlist['Comm_func3'] = Comm
        Comm = Component(type='comment', nodes=[], value='* The suffix of each element have the format _{aperture}_{group}')
        Netlist['Comm_func4'] = Comm
        Comm = Component(type='comment', nodes=[], value='* Each capacitance is calculated as C_ground /(tot_num_apertures * tot_num_groups)')
        Netlist['Comm_func5'] = Comm
        Comm = Component(type='comment', nodes=[], value='* Each V_tap = 0 since it is just used to access the current in that group')
        Netlist['Comm_func6'] = Comm
        Comm = Component(type='comment', nodes=[], value='* Each R_warm is calculated as R_warm_tot / (tot_num_apertures * tot_num_groups)')
        Netlist['Comm_func7'] = Comm
        Comm = Component(type='comment', nodes=[], value='* Each L value is taken from the the Inductance Matrix in BuilderLEDET, according to the contribute of the turns associated to that group')
        Netlist['Comm_func8'] = Comm
        Comm = Component(type='comment', nodes=[], value='* The coupling coefficients between different L are at the end of the lib file')
        Netlist['Comm_func9'] = Comm
        Netlist['Comm_func_nl'] = Comm_newline

        Comm_space = Component(type='comment', nodes=[], value='*'*150)  # Introduces a frae of stars in the file
        Netlist['Comment_Space_B_Magnet'] = Comm_space
        Comm = Component(type='comment', nodes=[], value='*'*50 + ' MAGNET ' + '*'*80)
        Netlist['Comment_Magnet'] = Comm
        Netlist['Comment_Space_AB_Magnet'] = Comm_space
        # Comments to explain the magnet circuit
        ################################## INITIALIZE MAGNET CIRCUIT ###################################################

        # Calculation of the magnet inductance values for each turn and aperture
        L_magnet = self.calculate_Inductance_Sections()
        Netlist = self.generate_magnet_circuit_library(Netlist=Netlist, Nodes=Nodes)

        Netlist['Comment_newline_After_Magnet1'] = Comm_newline
        Netlist['Comment_newline_After_Magnet2'] = Comm_newline

        ################################## COUPLING EFFECTS ###################################################

        Netlist['Comment_Space_B_Magnet_2'] = Comm_space
        Comm = Component(type='comment', nodes=[], value='*' * 50 + ' COUPLING OF THE EFFECTS ' + '*' * 80)
        Netlist['Comment_eff'] = Comm
        Netlist['Comment_Space_eff'] = Comm_space

        Comm = Component(type='comment', nodes=[], value='* This magnet model is taking into account all the effects that can be seen below')
        Netlist['Comm_func1_eff'] = Comm
        Comm = Component(type='comment', nodes=[], value='* Each effect, besides of Wedge and ColdBore, has a different equivalent circuit for each aperture and for each group in that aperture ')
        Netlist['Comm_func2_eff'] = Comm
        Comm = Component(type='comment', nodes=[], value='* If flag_T = 0 we have a different group for each cable conductor (Data taken from Builder LEDET), we have instead just one section per aperture')
        Netlist['Comm_func3_eff'] = Comm
        Comm = Component(type='comment', nodes=[], value='* If flag_T = 1 and the parameters turn_to_aperture and turn_to_group in the circuit yaml file are empty, group = section = group described above')
        Netlist['Comm_func4_eff'] = Comm
        Comm = Component(type='comment', nodes=[], value='* If flag_T = 1 and the parameters turn_to_aperture and turn_to_group in the circuit yaml file are NOT empty, group = section = specified in these parameters')
        Netlist['Comm_func5_eff'] = Comm
        Comm = Component(type='comment', nodes=[], value='* The suffix of each element have the format _{aperture}_{group}')
        Netlist['Comm_func6_eff'] = Comm
        Comm = Component(type='comment', nodes=[], value='* Each group has a L, R, V and R_gnd')
        Netlist['Comm_func7_eff'] = Comm
        Comm = Component(type='comment', nodes=[], value='* Each effect has a number of M FUNC. equal to the number of groups')
        Netlist['Comm_func8_eff'] = Comm
        Comm = Component(type='comment', nodes=[], value='* The values of M FUNC. can be changed thanks to the function change_coupling_parameter in BuilderTFM')
        Netlist['Comm_func9_eff'] = Comm
        Comm = Component(type='comment', nodes=[], value='* If flag_T = 0 the network model of each effect is coupled to the magnet inductance of its aperture')
        Netlist['Comm_func10_eff'] = Comm
        Comm = Component(type='comment', nodes=[], value='* If flag_T = 1 the network model of a group for each effect is coupled to the corresponding magnet inductance of the same group and same aperture')
        Netlist['Comm_func11_eff'] = Comm
        Comm = Component(type='comment', nodes=[], value='* Each network model of a group is coupled to all the other network models of the others effects in that group ')
        Netlist['Comm_func12_eff'] = Comm
        Netlist['Comm_func_nl_eff'] = Comm_newline
        Netlist['Comm_func_space_eff'] = Comm_space

        effs = list(self.Effects.keys()) # List of all the possible effects that might be included in the magnet
        effs_notCond = list(self.Effects.keys())[:3]  # List of the effects that are not conductor losses (Wedge, CB)


        for eff_ind in range(len(effs)): # Looping through all the effects
            eff = effs[eff_ind]
            Comm = Component(type='comment', nodes=[], value='*'*50 + f' EFFECT {eff} ' + '*'*80)
            Netlist[f'Comment_{eff}'] = Comm
            Netlist[f'Comment_{eff}_space_Aft'] = Comm_space

            # Defining the L, M and R functions for each effect and each loop
            Netlist = self.generate_function_library(Netlist=Netlist, eff=eff, eff_ind=eff_ind)

            for ap in range(1, apertures + 1): # Looping through the apertures
                Comm_Ap = Component(type='comment', nodes=[], value='*'*50 + f' APERTURE {ap} ' + '*'*80 )
                Netlist[f'Comment_{eff}_ap_{ap}'] = Comm_Ap

                for n in range(1, groups + 1):  # Looping through all the groups in that aperture
                    if eff in effs_notCond and n != 1: continue # This loop need to be executed just for group == 1 for the not groupned effects (CB, Wedge)

                    # Initialize the loop comment just if the number of groups != 1 and eff != Wedge and CB
                    if groups != 1 and eff not in effs_notCond:
                        Comm_group = Component(type='comment', nodes=[], value='*'*6 + f' LOOP {n} ' + '*'*6)
                        Netlist[f'Comment_{eff}_group_{n}_ap_{ap}_{n}'] = Comm_group
                    Comm_Ap_d = Component(type='comment', nodes=[], value=f'* Coupled {eff} current loop ')
                    Netlist[f'Comment_{eff}_ap_{ap}_{n}'] = Comm_Ap_d

                    # Defining the circuit parameters L, R, V, R_gnd and K for the different effects and each loop
                    Netlist = self.generate_loop_library(Netlist=Netlist, eff=eff, ap=ap, n=n)

                    for eff_coup_ind in range(eff_ind + 1, len(effs)): # Loop to assign the mutual coupling between the Conductor Losses effects for each loop
                        if eff in effs_notCond: continue  # This loop is just for the Conductor Losses effects
                        eff_coup = effs[eff_coup_ind]
                        # Establishing the mutual coupling between each effect among the conductor Losses ones
                        Netlist = self.generate_coupling_library(Netlist=Netlist, eff=eff, eff_coup=eff_coup, ap=ap, n=n)

                    if eff not in effs_notCond: Netlist[f'Comment_newline_{eff}_{ap}_{n}'] = Comm_newline

                for eff_coup_ind in range(eff_ind + 1, len(effs)):  # Loop to all the effcts subsequent at eff to assign the mutual coupling between the NOT Conductor Losses effects and the Conductor ones
                    if eff not in effs_notCond: continue # This loop is just for the NOT Conductor Losses effects --> it is outside of the groups loop (one per aperture)
                    eff_coup = effs[eff_coup_ind]
                    for n in range(1, groups + 1): # Looping through all the groups in order to have together the all the couplings for that aperture
                        # Establishing the mutual coupling between each effect among the conductor Losses ones
                        Netlist = self.generate_coupling_library(Netlist=Netlist, eff=eff, eff_coup=eff_coup, ap=ap, n=n)

                Netlist[f'Comment_newline_{eff}_ap_{ap}'] = Comm_newline
            Netlist[f'Comment_newline_{eff}_ap_final'] = Comm_newline
            Netlist[f'Comment_final_space_{eff}'] = Comm_space

        # Computing the mutual coupling between the inductance of the magnet of different groups
        Netlist['comm_mutual'] = Component(type='comment', nodes=[], value='*Mutual coupling between Magnet Inductances')
        Netlist = self.calculate_MutualInductance_Sections(Netlist=Netlist)

        Netlist['newline_final'] = Comm_newline
        Netlist['space_final'] = Comm_space

        # Initializing the parameters that must be printed on top of the lib file
        Params = {}
        # Initialization of the magnet circuit Inductances
        for key, value in L_magnet.items():
            Params[f'{key}_value'] = value

        Params['T_mag'] = self.temperature
        Params['l_m'] = self.General.magnet_length
        Params['C_ground'] = self.General.C_ground
        Params['L_mag'] = self.General.L_mag
        for eff, value in self.Effects.items(): # Flag names and values for each effect
            Params[f'flag_{eff}'] = int(value)

        circuit_name = self.General.magnet_name + '_TFM'  # Initializing the circuit name as the magnet name + TFM

        # Passing everything to XYCE to write the lib file from the dict of Components
        PX = ParserXYCE()
        PX.write_library(output_path=output_path, name=circuit_name, nodes=Nodes, params=Params, Netlist=Netlist)

    def calculate_Inductance_Sections(self) -> dict:
        '''
        This function initialize the inductance values for each turn for the magnet circuit of the lib file used in XYCE

        :return L: a dictionary with the name and the value of L_mag for each turn
        '''
        flag_T = self.flag_T
        M_block = np.array(self.ledet_inputs['M_InductanceBlock_m'])
        fL_L = np.array(self.ledet_inputs[
                            'fL_L'])  # Current-dependent effect of the iron on the differential inductance of the magnet
        fL_I = np.array(self.ledet_inputs['fL_I'])  # Current corresponding to fL_L
        length_mag = self.General.magnet_length
        I_magnet = self.General.I_magnet
        apertures = self.General.apertures
        n_Turns = self.General.num_HalfTurns // 2
        turns_to_sections = self.Turns.turns_to_sections
        turns_to_apertures = self.Turns.turns_to_apertures
        sections = max(turns_to_sections)

        if M_block.all() == 0:
            M_block_path = os.path.join(Path(self.General.local_library_path), f'{self.General.magnet_name}_MutualInductanceMatrix_TFM.csv')
            df = pd.read_csv(M_block_path, skiprows=1, header=None)
            M_block = df.values

        fL = np.interp(I_magnet, fL_I, fL_L)  # Interpolation to calculate the fL_L for our current
        L = {}

        L_sum = 0
        for ap in range(1, apertures + 1): # Looping through the apertures
            idx_ap = np.where(turns_to_apertures == ap)[0]
            if not flag_T:
                # If not flag_T we just need one L_mag per aperture = sum of the L block * length_mag * fL
                M = M_block[np.ix_(idx_ap, idx_ap)] # Taking the correct L block corresponding to this aperture
                L_sum_ap = np.sum(M) * length_mag * fL
                L_sum += L_sum_ap
                L[f'L_{ap}'] = L_sum_ap
            else:
                # If flag_T we need one L_mag per group per aperture
                for section in range(1, sections + 1):
                    L_sum = 0
                    idx_section = np.where(turns_to_sections == section)[0]  # Finds the indexes of the turns that belong to the current section
                    idx = np.intersect1d(idx_section, idx_ap)  # Taking only the indexes that correspond also to the current aperture
                    M = M_block[np.ix_(idx, idx)]  # Taking the correct L block corresponding to this aperture
                    L_sum_ap_section = np.sum(M) * length_mag * fL
                    L_sum += L_sum_ap_section
                    L[f'L_{ap}_{section}'] = L_sum_ap_section

        self.setAttribute(self.General, 'L_mag', L_sum)

        return L


    def generate_magnet_circuit_library(self, Netlist: dict, Nodes: list) -> dict:
        '''
        This function initialize the magnet circuit for the circuit lib file used in XYCE

        :param Netlist: a dictionary of Components where the new components must be added.
        :param Nodes: a list of 4 nodes corresponding to the ones of the magnet initialization in the circuit yaml file.
        :param L_magnet: a dictionary of Inductances values that must be inserted in the magnet cicruit

        :return Netlist: it returns the updated Netlist with the magnet circuit components
        '''

        apertures = self.General.apertures
        flag_T = self.flag_T
        sections = max(self.Turns.turns_to_sections)
        turns_to_sections = self.Turns.turns_to_sections
        C_g = self.General.C_ground/(sections * apertures)
        R_w = self.General.R_warm /(sections* apertures)
        type = 'standard component'
        Comm_newline = Component(type='comment', nodes=[], value=' ')
        Comm_space = Component(type='comment', nodes=[], value='*'*150)

        count_nodes = 0 # Starting the node counting
        # Initialize comments for V_ap
        Comm_input_V_ap1 = Component(type='comment', nodes=[], value='* Fake voltage source to easily access the input current')
        Netlist['Comm_input_tap'] = Comm_input_V_ap1

        # Initialize V_ap1 to easily access the input current
        V_ap1 = Component(type=type, nodes=[Nodes[0], f'EE{count_nodes:03d}'], value='0')
        Netlist['V_ap_1'] = V_ap1
        Netlist['Comm_nl_after_input_1'] = Comm_newline

        for ap in range(1, apertures + 1): # Looping through the apertures
            # To add the comment 'APERTURE n'
            Comm_Ap = Component(type='comment', nodes=[], value='*'*50 + f' APERTURE {ap} ' + '*'*80)
            Netlist[f'Comment_Magnet_Ap{ap}'] = Comm_Ap
            # Defining the number of sub circuits for each aperture, based on flag_T value, if not flag_T the turn is always 1

            for n in range(1, sections + 1): # Looping for the number of turns
                if sections != 1: # Adding Turn comment only if number of turns != 1
                    Comm_turning = Component(type='comment', nodes=[], value=f'****** Group {n} ******')
                    Netlist[f'Comment_turning_{ap}_{n}'] = Comm_turning

                # Add C_GND, R_warm, L and V_tap for each subcircuit, considering that
                if ap == 2 and n == 1:  # If we are are between one Aperture and the other
                    # 1) the closest C_GND (first of the second Ap) must be attached to the central nod
                    C_GND = Component(type=type, nodes=[Nodes[1], Nodes[3]], value=f'{C_g}')
                    # 2) the closest V_tap (first of the second Ap) must be attached to the central node
                    V_tap = Component(type=type, nodes=[Nodes[1], f'EE{count_nodes:03d}'], value='0')
                else:
                    # Normal situation
                    C_GND = Component(type=type, nodes=[f'EE{count_nodes:03d}', '1_GND'], value=f'{C_g}')
                    V_tap = Component(type=type, nodes=[f'EE{count_nodes:03d}', f'EE{count_nodes + 1:03d}'], value='0')
                    count_nodes += 1 # Update node counting

                R_warm = Component(type=type, nodes=[f'EE{count_nodes:03d}', f'EE{count_nodes + 1:03d}'], value=f'{R_w}')
                count_nodes += 1 # Update node counting

                L_mag = f'L_{ap}_value' if not flag_T else f'L_{ap}_value'# Take the correct value of L_mag from the input dict

                if ap == 1 and n == sections: # If we are are between one Aperture and the other
                    # 3) the closest L (last of the first Ap) must be attached to the central node
                    L = Component(type=type, nodes=[f'EE{count_nodes:03d}', Nodes[1]], value=f'{L_mag}')
                else:
                    L = Component(type=type, nodes=[f'EE{count_nodes:03d}', f'EE{count_nodes + 1:03d}'], value=f'{L_mag}')
                count_nodes += 1 # Update node counting

                Netlist[f'C_GND_{ap}_{n}'] = C_GND
                Netlist[f'V_tap_{ap}_{n}'] = V_tap
                Netlist[f'R_warm_{ap}_{n}'] = R_warm
                Netlist[f'L_{ap}_{n}'] = L
                Netlist[f'Comment_newline_Magnet_{ap}_{n}'] = Comm_newline

        # Initialize comments for the last Capacitance and V_ap2
        Netlist[f'Comment_space_Magnet_out'] = Comm_space
        Comm_out_V_ap2 = Component(type='comment', nodes=[],
                                   value='* Fake voltage source to easily access the output current')
        Netlist['Comm_output_tap'] = Comm_out_V_ap2

        # Adding last V_ap2 to complete the circuit
        V_ap2 = Component(type=type, nodes=[f'EE{count_nodes:03d}', Nodes[2]], value='0')
        Netlist['V_ap_2'] = V_ap2

        return Netlist


    def generate_function_library(self, Netlist: dict, eff: str, eff_ind: int) -> dict:
        '''
        This function initialize the function parameter .FUNC for a given effect in the lib file used in XYCE

        :param Netlist: a dictionary of Components where the new components must be added.
        :param eff: name of the effect for which we need the .FUNC parameters
        :param eff_ind: index of this effect fin the effs list

        :return Netlist: it regroups the updated Netlist with the magnet circuit components
        '''

        effs_notCond = list(self.Effects.keys())[:3] # Effects which are not the conductor losses
        effs = list(self.Effects.keys())  # All effects
        groups = self.General.groups

        type_func = 'function'
        default_1 = Component(type=type_func, nodes=['1', ], value='(1.0,1.0) (100000.0,1.0)') # Default function for L, R (default value = 1)
        default_0 = Component(type=type_func, nodes=['1', ], value='(1.0,0.0) (100000.0,0.0)') # Default function for M (default value = 0)
        Comm_newline = Component(type='comment', nodes=[], value=' ')

        for n in range(1, groups + 1): # looping through the groups
            if eff in effs_notCond and n != 1: continue # If eff is not conductor losses we need to create the function parameter just once
            Netlist[f'{eff}_L_{n}'] = default_1
            if eff != 'PC': Netlist[f'{eff}_R_{n}'] = default_1
            Netlist[f'{eff}_M_{n}'] = default_0
            Netlist[f'Comment_newline_func_{eff}_{n}'] = Comm_newline

        for eff_coup_ind in range(eff_ind + 1, len(effs)): # looping through any effect subsequent to this one
            for n in range(1, groups + 1): # looping through the groups
                eff_coup = effs[eff_coup_ind]
                if (eff_coup in effs_notCond or eff == 'IFCC'):
                    # For the coupling between IFCC and PC we need only one M_PC_IFCC(1)
                    # For the coupling between Wedge and CB we need only one M_CB_wedge(1)
                    if n != 1: continue
                    Netlist[f'M_{eff_coup}_{eff}'] = default_0
                else: # Fpor all the others we need one M function per loop
                    Netlist[f'M_{eff_coup}_{eff}_{n}'] = default_0
            Netlist[f'Comment_{eff_coup}_{eff}'] = Comm_newline

        return Netlist

    def generate_loop_library(self, Netlist: dict, eff: str, ap: int, n: int) -> dict:
        '''
        This function initialize the circuit parameter for a given effect in a given aperture and for a given loop of the lib file

        :param Netlist: a dictionary of Components where the new components must be added.
        :param eff: name of the effect for which we need the circuit parameters
        :param ap: index of the aperture
        :param n: index of the groups

        :return Netlist: it returns the updated Netlist with the magnet circuit components
        '''
        effs = self.Effects.items()
        type = 'standard component'
        Comm_newline = Component(type='comment', nodes=[], value=' ')
        effs_notCond = list(self.Effects.keys())[:3]
        flag_T = self.flag_T
        groups = self.General.groups

        # If eff == CB or eff == Wedge no need to have multiples circuit component names
        suff = f'{ap}' if eff in effs_notCond else f'{ap}_{n}'
        suff_L = f'{ap}' if not self.flag_T else f'{ap}_{n}'

        if eff != 'PC':  # Assigning L, R, V if eff != 'PC'
            L = Component(type=type, nodes=[f'{eff}_{suff}a', f'{eff}_{suff}b'], value=f'{eff}_L_{n}(1)')
            Netlist[f'L_{eff}_{suff}'] = L
            R = Component(type=type, nodes=[f'{eff}_{suff}b', f'{eff}_{suff}c'], value=f'{eff}_R_{n}(1)')
            Netlist[f'R_{eff}_{suff}'] = R
            V = Component(type=type, nodes=[f'{eff}_{suff}c', f'{eff}_{suff}a'], value='0')
            Netlist[f'V_{eff}_{suff}'] = V
        else:  # If eff == 'PC' add parameter to L and assigns B instead of L
            param = {}
            param['IC'] = f'{eff}_{n}'
            L = Component(type=type, nodes=[f'{eff}_{suff}a', f'{eff}_{suff}b'], value=f'{eff}_L_{n}(1)', parameters=param)
            Netlist[f'L_{eff}_{ap}_{n}'] = L
            I = f'(PC_M_{n}(1)*I(V_tap_{ap}_1)' if not flag_T else f'(PC_M_{n}(1)*I(V_tap_{ap}_{n})'
            for eff_c, value in effs:
                if eff == eff_c or not value: continue
                if eff_c in effs_notCond:
                    I = I + f'+M_PC_{eff_c}_1(1)*flag_{eff_c}*I(V_{eff_c}_{ap})'
                elif eff_c == 'IFCC':
                    I = I + f'+M_PC_{eff_c}(1)*flag_{eff_c}*I(V_{eff_c}_{ap}_{n})'
                else:
                    I = I + f'+M_PC_{eff_c}_{n}(1)*flag_{eff_c}*I(V_{eff_c}_{ap}_{n})'
            I = I + ')'
            B = Component(type='behavioral-current component', nodes=[f'{eff}_{suff}a', f'{eff}_{suff}b'], value=I + f'/{eff}_L_{n}(1)')
            Netlist[f'B_{eff}_{ap}_{n}'] = B

        # Assigning R_gnd for each effect
        R_gnd = Component(type=type, nodes=[f'{eff}_{suff}a', '0'], value='10G')
        Netlist[f'R_gnd_{eff}_{suff}'] = R_gnd

        Netlist[f'Comment_newline_K_{eff}_{suff}'] = Comm_newline
        Comm_Ap_K = Component(type='comment', nodes=[], value=f'* Coupling groups and magnet')
        Netlist[f'Comment_{eff}_{suff}_K'] = Comm_Ap_K

        # Assigning the coupling coefficient between the eff and the inductances of the magnet
        if eff == 'PC' or eff == 'IFCC': # Assigning K_value depending on superconductive or not (PC and IFCC only exclusively superconductive effects)
            K_value = f'flag_{eff}*{eff}_M_{n}(1)/sqrt(L_{suff_L}_value*{eff}_L_{n}(1))*{int(self.Options.flag_SC)}'
        else:
            K_value = f'flag_{eff}*{eff}_M_{n}(1)/sqrt(L_{suff_L}_value*{eff}_L_{n}(1))'

        if (eff not in effs_notCond or (eff in effs_notCond and not self.flag_T)):  # If eff Conductor Losses or if eff NOT conductor losses but not flag_T
            if flag_T:
                K = Component(type=type, nodes=[f'L_{eff}_{suff}', f'L_{ap}_{n}'], value=K_value)
            else: # If not flag_T there is only one L per aperture
                K = Component(type=type, nodes=[f'L_{eff}_{suff}', f'L_{ap}_1'], value=K_value)
            Netlist[f'K_{eff}_{suff}'] = K
        else:  # If eff == 'Wedge' or == 'CB' and flag_T K_CB and K_Wedge must be coupled to each section
            for i in range(1, groups + 1):
                K = Component(type=type, nodes=[f'L_{eff}_{ap}', f'L_{ap}_{i}'], value=K_value)
                Netlist[f'K_{eff}_{ap}_{i}'] = K

        return Netlist

    def generate_coupling_library(self, Netlist: dict, eff: str, eff_coup: str, ap: int, n: int) -> dict:
        '''
        This function initialize the mutual coupling coefficients between one eff and another for a given aperture and a given loop

        :param Netlist: a dictionary of Components where the new components must be added.
        :param eff: name of the first effect
        :param eff_coup: name of the coupled effect
        :param ap: index of the aperture
        :param n: index of the loop

        :return Netlist: it returns the updated Netlist with the magnet circuit components
        '''

        effs = list(self.Effects.keys()) # All effects
        effs_notCond = list(self.Effects.keys())[:3] # effects not conductor losses
        type = 'standard component'

        if (eff_coup in effs_notCond and eff in effs_notCond):
            # If both effects are not Cond Losses then they both have just one M and L, the mutual M doesn't have a group suffix and the nodes as well
            K_coup_value = f'flag_{eff}*flag_{eff_coup}*M_{eff_coup}_{eff}(1)/sqrt({eff_coup}_L_1(1)*{eff}_L_1(1))'
            K_coup = Component(type=type, nodes=[f'L_{eff_coup}_{ap}', f'L_{eff}_{ap}'], value=K_coup_value)
            Netlist[f'K_{eff_coup}_{eff}_{ap}'] = K_coup
        elif (eff in effs_notCond):
            # If only one effect is not Cond Losses then it has just one M and L, the node corresponding to eff has no group suffix
            K_coup_value = f'flag_{eff}*flag_{eff_coup}*M_{eff_coup}_{eff}_{n}(1)/sqrt({eff_coup}_L_{n}(1)*{eff}_L_1(1))'
            K_coup = Component(type=type, nodes=[f'L_{eff_coup}_{ap}_{n}', f'L_{eff}_{ap}'], value=K_coup_value)
            Netlist[f'K_{eff_coup}_{eff}_{ap}_{n}'] = K_coup
        else:
            if eff == 'IFCC' and eff_coup == 'PC': # The mutual coupling function between PC and IFCC doesn't have a n suffix
                K_coup_value = f'-1*flag_{eff}*flag_{eff_coup}*M_{eff_coup}_{eff}(1)/sqrt({eff_coup}_L_{n}(1)*{eff}_L_{n}(1))*{int(self.Options.flag_SC)}'
            elif eff_coup == 'PC':
                K_coup_value = f'-1*flag_{eff}*flag_{eff_coup}*M_{eff_coup}_{eff}_{n}(1)/sqrt({eff_coup}_L_{n}(1)*{eff}_L_{n}(1))'
            else:
                K_coup_value = f'flag_{eff}*flag_{eff_coup}*M_{eff_coup}_{eff}_{n}(1)/sqrt({eff_coup}_L_{n}(1)*{eff}_L_{n}(1))'

            K_coup = Component(type=type, nodes=[f'L_{eff_coup}_{ap}_{n}', f'L_{eff}_{ap}_{n}'], value=K_coup_value)
            Netlist[f'K_{eff_coup}_{eff}_{ap}_{n}'] = K_coup

        return Netlist


    def calculate_MutualInductance_Sections(self, Netlist: dict) -> dict:
        '''
        This function initialize the Mutual inductance Coupling coefficient values between each turn for the magnet circuit of the lib file used in XYCE

        :param Netlist: a dictionary of Components where the new components must be added

        :return Netlist: it returns the updated Netlist with the magnet circuit components
        '''
        flag_T = self.flag_T
        M_block = np.array(self.ledet_inputs['M_InductanceBlock_m'])
        fL_I = np.array(self.ledet_inputs['fL_I'])
        fL_L = np.array(self.ledet_inputs['fL_L'])
        length_mag = self.General.magnet_length
        I_magnet = self.General.I_magnet
        apertures = self.General.apertures
        type = 'standard component'
        n_Turns = self.General.num_HalfTurns // 2
        turns_to_sections = self.Turns.turns_to_sections
        turns_to_apertures = self.Turns.turns_to_apertures
        sections = np.max(turns_to_sections)

        if M_block.all() == 0:
            M_block_path = os.path.join(Path(self.General.local_library_path),
                                        f'{self.General.magnet_name}_MutualInductanceMatrix_TFM .csv')
            df = pd.read_csv(M_block_path, skiprows=1, header=None)
            M_block = df.values

        fL = np.interp(I_magnet, fL_I, fL_L)
        portion = n_Turns // apertures
        idx_ap1 = np.where(turns_to_apertures == 1)[0]  # Extracting the turns corresponding to the first Aperture
        idx_ap2 = np.where(turns_to_apertures == 2)[0]  # Extracting the turns corresponding to the second Aperture

        if not flag_T: # if NOT flag_T then we have only the coupling between the 2 apertures
            if apertures == 2: # Check if there are 2 apertures, otherwise no coupling
                M_coup = np.sum(M_block[np.ix_(idx_ap1, idx_ap2)]) * length_mag * fL  # In this case we have to take the block on the bottom left
                K_coup_value = f'{M_coup}/sqrt(L_1_value*L_2_value)'
                K_mag = Component(type=type, nodes=['L_1_1', f'L_2_1'], value=K_coup_value)
                Netlist[f'K_mag_1_2'] = K_mag

        elif apertures != 1 or sections != 1: # Check if either there is more than 1 Ap or more than 1 group, otherwise no coupling
            # Loop to calculate the M for the coupling of different sections in the same aperture
            for ap in range(1, apertures+1):
                idx =  np.where(turns_to_apertures == ap)[0]
                # Coupling between different sections of the same aperture
                for group1 in range(1, sections):
                    indices1 = np.where(turns_to_sections == group1)[0] # Taking the indices corresponding to group1
                    indices1 = np.intersect1d(indices1, idx) # Taking the indices corresponding to group1 and inside the aperture ap
                    for group2 in range(group1 + 1, sections + 1):
                        indices2 = np.where(turns_to_sections == group2)[0]  # Taking the indices corresponding to group2
                        indices2 = np.intersect1d(indices2, idx)  # Taking the indices corresponding to group2 and inside the aperture ap
                        M_coup = M_block[np.ix_(indices1, indices2)] # Taking the M block corresponding to orix_idx = indices1, vert_idx = indices2
                        K_coup_value = f'{np.sum(M_coup) * (length_mag * fL)}/sqrt(L_{ap}_{group1}_value*L_{ap}_{group2}_value)'
                        K_mag = Component(type=type, nodes=[f'L_{ap}_{group1}', f'L_{ap}_{group2}'], value=K_coup_value)
                        Netlist[f'K_mag_{ap}_{group1}_{ap}_{group2}'] = K_mag

            # Coupling between sections of different apertures
            if apertures == 2: # Only if apertures == 2
                 for group1 in range(1, sections + 1): # All the sections of the 1st ap
                     indices1 = np.where(turns_to_sections == group1)[0] # Taking index of turns that belong to group 1
                     indices1 = np.intersect1d(indices1, idx_ap1) # Taking index of turns taht belongs to group 1 and ap 1
                     for group2 in range(1, sections + 1): # All the sections of the 2nd Ap
                         indices2 = np.where(turns_to_sections == group2)[0]  # Taking index of turns that belong to group 2
                         indices2 = np.intersect1d(indices2, idx_ap2)  # Taking index of turns taht belongs to group 2 and ap 2
                         M = M_block[np.ix_(indices1, indices2)]
                         K_coup_value = f'{np.sum(M) * (length_mag * fL)}/sqrt(L_1_{group1}_value*L_2_{group2}_value)'
                         K_mag = Component(type=type, nodes=[f'L_1_{group1}', f'L_2_{group2}'], value=K_coup_value)
                         Netlist[f'K_mag_1_{group1}_2_{group2}'] = K_mag

        return Netlist


    ####################################################################################################################
    ############################################### EFFECTS FUNCTIONS ###############################################

    def calculate_PC(self, frequency: np.ndarray, T: float, fMag: np.ndarray, flag_coupling:bool = True, flag_save:bool=False) -> np.ndarray:
        '''
        Function that calculates the equivalent circuit parameter for the persistent currents and save them to the
        PC dataclass

        :param frequency: Frequency vector
        :param T: temperature vector, to be used in the interaction with Eddy-currents
        :param fMag: field-factor for each strand
        :param flag_coupling: if True it means it has to be coupled to another effect
        :param flag_save: if True saves the circuit parameter in the PC dataclass
        '''

        l_magnet = self.General.magnet_length
        ds_filamentary = self.Strands.d_filamentary
        dws = self.Strands.diameter
        RRR = self.Strands.RRR
        groups = self.General.groups
        n_strands = np.sum(self.HalfTurns.n_strands)
        strands_to_conductor = self.Strands.strands_to_conductor

        # Calculating constants
        mu0 = 4 * np.pi / 10 ** 7
        w = 2 * np.pi * frequency.reshape(len(frequency), 1)

        B = self.General.I_magnet*fMag
        rho_el_0 = self.rhoCu_nist(T=T, RRR=RRR, B=B[0, :])

        tb_strand = dws - ds_filamentary

        # Calculate the equivalent circuit parameter
        tau_ed = mu0 / 2 * (dws / 2 * tb_strand / 2) / rho_el_0

        if flag_coupling:
            alpha2 = 1 / np.sqrt(np.sqrt((1 + (w * tau_ed) ** 2)))
        else:
            alpha2 = np.ones(w.shape)

        M_temp = (np.pi / 4 * l_magnet * ds_filamentary * fMag * alpha2)
        Lm = np.array([mu0 * np.pi / 4 * l_magnet] * len(frequency))
        M_if_Pc = mu0 * np.pi / 8 * l_magnet


        # M_pc = np.sqrt(np.sum(M_temp[:, idx_valid], axis=1))
        L_repeated = np.tile(Lm, n_strands)
        L_pc = np.reshape(L_repeated, (len(frequency), n_strands), order='F')
        STC_repeated = np.tile(strands_to_conductor, len(frequency))
        STC_pc = np.reshape(STC_repeated, (len(frequency), n_strands), order='F')
        I_Pc = np.array([0]*len(frequency))
        I_Pc = np.tile(I_Pc, n_strands)
        I_Pc = np.reshape(I_Pc, (len(frequency), n_strands), order='F')

        L_pc = np.squeeze(L_pc)
        STC_pc = np.squeeze(STC_pc)
        M_temp = np.squeeze(M_temp)

        L_group, R_group, M_group, I_group = self.group_components(frequency=frequency, L=L_pc, R=STC_pc, M=M_temp, groups=groups, sort_on='R', I=I_Pc)

        if flag_save:
            self.setAttribute(self.PC, 'M', np.sqrt(2)*M_group)
            self.setAttribute(self.PC, 'I', I_group)
            self.setAttribute(self.PC, 'L', L_group)
            self.setAttribute(self.PC, 'M_PC_IFCC', M_if_Pc)
        else:
            return  np.sqrt(2)*M_group


    def calculate_IFCC(self, frequency: np.ndarray, T: float, fMag: np.ndarray, flag_coupling: bool = True, flag_save: bool = False) -> np.ndarray:
        '''
        Calculates the equivalent IFCL coupling loops for a given temperature and field

        :param frequency: Frequency vector
        :param T: temperature vector
        :param fMag: field-factor for each strand
        :param flag_coupling: if True it means it has to be coupled to another effect
        :param flag_save: if True saves the circuit parameter in the IFCC dataclass
        '''

        w = 2 * np.pi * frequency.reshape(len(frequency), 1)
        mu0 = 4 * np.pi / 10 ** 7

        # Setting all required parameters for the MB magnet
        f_ro_eff = self.Strands.f_rho_effective
        fsc = self.Strands.fsc
        l_mag = self.General.magnet_length
        dws = self.Strands.diameter
        ds_filamentary = self.Strands.d_filamentary
        RRR = self.Strands.RRR
        Lp_f = self.Strands.fil_twist_pitch
        groups = self.General.groups

        mu0_eff = 4 * np.pi / 10 ** 7  #* (1 - fsc)

        # Resistivity calculations
        B = self.General.I_magnet*fMag
        rho_el_0 = self.rhoCu_nist(T=T, RRR=RRR*f_ro_eff, B=B[0, :]) + 1e-12
        rho_el_Outer = self.rhoCu_nist(T=T, RRR=RRR, B=B[0, :]) + 1e-12

        # Calculating the coupled loop equivalent parameter
        beta_if = (Lp_f / (2 * np.pi)) ** 2 * 1 / (rho_el_0)
        tau_if = mu0_eff / 2 * beta_if

        tb_strand = dws - ds_filamentary
        tau_ed = mu0 / 8 * (dws / 2) ** 2  / rho_el_Outer
        # tau_ed = mu0 / 2 * (ds_filamentary / 2 * tb_strand / 2) / rho_el_Outer
        if flag_coupling:
            tau = tau_if+tau_ed
            beta_if = 2 * tau / mu0_eff
        else:
            tau = tau_if
        alpha = 1 / np.sqrt((1 + (w * (tau)) ** 2))
        dB = w * fMag * alpha

        # Standard method
        I_if = beta_if * ds_filamentary * dB
        P_if = beta_if * (ds_filamentary/2) **2 * np.pi * l_mag *  dB**2
        # Power formula proposed in Arjans thesis - not working in XYCE
        # I_if = np.sqrt(np.pi / (2*w)) * beta_if * dS * dB
        # P_if = 2*dS**2*l_mag*np.pi/4*(2*tau_if*np.pi*w)/mu0*(f_mag*alpha)**2

        I_tot_im = I_if * alpha
        I_tot_re = I_if * alpha * w * tau
        # I_tot_re = np.sqrt(I_if ** 2 - I_tot_im ** 2)
        I_if = I_tot_re + 1j * I_tot_im

        R_if = P_if / np.real((I_if * np.conjugate(I_if)))
        L_if = np.ones((len(frequency), 1)) * tau * R_if[0, :]
        M_if = (1j * w.reshape(len(frequency), 1) * L_if * I_if + I_if * R_if) / (1j * w.reshape(len(frequency), 1) * 1)

        R_if = np.squeeze(R_if)
        L_if = np.squeeze(L_if)
        M_if = np.squeeze(M_if)
        I_if = np.squeeze(I_if)

        L, R, M, I = self.group_components(frequency, L_if, R_if, M_if,  sort_on='R', groups=groups, I=I_if)

        if flag_save:
            self.setAttribute(self.IFCC, 'M',  np.sqrt(2)*M)
            self.setAttribute(self.IFCC, 'R', R)
            self.setAttribute(self.IFCC, 'L', L)
            self.setAttribute(self.IFCC, 'I', I)
            self.setAttribute(self.IFCC, 'P', P_if)
            self.setAttribute(self.IFCC, 'tau', tau_if)
        else:
            return  np.sqrt(2)*M


    def calculate_ISCC(self, frequency: np.ndarray, T: float, fMag_X: np.ndarray, fMag_Y: np.ndarray, flag_save: bool = False) -> np.ndarray:
        '''
        Function that calculates the power loss and induced currents by ISCL and derives the equivalent circuit parameter

        :param frequency: Frequency vector
        :param T: temperature vector
        :param fMag_X: field-factor along X axis for each strand
        :param fMag_Y: field-factor along Y axis for each strand
        :param flag_save: if True saves the circuit parameter in the ISCC dataclass

        :return f_mag_X_return: return field-factor along X axis for each strand
        :return fMag_Y: return field-factor along Y axis for each strand
        '''
        f = frequency
        w = 2 * np.pi * f.reshape(len(f), 1)  #

        l_mag = self.General.magnet_length
        mu0 = 4 * np.pi / 10 ** 7

        dws = self.HalfTurns.diameter
        rotation_block = self.HalfTurns.rotation_ht
        mirror_block = self.HalfTurns.mirror_ht
        alphasRAD = self.HalfTurns.alphaDEG_ht * np.pi / 180
        groups = self.General.groups
        fsc = self.HalfTurns.fsc
        n_strands = self.HalfTurns.n_strands
        n_HT = self.General.num_HalfTurns
        Lp_s = self.HalfTurns.strand_twist_pitch
        wBare = self.HalfTurns.bare_cable_width
        hBare = self.HalfTurns.bare_cable_height_mean
        Nc = self.HalfTurns.Nc
        C = self.HalfTurns.C_strand
        R_c = self.HalfTurns.Rc
        RRR = self.HalfTurns.RRR
        f_ro_eff = self.HalfTurns.f_rho_effective

        inverse_field = int(n_HT / 4) * [1] + int(n_HT / 4) * [-1] + int(n_HT / 4) * [1] + int(n_HT / 4) * [-1]
        inverse_field = np.repeat(inverse_field, n_strands)
        alphas_ht = np.zeros(np.sum(n_strands),)
        tempS = 0

        for h in range(len(alphasRAD)):
            if mirror_block[h] == 0:
                alphas_ht[tempS:tempS + n_strands[h]] = alphasRAD[h] - rotation_block[h] / 180 * np.pi
            elif mirror_block[h] == 1:
                alphas_ht[tempS:tempS + n_strands[h]] = np.pi / 2 - alphasRAD[h] - rotation_block[h] / 180 * np.pi
            tempS = tempS + n_strands[h]

        f_magPerp = (-fMag_X * np.sin(alphas_ht) + fMag_Y * np.cos(alphas_ht))
        f_magPerp = np.transpose(inverse_field * f_magPerp)

        r_magPerp = np.transpose(fMag_X * np.cos(alphas_ht) + fMag_Y * np.sin(alphas_ht))
        B_temp = np.sqrt(fMag_X ** 2 + fMag_Y ** 2).T

        ## Reverse action:
        ## fMag_X = r_magPerp.T*np.cos(alphas)-f_magPerp.T*np.sin(alphas)
        ## fMag_Y = r_magPerp.T*np.sin(alphas)+f_magPerp.T*np.cos(alphas)

        f_magPerp_ht = np.zeros((n_HT, len(frequency)))
        r_magPerp_ht = np.zeros((n_HT, len(frequency)))
        B_ht = np.zeros((n_HT, len(frequency)))
        tempS = 0
        for i in range(len(n_strands)):
            f_magPerp_ht[i] = np.average(f_magPerp[tempS:tempS + n_strands[i], :], axis=0)
            r_magPerp_ht[i] = np.average(r_magPerp[tempS:tempS + n_strands[i], :], axis=0)
            B_ht[i] = np.average(B_temp[tempS:tempS + n_strands[i], :], axis=0)
            tempS = tempS + n_strands[i]

        # alpha_c = wBare / hBare
        # rho_C_Strands = R_c / (rho_el_Outer * (n_strands ** 2 - n_strands) / (2 * Lp_s * alpha_c)) #Eq. 4.33 in Arjans Thesis p. 78

        #  Calculating the equivalent circuit parameter
        beta_is = 1 / 120 * Lp_s / R_c * n_strands * (n_strands - 1) * wBare / hBare
        tau_is = mu0 * beta_is
        # factor_tau = alpha_c * Nc / (alpha_c + C * (Nc - 1))  # Eq. 4.41 in Arjans Thesis p.89
        # tau_is = 1.65e-08 * (Lp_s * (n_strands ** 2 - 4 * n_strands)) / R_c * factor_tau  # Eq. 4.31 in Arjans Thesis p.78

        alpha = 1 / np.sqrt((1 + (w * tau_is) ** 2))
        dB = w * f_magPerp_ht.T * alpha

        P_is = l_mag * beta_is * dB ** 2 * wBare * hBare
        I_is = beta_is * hBare * dB

        I_tot_im = I_is * alpha
        I_tot_re = I_is * alpha * w * tau_is
        #I_tot_re = np.sqrt(I_is ** 2 - I_tot_im ** 2)
        I_is = I_tot_re + 1j * I_tot_im

        # Calculate equivalent parameter
        R_is = P_is / np.real((I_is*np.conjugate(I_is)))
        L_is = np.ones((len(f),1))* tau_is * R_is
        M_is = (1j * w.reshape(len(f), 1) * L_is * I_is + I_is * R_is) / (1j * w.reshape(len(f), 1) * 1)
        # M_is = np.sqrt(np.real(M_is) ** 2 + np.imag(M_is) ** 2)

        # Calculate warm resistance of a strand-pitch
        if not self.Options.flag_SC:
            ## Add the warm part to account for ISCL in non-superconducting state
            rho_el_Outer = self.rhoCu_nist(T, B_ht[:, 0], RRR*f_ro_eff) + 1e-12
            alpha_st = np.arctan(wBare/(Lp_s/2)) #Half twist-pitch as Lp is the full length until its back at the beginning
            l_strand = 2 * wBare / np.sin(alpha_st) + 2 * hBare  # twice as we go back AND forth
            A_strand = (1 - fsc) * np.pi * (dws / 2) ** 2
            R_strand = rho_el_Outer * l_strand / A_strand

            R_c_warm = 2e-3 * rho_C_Strands * rho_el_Outer * (n_strands** 2 - n_strands) / (2 * Lp_s * alpha_c)
            R_c_N = R_c_warm + R_strand
            # fT = 1/(1.9)**0.08*T**(0.08)
            # fT = 2*1/(np.log(1.9)**0.186)*np.log(T)**0.186
            fT = 1 / (np.log(1.9) ** 0.186) * np.log(T) ** 0.186
            # fT = 1 / (np.log(1.9) ** 0.3179) * np.log(T) ** 0.3179
            R_c_warm = R_c * fT
            R_c_N = fT * (R_c_warm + R_strand)

            tau_is_N = np.zeros(Nc.shape)
            for i in range(len(tau_is_N)):
                if Nc[i] >= 8:
                    tau_is_N[i] = 1.65e-8 * C[i] * (Lp_s[i] * (n_strands[i] ** 2 - 4 * n_strands[i])) / R_c_N[i] * factor_tau[
                        i]  # Eq. 4.31 in Arjans Thesis p.78
                else:
                    tau_is_N[i] = mu0 * beta_is[i]
            # tau_is_N = 1.65e-8*C*2/(fT) * (Lp_s*(nS**2-4*nS))/R_c_N *factor_tau # Equation 4.31 in Arjans Thesis P.78 and Eq. 4.41
            # beta_is_N = tau_is_N/ mu0
            beta_is_N = 1 / 120 * Lp_s / R_c_N * n_strands * (n_strands - 1) * wBare / hBare  # 60 works well for 290 K

            ## Adjust the components again on the new time constant
            alpha = 1 / np.sqrt((1 + (w * tau_is_N) ** 2))
            dB = w * f_magPerp_ht.T * alpha

            P_is = l_mag * beta_is_N * dB ** 2 * wBare * hBare
            I_is = beta_is_N * hBare * dB
            # I_is = 1 / 12 * Lp_s / R_c * wBare * dB * (nS ** 2 - 1) / nS
            I_tot_im = I_is * alpha
            # I_tot_re = np.sqrt(I_is ** 2 - I_tot_im ** 2)
            I_tot_re = I_is * alpha * w * tau_is_N
            I_is = I_tot_re + 1j * I_tot_im

            # Calculate equivalent parameter
            R_is = P_is / np.real((I_is * np.conjugate(I_is)))
            L_is = np.ones((len(f), 1)) * tau_is_N * R_is[0, :]
            M_is = (1j * w.reshape(len(f), 1) * L_is * I_is + I_is * R_is) / (1j * w.reshape(len(f), 1) * 1)
            # M_is = np.sqrt(np.real(M_is) ** 2 + np.imag(M_is) ** 2)

        # ## Calculate the return field
        # Assuming a current line on each side of the cable
        # Average distance to each strand is hence: (1/2*(dws/2 + (nS/2-1)*dws)), neglecting hBare
        # Twice, as we have one line on each side -> both generating the same field
        # B_return = (2 * (mu0 * np.abs(I_is)) / np.pi * 1 / (1 / 2 * (dws / 2 + (n_strands / 2 - 1) * dws)))
        # dB_return = (B_return/tau_is)

        # f_mag_X_return_ht = r_magPerp_ht*np.cos(alphas_ht)-B_return.T*np.sin(alphas_ht)
        # f_mag_Y_return_ht = r_magPerp_ht*np.sin(alphas_ht)+B_return.T*np.cos(alphas_ht)
        # ratio_Breturn = B_return / B_ht.T

        f_mag_X_return = np.zeros((len(f), fMag_X.shape[1]))
        f_mag_Y_return = np.zeros((len(f), fMag_Y.shape[1]))

        temp_c = 0
        for i in range(len(n_strands)):
            for j in range(int(n_strands[i] / 2)):
                ratio_Breturn1 = ((mu0 * np.abs(I_is[:, i])) / (4 * np.pi) * 1 / ((dws[i] / 2 + j * dws[i])))
                ratio_Breturn2 = ((mu0 * np.abs(I_is[:, i])) / (4 * np.pi) * 1 / ((dws[i] / 2 + (int(n_strands[i] / 2) - j) * dws[i])))
                ratio_Breturn = ratio_Breturn1 + ratio_Breturn2
                f_mag_X_return[:, temp_c] = ratio_Breturn / B_temp[temp_c, :] * fMag_X[:, temp_c]
                f_mag_Y_return[:, temp_c] = ratio_Breturn / B_temp[temp_c, :] * fMag_Y[:, temp_c]
                f_mag_X_return[:, temp_c + 1] = ratio_Breturn / B_temp[temp_c + 1, :] * fMag_X[:, temp_c + 1]
                f_mag_Y_return[:, temp_c + 1] = ratio_Breturn / B_temp[temp_c + 1, :] * fMag_Y[:, temp_c + 1]
                temp_c = temp_c + 2

        R_is = np.squeeze(R_is)
        L_is = np.squeeze(L_is)
        M_is = np.squeeze(M_is)
        I_is = np.squeeze(I_is)
        P_is = np.squeeze(P_is)

        L, R, M, I = self.group_components(f, L_is, R_is, M_is, sort_on='L', groups=groups, I=I_is)

        if flag_save:
            self.setAttribute(self.ISCC, 'M',  np.sqrt(2)*M)
            self.setAttribute(self.ISCC, 'R', R)
            self.setAttribute(self.ISCC, 'L', L)
            self.setAttribute(self.ISCC, 'P', P_is)
            self.setAttribute(self.ISCC, 'I', I)
            if not self.Options.flag_SC:
                self.setAttribute(self.ISCC, 'tau', tau_is_N)
            else:
                self.setAttribute(self.ISCC, 'tau', tau_is)
        else:
            return  np.sqrt(2)*M, f_mag_X_return, f_mag_Y_return


    def calculate_ED(self, frequency: np.ndarray, T: float, fMag: np.ndarray, flag_coupling: bool = True, flag_save: bool = False) -> np.ndarray:
        '''
        Calculates the equivalent coupling loops in the outer copper sheet for a given temperature and field

        :param frequency: Frequency vector
        :param T: temperature vector
        :param fMag: field-factor for each strand
        :param flag_coupling: if True it means it has to be coupled to another effect
        :param flag_save: if True saves the circuit parameter in the ED dataclass
        '''

        f = frequency
        w = 2 * np.pi * f.reshape(len(f), 1)

        groups = self.General.groups
        l_mag = self.General.magnet_length
        RRR = self.Strands.RRR
        rws = self.Strands.diameter / 2

        if not self.Options.flag_SC:  # TODO - check if needed or not
            r_filamentary = self.Strands.d_filamentary / 2 * 0.5
        else:
            r_filamentary = self.Strands.d_filamentary / 2


        B = self.General.I_magnet * fMag
        rho_el_0 = self.rhoCu_nist(T=T, B=B[0, :], RRR=RRR) + 1e-12
        mu0 = 4 * np.pi / 10 ** 7  # mu0 = 4 * np.pi / 10 ** 7 / (1 - fsc)  #
        tb_strand = rws - r_filamentary
        rho_el_0 = rho_el_0 + 1e-12

        # Calculating time constant, correction factor and field derivative
        tau_ed = mu0 / 2 * ((rws) * tb_strand) / rho_el_0
        # tau_ed = mu0 / 8 * dws**2 / rho_el_0 ## Formula from Turck79
        alpha = 1 / np.sqrt((1 + (w * tau_ed) ** 2))
        dB = w * fMag

        # Skindepth
        skinDepth = np.sqrt(2 * rho_el_0 / (w * mu0))
        idx_s = np.argmin(abs(skinDepth - (1 - 1 / np.exp(1)) * tb_strand), axis=0) + 1

        # Calculating the power loss
        P_DC = 1/2 * l_mag * np.pi/(4*rho_el_0) * rws **4 *(dB * alpha) ** 2
        # P_DC = tau_ed/mu0/2 * (1-(dS_inner/dws)**2) * (dB*alpha)**2 # Formula from Turck
        # P_DC = v3 * v1v2/(v1v2+1)*beta_if*(dB*alpha)**2 # Formula from Arjan's thesis

        P_AC = 1/2 * l_mag * np.pi / rho_el_0 * rws * skinDepth ** 3 * (dB) ** 2
        # P_AC = dB ** 2 * skinDepth/(w*4*mu0*dws) #Formula from Turck1979

        # Calculating the induced current
        I_DC = rws ** 3 / (3 * rho_el_0) * (dB * alpha)
        # I_DC = 2 * tb_strand / (3 * rho_el_0) * (tb_strand ** 2 - 3 * tb_strand * dS_outer + 3 * dS_outer ** 2) * (dB * alpha)
        # I_DC = 2 * tau_ed / mu0 * dS_outer * (dB*alpha)
        I_DC_im = I_DC * alpha
        I_DC_re = I_DC * alpha * w * tau_ed
        # I_tot_re = np.sqrt(I_tot ** 2 - I_tot_im ** 2)
        I_DC = I_DC_re + 1j * I_DC_im

        I_tot = I_DC
        # I_tot = np.zeros((I_DC.shape), dtype=np.complex_)
        # for j in range(I_tot.shape[1]):
        #     fac = np.sqrt(w[idx_s[j]:]) / np.sqrt(w[idx_s[j]])
        #     I_t = [I_DC[:idx_s[j], j], I_DC[idx_s[j]:, j] * fac[:, 0]]
        #     I_tot[:, j] = np.concatenate(I_t).ravel()

        P_tot = np.zeros((P_DC.shape))
        for j in range(P_DC.shape[1]):
            P_t = [P_DC[:idx_s[j], j], P_AC[idx_s[j]:, j]]
            P_tot[:, j] = np.concatenate(P_t).ravel()
        P_tot = P_tot

        P_tot = np.squeeze(P_tot)
        I_ed = np.squeeze(I_tot)
        tau_ed = tau_ed

        # Calculating the coupled loop equivalent parameter
        R_ed = P_tot / np.real(I_ed * np.conjugate(I_ed))
        L_ed = np.ones((len(f), 1)) * tau_ed * R_ed[0, :]
        M_ed = (1j * w * L_ed * I_ed + I_ed * R_ed) / (1j * w * 1)
        # M_ed = np.real(M_ed) ** 2 + np.imag(M_ed) ** 2

        if not flag_coupling:
            L, R, M, Ied = self.group_components(f, L_ed, R_ed, M_ed, groups=groups, I=I_ed)
        else:
            L, R, M = self.group_components(f, L_ed, R_ed, M_ed, groups=groups)

        if flag_save:
            self.setAttribute(self.ED, 'M',  np.sqrt(2)*M)
            self.setAttribute(self.ED, 'R', R)
            self.setAttribute(self.ED, 'L', L)
            self.setAttribute(self.ED, 'P', P_tot)
            self.setAttribute(self.ED, 'I', Ied)
            self.setAttribute(self.ED, 'tau', tau_ed)
        else:
            return  np.sqrt(2)*M


    def calculate_Wedge(self, T: float):
        '''
        Function that calculates the equivalent parameter for eddy currents in the copper Wedge
        It takes the Temperature. It then calculates the resistivity and
        interpolates the current and power from a pre-simulated Comsol model that includes the wedges effect.
        '''
        rho_W = self.rhoCu_nist(T=T, RRR=self.Wedge.RRR_wedges, B=np.array([0]))
        P_tot, I_tot, tau_W, frequency = self.interpolate(rho=rho_W, case='Wedge')

        w = 2 * np.pi * frequency
        P_tot = P_tot * self.General.magnet_length * 2

        # Calculating the coupled loop equivalent parameter
        # R_W = P_tot / I_tot ** 2
        R_W = P_tot / np.real((I_tot * np.conjugate(I_tot)))
        L_W = tau_W * R_W[0]
        L_W = np.repeat(L_W, len(R_W))
        M_W = (1j * w * L_W * I_tot + I_tot * R_W) / (1j * w * 1)
        # M_W = np.sqrt(np.real(M_W*np.conjugate(M_W))) # Checked: is the same as the line below
        # M_W = np.sqrt(np.real(M_W) ** 2 + np.imag(M_W) ** 2)
        # M_W1 = M_W[:tau_index]
        # M_W2 = np.transpose(np.ones(len(M_W)-tau_index).transpose() * M_W[tau_index])
        # M_W = np.concatenate((M_W1, M_W2))
        M_W = np.transpose(np.ones(M_W.shape).transpose() * M_W[0])

        self.setAttribute(self.Wedge, 'P', P_tot)
        self.setAttribute(self.Wedge, 'I', I_tot)
        self.setAttribute(self.Wedge, 'tau', tau_W)
        self.setAttribute(self.Wedge, 'L', L_W)
        self.setAttribute(self.Wedge, 'R', R_W)
        self.setAttribute(self.Wedge, 'M', M_W)

    def calculate_CB(self, T: float):
        '''
        Function that calculates the equivalent parameter for eddy currents in the cold bore.
        It takes the Temperature. It then calculates the resistivity and
        interpolates the current and power from Comsol model that includes the ColdBore effect.
        '''

        rho_CB = self.rhoSS_nist(T=T)
        P_tot, I_tot, tau_CB, frequency = self.interpolate(rho=rho_CB, case='CB')
        w = 2 * np.pi * frequency
        P_tot = P_tot * self.General.magnet_length * 2

        # Calculating the coupled loop equivalent parameter
        # R_W = P_tot / I_tot ** 2
        R_CB = P_tot / np.real((I_tot * np.conjugate(I_tot)))
        L_CB = tau_CB * R_CB[0]
        L_CB = np.repeat(L_CB, len(R_CB))
        M_CB = (1j * w * L_CB * I_tot + I_tot * R_CB) / (1j * w * 1)
        # M_W = np.sqrt(np.real(M_W*np.conjugate(M_W))) # Checked: is the same as the line below
        # M_W = np.sqrt(np.real(M_W) ** 2 + np.imag(M_W) ** 2)
        M_CB = np.transpose(np.ones(M_CB.shape).transpose() * M_CB[0])

        self.setAttribute(self.CB, 'P', P_tot)
        self.setAttribute(self.CB, 'I', I_tot)
        self.setAttribute(self.CB, 'tau', tau_CB)
        self.setAttribute(self.CB, 'L', L_CB)
        self.setAttribute(self.CB, 'R', R_CB)
        self.setAttribute(self.CB, 'M', M_CB)

    def calculate_CPS(self, T: float):
        '''
        Function that calculates the equivalent parameter for eddy currents in the coil protection sheets.
        It takes the Temperature. It then calculates the resistivity and
        interpolates the current and power from Comsol model that includes the ColdBore effect.
        '''

        name = self.General.magnet_name
        path = Path(self.General.local_library_path).resolve()
        # Takes the PowerLoss excel file corresponding to that effect
        df_P = pd.read_csv(os.path.join(path, 'TFM_input', f'{name}_PowerLoss_CPS_Interpolation.csv')).dropna(axis=1)
        # Takes the InducedCurrent excel file corresponding to that effect
        df_I = pd.read_csv(os.path.join(path, 'TFM_input', f'{name}_InducedCurrent_CPS_Interpolation.csv')).dropna(axis=1)
        frequency = df_P['f'].values[:]
        P_tot = df_P['1'].values[:]
        I_real = df_I['Re_Jz_1'].values[:]
        I_imag = df_I['Im_Jz_1'].values[:]
        I_tot = I_real + 1j * I_imag
        tau_CPS = calculate_tau(P_tot=P_tot, frequency=frequency)
        # tau_CPS = 0.0001465

        w = 2 * np.pi * frequency
        P_tot = P_tot * self.General.magnet_length * 2

        # Calculating the coupled loop equivalent parameter
        # R_W = P_tot / I_tot ** 2
        R_CPS = P_tot / np.real((I_tot * np.conjugate(I_tot)))
        L_CPS = tau_CPS * R_CPS[0]
        L_CPS = np.repeat(L_CPS, len(R_CPS))
        M_CPS = (1j * w * L_CPS * I_tot + I_tot * R_CPS) / (1j * w * 1)
        # M_W = np.sqrt(np.real(M_W*np.conjugate(M_W))) # Checked: is the same as the line below
        # M_W = np.sqrt(np.real(M_W) ** 2 + np.imag(M_W) ** 2)
        M_CPS = np.transpose(np.ones(M_CPS.shape).transpose() * M_CPS[0])

        self.setAttribute(self.CPS, 'P', P_tot)
        self.setAttribute(self.CPS, 'I', I_tot)
        self.setAttribute(self.CPS, 'tau', tau_CPS)
        self.setAttribute(self.CPS, 'L', L_CPS)
        self.setAttribute(self.CPS, 'R', R_CPS)
        self.setAttribute(self.CPS, 'M', M_CPS)


    def interpolate(self, rho: np.ndarray, case: str) -> np.ndarray:
        '''
        Helper function that takes a temperature, fits the respective resistivity to it and interpolates from other resistivity values.

        :param case: name of the effect to select the excel file from (Wedge or CB)
        :param rho: resistivity of the Effect
        '''

        name = self.General.magnet_name
        path = Path(self.General.local_library_path).resolve()
        # Takes the PowerLoss excel file corresponding to that effect
        df_P = pd.read_csv(os.path.join(path, 'TFM_input', f'{name}_PowerLoss_{case}_Interpolation.csv')).dropna(axis=1)
        # Takes the InducedCurrent excel file corresponding to that effect
        df_I = pd.read_csv(os.path.join(path, 'TFM_input', f'{name}_InducedCurrent_{case}_Interpolation.csv')).dropna(axis=1)
        frequency = df_P['f'].values[1:]
        # Takes all the possible resistivity values included in these files
        resistivities = np.array(df_P.iloc[0, 1:]).astype(float)
        order = np.argsort(resistivities)
        resistivities = resistivities[order]

        P_temp = np.zeros((len(frequency),))
        I_temp_real = np.zeros((len(frequency),))
        I_temp_imag = np.zeros((len(frequency),))

        # Performs interpolation between the desired resistivity value (rho[0]) and the resistivity values extracted from the file.
        # This is done to obtain accurate values of power loss and induced current corresponding to the desired resistivity.
        for i in range(len(frequency)):
            P_res = df_P.loc[df_P['f'] == frequency[i]].reset_index(drop=True).values[0][1:]
            P_res = P_res[order]
            P_temp[i] = np.interp(rho[0], resistivities, P_res)
            I_res = df_I.loc[df_I['f'] == frequency[i]].reset_index(drop=True).values[0][1::2]
            I_res = I_res[order]
            I_temp_real[i] = np.interp(rho[0], resistivities, I_res)
            I_res = df_I.loc[df_I['f'] == frequency[i]].reset_index(drop=True).values[0][2::2]
            I_res = I_res[order]
            I_temp_imag[i] = np.interp(rho[0], resistivities, I_res)
        I_tot = I_temp_real + 1j * I_temp_imag
        #I_tot = np.real(np.sqrt(I_tot * np.conjugate(I_tot)))

        P_tot = P_temp
        # In order to calculate the tau, it calls the helper function
        # tau_index = calculate_tau_index(P_tot=P_tot, frequency=frequency)
        tau =  calculate_tau(P_tot=P_tot, frequency=frequency)

        return P_tot, I_tot, tau, frequency


    ####################################################################################################################
    ############################################### MAIN FUNCTION TFM ###############################################

    def change_coupling_parameter(self, output_path: str):
        '''
        Main function of TFM_model
        Changes the equivalent coupling loop parameters for the MB magnet using all the other functions.

        :param output_path: path to save the generated lib file
        '''

        frequency = self.frequency
        groups = self.General.groups
        T = self.temperature
        f_rho_original = self.Strands.f_rho_effective
        f_mag_Roxie= self.Strands.f_mag_Roxie
        Mutual_dict = {}

        # Inter-Strands Coupling Currents
        if self.Options.flag_ISCC:
            f_mag_X_ISCC = self.Strands.f_mag_X_Roxie
            f_mag_Y_ISCC = self.Strands.f_mag_Y_Roxie
            M_ISCC, f_mag_X_ISCC_return, f_mag_Y_ISCC_return = self.calculate_ISCC(frequency=frequency, T=T, fMag_X=f_mag_X_ISCC, fMag_Y=f_mag_Y_ISCC, flag_save=False)
            self.calculate_ISCC(frequency=frequency, T=T, fMag_X=f_mag_X_ISCC, fMag_Y=f_mag_Y_ISCC, flag_save=True)
            self.General.lib_path = change_library_EqLoop(self.General.lib_path, 'ISCC', frequency, self.ISCC.L, self.ISCC.R, self.ISCC.M, groups=groups,
                                             force_new_name=self.General.lib_path)

        # Persistent currents and magnetization
        if self.Options.flag_PC:
            self.setAttribute(self.Strands, 'f_rho_effective', f_rho_original)
            self.calculate_PC(frequency=frequency, T=T, fMag=f_mag_Roxie, flag_coupling=False, flag_save=True)
            if self.Options.flag_ISCC: # calculates coupling between PC and ISCC
                f_mag_PC = np.maximum(f_mag_Roxie - np.sqrt(f_mag_X_ISCC_return ** 2 + f_mag_Y_ISCC_return ** 2), 1e-12)
                M_PC_ISCC = self.calculate_PC(frequency=frequency, T=T, fMag=f_mag_PC, flag_coupling=False, flag_save=False)
                Mutual_dict['M_PC_ISCC'] = M_PC_ISCC
            if self.Options.flag_ED: # calculates coupling between PC and ED
                M_PC_ED = np.ones(self.PC.M.shape) * self.PC.M_PC_IFCC
                for i in range(groups):
                    self.General.lib_path = change_library_MutualCoupling(self.General.lib_path, f'M_PC_ED_{i + 1}', frequency, M_PC_ED[:, i])
            self.General.lib_path = change_library_EqLoop(self.General.lib_path, 'PC', frequency, self.PC.L, np.array([]), self.PC.M, groups=groups,
                                             force_new_name=self.General.lib_path)

        # Inter-Filament Coupling Currents
        if self.Options.flag_IFCC:
            self.setAttribute(self.Strands, 'f_rho_effective', f_rho_original)#Change rho_eff to 0.6
            if self.Options.flag_ISCC: # calculates coupling between IFCC and ISCC
                f_mag_IFCC = np.maximum(f_mag_Roxie - np.sqrt(f_mag_X_ISCC_return ** 2 + f_mag_Y_ISCC_return ** 2), 1e-12)
                M_IFCC_ISCC = self.calculate_IFCC(frequency=frequency, T=T, fMag=f_mag_IFCC, flag_coupling=False, flag_save=False)
                Mutual_dict['M_IFCC_ISCC'] = M_IFCC_ISCC
            if self.Options.flag_ED: # calculates coupling between IFCC and ED
                M_IFCC_ED = self.calculate_IFCC(frequency=frequency, T=T, fMag=f_mag_Roxie, flag_coupling=True, flag_save=False)
                Mutual_dict['M_IFCC_ED'] = M_IFCC_ED
            self.calculate_IFCC(frequency=frequency, T=T, fMag=f_mag_Roxie, flag_coupling=False, flag_save=True)
            self.General.lib_path = change_library_EqLoop(self.General.lib_path, 'IFCC', frequency, self.IFCC.L, self.IFCC.R, self.IFCC.M, groups=groups,
                                             force_new_name=self.General.lib_path)

        # Eddy currents in the copper sheath
        if self.Options.flag_ED:
            self.setAttribute(self.Strands, 'f_rho_effective', f_rho_original)
            if self.Options.flag_ISCC: # calculates coupling between ED and ISCC
                f_mag_ED = np.maximum(f_mag_Roxie - np.sqrt(f_mag_X_ISCC_return ** 2 + f_mag_Y_ISCC_return ** 2), 1e-12)
                M_ED_ISCC = self.calculate_ED(frequency=frequency, T=T, fMag=f_mag_ED, flag_coupling=True, flag_save=False)
                Mutual_dict['M_ED_ISCC'] = M_ED_ISCC

            self.calculate_ED(frequency=frequency, T=T, fMag=f_mag_Roxie, flag_coupling=False, flag_save=True)
            self.General.lib_path = change_library_EqLoop(self.General.lib_path, 'ED', frequency, self.ED.L, self.ED.R, self.ED.M, groups=groups,
                                             force_new_name=self.General.lib_path)
        # Eddy currents in the Wedge
        if self.Options.flag_Wedge:
            self.calculate_Wedge(T=T)
            self.General.lib_path = change_library_EqLoop(self.General.lib_path, 'Wedge', frequency, self.Wedge.L, self.Wedge.R, self.Wedge.M, groups=1,
                                                          force_new_name=self.General.lib_path)
            # Calculates coupling between Wedge and the conductor Losses effects
            M_W = self.calculate_Coupling_Components(Effect='Wedge')
            Mutual_dict.update(M_W)

        # Eddy currents in the Cold Bore
        if self.Options.flag_CB:
            self.calculate_CB(T=T)
            self.General.lib_path = change_library_EqLoop(self.General.lib_path, 'CB', frequency, self.CB.L, self.CB.R, self.CB.M, groups=1,
                                                          force_new_name=self.General.lib_path)
            # Calculates coupling between CB and the conductor Losses effects
            # M_CB = self.calculate_Coupling_Components(Effect='CB')
            # Mutual_dict.update(M_CB)

        # Eddy currents in the Coil Protection Sheets
        if self.Options.flag_CPS:
            self.calculate_CPS(T=T)
            self.General.lib_path = change_library_EqLoop(self.General.lib_path, 'CPS', frequency, self.CPS.L,
                                                          self.CPS.R, self.CPS.M, groups=1,
                                                          force_new_name=self.General.lib_path)
            # Calculates coupling between CB and the conductor Losses effects
            # M_CPS = self.calculate_Coupling_Components(Effect='CPS')
            # Mutual_dict.update(M_CPS)


        if len(Mutual_dict) != 0:
            # Calculates mutual coupling coefficients using the Mutual_dict values
            self.calculate_Mutual_Coupling(Mutual_dict)

        if self.Options.flag_PC and self.Options.flag_IFCC: # Changes values of M_PC_IFCC in the .lib file
            M_PC_IFCC = np.repeat(self.PC.M_PC_IFCC, np.sum(self.HalfTurns.n_strands))
            self.General.lib_path = change_library_MutualCoupling(self.General.lib_path, 'M_PC_IFCC', frequency, M_PC_IFCC)

        if self.magnet_data.M_CB_wedge != None: # If M_CB_wedge not None changes the value of M_CB_wedge in the .lib file
            M_CB_wedge = self.self.magnet_data.M_CB_wedge
            if isinstance(M_CB_wedge, np.ndarray):
                M_CB_wedge = np.repeat(M_CB_wedge, len(frequency))
            else:
                M_CB_wedge = np.array([M_CB_wedge] * len(frequency))
            self.General.lib_path = change_library_MutualCoupling(self.General.lib_path, 'M_CB_wedge', frequency, M_CB_wedge)

        if self.flag_debug:
            for eff, value in self.Effects.items():
                if value:
                    attributes = ['M', 'I', 'L', 'R', 'K']
                    y_labels = ['M [H]', 'I [A]', 'L [H]', 'R [ohm]', 'K']
                    fig_path = os.path.abspath(os.path.join(self.output_path, '..'))
                    fig_path = os.path.join(fig_path, 'Effects_params')
                    os.makedirs(fig_path, exist_ok=True)

                    for attr, y_label in zip(attributes, y_labels):
                        if attr == 'R' and eff == 'PC': continue
                        if attr != 'K':
                            data = self.getAttribute(eff, attr)
                        else:
                            M = self.getAttribute(eff, 'M')
                            L = self.getAttribute(eff, 'L')
                            data = M / np.sqrt(L * self.General.L_mag / 2)
                        list_legend = []
                        fig, ax = plt.subplots()
                        if eff != 'Wedge' and eff != 'CB':
                            for i in range(self.General.groups):
                                if attr == 'M':
                                    ax.semilogx(frequency, np.real(data[:, i]), marker='*')
                                    list_legend.append(f'Group {i + 1}, Re(M)')
                                    ax.semilogx(frequency, np.imag(data[:, i]), marker='*')
                                    list_legend.append(f'Group {i + 1}, Im(M)')
                                else:
                                    ax.semilogx(frequency, data[:, i], marker='*')
                                    list_legend.append(f'Group {i+1}')
                        else:
                            if attr == 'M':
                                ax.semilogx(frequency, np.real(data[:]), marker='*')
                                list_legend.append(f'Re(M)')
                                ax.semilogx(frequency, np.imag(data[:]), marker='*')
                                list_legend.append(f'Im(M)')
                            else:
                                ax.semilogx(frequency, data[:], marker='*')
                                list_legend.append(f'No grouping')
                        ax.legend(list_legend, loc='upper left')
                        plt.xlabel('Frequency [Hz]')
                        plt.ylabel(y_label)
                        plt.title(f'{eff} plot of {y_label} for different groups - {self.General.magnet_name}', fontweight='bold')
                        fig_path_final = os.path.join(fig_path, f'{eff}_{attr}_plot.png')
                        plt.savefig(fig_path_final)
                        plt.close()

    ####################################################################################################################
    ############################################### MUTUAL COUPLING CALCULATION #########################################

    def calculate_Mutual_Coupling(self, Mutual_dict: dict):
        '''
        This function calculates the Mutual Coupling coefficients between two different effects and inserts this value
        in the corresponding .FUNC of the lib file

        : param Mutual_dict: dictionary containing all the Mutual Coupling values between the effects
        '''
        frequency = self.frequency
        groups = self.General.groups

        fig_path = os.path.abspath(os.path.join(self.output_path, '..'))
        fig_path = os.path.join(fig_path, 'Effects_params')
        os.makedirs(fig_path, exist_ok=True)

        key_valid = ['M_IFCC_ISCC', 'M_IFCC_ED', 'M_ED_ISCC', 'M_PC_ISCC', 'M_PC_ED']

        for key, value in Mutual_dict.items(): # example of key = M_IFCC_ISCC
            # if key not in key_valid : continue
            first_effect = key.split('_')[-2] # Taking the name of the first effect
            second_effect = key.split('_')[-1]  # Taking the name of the second effect
            M_first_effect = self.getAttribute(first_effect, 'M') # Taking the value of M not coupled corresponding to the first effect and saved in the dataclass
            I_second_effect = self.getAttribute(second_effect, 'I')  # Taking the value of I corresponding to the sceond effect and saved in the dataclass

            M_key = key

            if second_effect == 'Wedge' or second_effect == 'CB':
                M_value = -1 * np.transpose((value**2 - M_first_effect**2).T / (I_second_effect*M_first_effect.T))
            else:
                M_value = -1 * (value ** 2 - M_first_effect ** 2) / (I_second_effect * M_first_effect)

            for i in range(groups):
                self.General.lib_path = change_library_MutualCoupling(self.General.lib_path, f'{M_key}_{i + 1}', frequency, M_value[:, i])

            if self.flag_debug:
                list_legend = []
                cases = [M_key, f'K_{M_key}']
                for case in cases:
                    fig, ax = plt.subplots()
                    for group in range(groups):
                        if case == M_key:
                            ax.semilogx(frequency, np.real(M_value[:, group]), marker='*')
                            list_legend.append(f'Re({M_key}) group {group+1}')
                            ax.semilogx(frequency, np.imag(M_value[:, group]), marker='*')
                            list_legend.append(f'Im({M_key}) group {group+1}')
                        else:
                            L1 = self.getAttribute(first_effect, 'L')
                            L2 = self.getAttribute(second_effect, 'L')
                            value = M_value/ np.sqrt(L1 * L2)
                            ax.semilogx(frequency, np.imag(value[:, group]), marker='*')
                            list_legend.append(f'Group {group+1}')

                    ax.legend(list_legend, loc='upper left')
                    plt.xlabel('Frequency [Hz]')
                    plt.ylabel(f'{case}') if case != M_key else plt.ylabel(f'{case} [H]')
                    plt.title(f'{case} plot for different groups - {self.General.magnet_name}', fontweight='bold')
                    fig_path_final = os.path.join(fig_path, f'{case}_plot.png')
                    plt.savefig(fig_path_final)
                    plt.close()


    def calculate_Coupling_Components(self, Effect: str) -> dict:
        '''
        This function calculates the Mutual Coupling values between the conductor losses and the given Effect

        :param Effect: str that indicates the corresponding Not Conductor Loss effect -> Wedge or CB

        :return M_dict: dictionary with the name of the Mutual coupling and the values
        '''
        M_dict = {}

        # Retrieve f_mag, f_mag_X and f_mag_Y from the Comsol field files specific for each effect
        f_mag, f_mag_X, f_mag_Y = self.read_COMSOL_field_file(Effect)
        frequency = self.frequency
        T = self.temperature

        effs_Cond = dict(list(self.Effects.items())[3:]) # Taking only the effects corresponding to the conductor losses
        for eff, value in effs_Cond.items():
            if value == True:  # If the flag of an effect is set takes the name of the effect
                # Calls the calculate function of the corresponding effect and calculates the M
                if eff == 'ISCC':  # attributes -> fMag-X, fMag_Y
                    M, _, _ = getattr(self, f'calculate_{eff}')(frequency=frequency, T=T, fMag_X=f_mag_X, fMag_Y=f_mag_Y, flag_save=False)
                else: # attributes -> fMag
                    M = getattr(self, f'calculate_{eff}')(frequency=frequency, T=T, fMag=f_mag, flag_coupling=True, flag_save=False)

                M_dict[f'M_{eff}_{Effect}'] = M # Save the new M in the dictionary

        return M_dict

    ####################################################################################################################
    ############################################ FUNCTION TO CALCULATE THE GROUPING #####################################

    def group_components(self, frequency: np.ndarray, L: np.ndarray, R: np.ndarray, M: np.ndarray, groups: int,
                         sort_on: str = 'L', I: np.ndarray = np.array([]), flag_groups: bool = True) -> np.ndarray:
        '''
        Helper function that groups components into n groups, based on a sorting on a specific variable out of R,L,M

        :param frequency: frequency vector
        :param L: L-vector
        :param R: R-vector
        :param M: M_vector
        :param groups: number of groups to be separated
        :param sort_on: Which variable to sort on
        :return: 3 np.ndarray in the order: L,R,M that are groupned into n_groups
        '''
        if sort_on == 'L':
            if np.all(np.isclose(L, L[0, 0])):
                sort_on = 'R_group'
            else:
                sort_on = 'L_group'
        elif sort_on == 'R':
            sort_on = 'R_group'
        elif sort_on == 'M':
            sort_on = 'M_group'
        else:
            raise Exception(f'Do not understand sort_on: {sort_on} - Only R, L, M')

        f = frequency
        R_group = np.zeros((len(f), groups), dtype=float)
        M_group = np.zeros((len(f), groups), dtype=np.complex_)
        # s_r = np.zeros((len(f), groups))
        # s_i = np.zeros((len(f), groups))
        L_group = np.zeros((len(f), groups), dtype=float)
        I_group = np.zeros((len(f), groups), dtype=np.complex_)
        for j in range(len(f)):
            # group the resistivities and take the mean of their M
            df = pd.DataFrame.from_dict({'R_group': np.nan_to_num(R[j, :])}).astype(float)
            df['M_group'] = np.nan_to_num(M[j, :]).astype(complex)
            df['L_group'] = np.nan_to_num(L[j, :]).astype(float)
            if len(I) != 0:
                df['I_group'] = np.nan_to_num(I[j, :]).astype(complex)

            if not flag_groups:
                x = pd.cut(df[sort_on], np.linspace(min(df[sort_on]) * 0.9, max(df[sort_on]) * 1.1, groups + 1))
                x = x.cat.rename_categories(np.linspace(1, groups, groups).astype(int))
            else:
                if not self.flag_T:
                    HT_to_groups = self.HalfTurns.HalfTurns_to_conductor
                else:
                    HT_to_groups = self.HalfTurns.HalfTurns_to_sections
                HT_to_apertures = np.concatenate([self.Turns.turns_to_apertures, self.Turns.turns_to_apertures])
                # HT_to_apertures = np.repeat(self.Turns.turns_to_apertures, 2)
                HT_to_strands = self.HalfTurns.n_strands
                x = np.repeat(HT_to_groups, HT_to_strands) if M.shape[1] != self.General.num_HalfTurns else HT_to_groups
                apertures_x = np.repeat(HT_to_apertures, HT_to_strands) if M.shape[
                                                                               1] != self.General.num_HalfTurns else HT_to_apertures
                idx_ap1 = set(np.where(apertures_x == 1)[0])

            df['groups'] = x
            df = df.dropna(subset=['groups'])

            for i in range(1, groups + 1):
                group_indexes = df.index[df['groups'] == i]  # All Half turns
                valid_indexes = [idx for idx in group_indexes if idx in idx_ap1]  # Half of the Half Turns
                df.loc[group_indexes, 'R_group'] = np.average(df.loc[valid_indexes, 'R_group'])
                df.loc[group_indexes, 'L_group'] = np.average(df.loc[valid_indexes, 'L_group'])
                if len(I) != 0:
                    sum = np.sum(df.loc[valid_indexes, 'M_group'] * df.loc[valid_indexes, 'I_group'])
                    df.loc[group_indexes, 'I_group'] = sum

                M_sel = np.sum(df.loc[valid_indexes, 'M_group'] ** 2)
                s_r_temp = np.sign(np.real(M_sel))
                s_i_temp = np.sign(np.imag(M_sel))
                df.loc[group_indexes, 'M_group'] = s_r_temp * np.real(np.sqrt(M_sel)) + 1j * s_i_temp * np.imag(
                    np.sqrt(M_sel))

            df = df.drop_duplicates().reset_index(drop=True).drop('groups', axis=1)
            df = df.loc[~(df == 0).all(axis=1)]

            R_group[j, :] = df['R_group']
            M_group[j, :] = df['M_group']
            L_group[j, :] = df['L_group']
            if len(I) != 0:
                I_group[j, :] = df['I_group']

        if len(I) != 0:
            I_group = I_group / M_group
            return L_group, R_group, M_group, I_group
        else:
            return L_group, R_group, M_group

    ####################################################################################################################
    ############################################ FUNCTIONS TO READ AND ASSIGN F_MAG #####################################

    def read_COMSOL_field_file(self, Effect: str = None) -> np.ndarray:
        '''
         Calculates the diff_field in each filament due to the given effct as the difference between the result of the
         'retrieve_field_contributions_COMSOL'function and the field obtained from the Comsol simulation w/o effects.
         Then returns the field in each filament as the sum of the field from Roxie and the diff_field

         :param Effect: str that indicates the corresponding Not Conductor Loss effect -> Wedge or CB
        '''
        if Effect is not None:
            f_mag_Roxie = self.Strands.f_mag_Roxie
            f_mag_X_Roxie = self.Strands.f_mag_X_Roxie
            f_mag_Y_Roxie = self.Strands.f_mag_Y_Roxie
            f_mag_Comsol = self.Strands.f_mag_Comsol
            f_mag_X_Comsol = self.Strands.f_mag_X_Comsol
            f_mag_Y_Comsol = self.Strands.f_mag_Y_Comsol

            f_mag, fMag_X, fMag_Y = self.retrieve_field_contributions_COMSOL(Effect=Effect)

            f_X_diff = fMag_X * np.sign(f_mag_X_Roxie) - f_mag_X_Comsol
            f_Y_diff = fMag_Y * np.sign(f_mag_Y_Roxie) - f_mag_Y_Comsol
            f_diff = f_mag - f_mag_Comsol

            f_X = f_mag_X_Roxie + f_X_diff
            f_Y = f_mag_Y_Roxie + f_Y_diff
            f_mag = f_diff + f_mag_Roxie

            return f_mag, f_X, f_Y


    def retrieve_field_contributions_COMSOL(self, Effect: str = None) -> np.ndarray:
        '''
        Extracts the magnetic field data for each filament of the MB magnet from Excel files corresponding to a specific
        Comsol Model that includes a given effect.
        Multiple files exist for each effect, with each file resulting from a simulation using a different value of a
        particular parameter (usually temperature, T).

        To select the most accurate data, the function performs an interpolation between the desired value of the parameter
        and the data from the four closest simulation values saved in the Excel files.

        :param Effect: str indicating the specific Not Conductor Loss effect (either "Wedge" or "CB").

        :return f_mag: field in each filament for a magnet that includes the specified effect.
        :return f_mag_X: field along the X-axis in each filament for a magnet that includes the specified effect.
        :return f_mag_Y: field along the Y-axis in each filament for a magnet that includes the specified effect.
        '''

        local_library_path = os.path.join(Path(self.General.local_library_path).resolve(), 'TFM_input')
        value = self.magnet_data.field_interp_value
        frequency = self.frequency

        Param = []
        files_Field = []
        df_array_X = []
        df_array_Y = []
        df_array_Mag = []

        # value is the desired parameter for which we want to find accurate f_mag, f_mag_X, f_mag_Y
        # usually it is the T of the simulation, if it is not it can be specified in field_interp_value
        if value is None:
            value = self.temperature

        # Loop to extract all the possible parameters values for the Comsol model with effect that are presents in the excel files
        for dir in os.listdir(local_library_path):
            if dir.startswith('Field_Map') and ('Changed' not in dir):
                if Effect in dir:
                    parameter = dir.replace('.csv','').split('_')[-1]
                    Param.append(float(parameter)) # Saving the parameter values
                    files_Field.append(dir) # Saving the file directory

        Param = np.array(Param)
        files_Field = np.array(files_Field)

        if float(value) in Param: # If there is one file performed with parameter = value no need for the interpolation
            closest_Param = np.array([value]) # Taking just the value as closest parameter
        elif(value < Param.min() or value > Param.max()):# If the value is out of bounds -> error
            raise Exception('Error: Parameter out of range')
        else:
            closest_indices = np.argsort(np.abs(Param - value))[:4] # Otherwise taking the 4 closest values of the excel files
            closest_Param = Param[closest_indices]

        for i in range(len(closest_Param)): # Reading the files of the closest parameter simulations
            file = os.path.join(local_library_path, files_Field[i])
            df_COMSOL = pd.read_csv(file, header=None, dtype=str, na_filter=False)
            mapping = np.vectorize(lambda t: complex(t.replace('i', 'j')))
            df_COMSOL = mapping(df_COMSOL.values[2:, 2:]).T
            df_X = np.real(df_COMSOL[::2, :] * np.conjugate(df_COMSOL[::2, :]))
            df_Y = np.real(df_COMSOL[1::2, :] * np.conjugate(df_COMSOL[1::2, :]))
            df_array_X.append(df_X)
            df_array_Y.append(df_Y)

        order = np.argsort(closest_Param)
        closest_Param = closest_Param[order]
        df_array_X = np.array(df_array_X)
        df_array_X = df_array_X[order]
        df_array_Y = np.array(df_array_Y)
        df_array_Y = df_array_Y[order]

        if len(closest_Param) != 1:# If there are 4 closest parameter -> interpolation to find f_mag_X and f_mag_Y
            interp_X = RegularGridInterpolator((closest_Param, frequency), df_array_X)
            new_points_X = (np.array([value]), frequency) # value = Parameter to interpolate for = input
            f_mag_X = interp_X(new_points_X)

            interp_Y = RegularGridInterpolator((closest_Param, frequency), df_array_Y)
            new_points_Y = (np.array([value]), frequency)
            f_mag_Y = interp_Y(new_points_Y)
        else: # If there is only 1 closest parameter -> excel file with parameter = desired value, just take f_mag_X and f_mag_Y from that file
            f_mag_X = df_array_X[0, :, :]
            f_mag_Y = df_array_Y[0, :, :]

        f_mag = np.sqrt(f_mag_X + f_mag_Y)
        f_mag_X = np.sqrt(f_mag_X)
        f_mag_Y = np.sqrt(f_mag_Y)
        # f_mag_X = -1 * f_mag_X
        # f_mag_Y = -1 * f_mag_Y

        return f_mag, f_mag_X, f_mag_Y


    def retrieve_field_contributions_Roxie(self) -> np.ndarray:
        '''
        Extracts the magnetic field data for each filament of the corresponding magnet fstarting from the Magnetic field
        taken from the Ledetclass attributes

        :return f_mag: field in each filament for the magnet w/o effects
        :return f_mag_X: field along the X-axis in each filament for for the magnet w/o effects
        :return f_mag_Y: field along the Y-axis in each filament for the magnet w/o effects
        '''

        Bx = self.ledet_auxiliary.Bx
        By = self.ledet_auxiliary.By
        Iref = self.ledet_options.Iref

        f_mag_X = Bx / Iref
        f_mag_Y = By / Iref
        B_E = np.sqrt(Bx ** 2 + By ** 2)

        f_mag = np.sqrt(f_mag_X ** 2 + f_mag_Y ** 2)
        peakB_superPos = np.max(f_mag * Iref)
        peakB_real = np.max(B_E)
        f_peakReal_Superposition = peakB_real / peakB_superPos

        fMag_X = f_mag_X * f_peakReal_Superposition
        fMag_Y = f_mag_Y * f_peakReal_Superposition

        frequency = np.logspace(0, 6, 120+1)
        self.frequency=frequency
        fMag_X = np.repeat(fMag_X[:, np.newaxis], len(frequency), axis=1).T
        fMag_Y = np.repeat(fMag_Y[:, np.newaxis], len(frequency), axis=1).T
        f_mag = np.repeat(f_mag[:, np.newaxis], len(frequency), axis=1).T

        return f_mag, fMag_X, fMag_Y

    ####################################################################################################################
    ############################################ FUNCTIONS FOR L MATRX CHECKING #####################################

    def check_inductance_matrix_losses(self, Mutual_dict: dict):
        '''
        This function constructs the L Matrix containing all the effects that are selected.
        This function has in the diagonal all the L corresponding to a given effect
        On the first column and on the first row at the index corresponding to that effect it has the M of that effect
        In the crossing betwwen indices of different effects, it has the mutual coupling between these two.
        In all the other places it has 0

        :param Mutual_dict: dictionary with the Mutual coupling between all the different effects
        '''
        frequency = self.frequency
        groups = self.General.groups
        effs = self.Effective.effs

        Effects = np.repeat(np.array(effs), groups)
        Effects = np.insert(Effects, 0, 'Mag').astype(str)
        L_matrix_list = []

        for freq in range(len(frequency)):
            # Creating the matrix and filling it with 0
            L_matrix = np.zeros((len(Effects), len(Effects)))
            for eff in range(len(Effects)):
                    if eff == 0:  # Checking if the Effect[eff] == 'Mag'
                        L_matrix[0, 0] = self.General.L_mag
                    else:
                        if Effects[eff-1] == Effects[eff]: # Checking if it's not the first time that we encounter this effect in the dict
                            count_group += 1  # If it's not the first time, the group counting must be incremented
                        else:
                            count_group = 0  # If it is the first time, the group counting is set to zero

                        # Filling the matrix with the L values along the diagonal and the M values symmetrically
                        # on the first row and on the first column, selecting the right values according to count_group
                        if Effects[eff] == 'Wedge' or Effects[eff] == 'CB':
                            L_matrix[0, eff] = self.getAttribute(Effects[eff], 'M')[freq]
                            L_matrix[eff, 0] = self.getAttribute(Effects[eff], 'M')[freq]
                            L_matrix[eff, eff] = self.getAttribute(Effects[eff], 'L')[freq]
                        else:
                            L_matrix[0, eff] = self.getAttribute(Effects[eff], 'M')[freq, count_group]
                            L_matrix[eff, 0] = self.getAttribute(Effects[eff], 'M')[freq, count_group]
                            L_matrix[eff, eff] = self.getAttribute(Effects[eff], 'L')[freq, count_group]

                        for key, value in Mutual_dict.items():
                            if Effects[eff] in key:  # For each key of the dict, check if the current effect is contained in it
                                for l in range(len(Effects)):  # If yes, find the other effect contained in the same key
                                    if l != 0 and eff != l and Effects[l] in key:
                                        if Effects[l - 1] != Effects[l]:
                                            # Take the first effect with that name and then select the right column index
                                            # and the right value by selecting the same count_group of the Effects[eff] element
                                            L_matrix[eff, l+count_group] = value[freq, count_group]
            L_matrix_list.append(L_matrix)

        for i in range(len(L_matrix_list)):
            if not is_positive_definite(L_matrix_list[i]):
                raise Exception(f'Matrix not positive definite for frequency {frequency[i]}')

    ####################################################################################################################
    ############################################ RESISTIVITY FUNCTIONS CALCULATION #####################################

    def rhoCu_nist(self, T: float, RRR: np.ndarray, B: np.ndarray) -> np.ndarray:
        '''
        Helper function to calculate resistivity of copper. Taken from steam-materials library

        :param T: Temperature
        :return: array of resistivities
        '''

        T_ref_RRR = 273
        # Make T of the same size of B and RRR
        T_flatten = np.tile(T, (len(B), 1)).flatten()
        # Create numpy2d by stacking B, RRR, and T along axis 0
        numpy2d = np.vstack((T_flatten, B, RRR, T_ref_RRR * np.ones_like(T_flatten)))
        sm_cp_rho = STEAM_materials('CFUN_rhoCu_v1', numpy2d.shape[0], numpy2d.shape[1], matpath)
        RhoCu = sm_cp_rho.evaluate(numpy2d)

        return RhoCu

    def rhoSS_nist(self, T: float) -> np.ndarray:
        '''
        Helper function to calculate resistivity of copper. Taken from steam-materials library

        :param T: Temperature
        :return: array of resistivities
        '''
        T_flatten = np.tile(T, (1)).flatten()
        # Create numpy2d by stacking B, RRR, and T along axis 0
        sm_cp_rho = STEAM_materials('CFUN_rhoSS_v1', 1, 1, matpath)
        RhoSS = sm_cp_rho.evaluate(T_flatten)

        return RhoSS

    ####################################################################################################################
    ###################################### GET AND SET FUNCTIONS FOR THE ATTRIBUTES #####################################

    def setAttribute(self, TFMclass, attribute: str, value):
        try:
            setattr(TFMclass, attribute, value)
        except:
            setattr(getattr(self, TFMclass), attribute, value)


    def getAttribute(self, TFMclass, attribute: str):
        try:
            return getattr(TFMclass, attribute)
        except:
            return getattr(getattr(self, TFMclass), attribute)


########################################################################################################################
########################################################################################################################
########################################################################################################################



########################################################################################################################
################################### TRANSLATE FUNCTIONS OF LEDET DATA TO TFM DATA  #####################################

def lookupModelDataToTFMHalfTurns(key: str):
    """
     Retrieves the correct HalfTurnsTFM parameter name for a DataModelMagnet input
    """
    lookup = {
        'nStrands_inGroup': 'n_strands',
        'wBare_inGroup': 'bare_cable_width',
        'hBare_inGroup': 'bare_cable_height_mean',
        'Lp_s_inGroup': 'strand_twist_pitch',
        'R_c_inGroup': 'Rc',
        'RRR_Cu_inGroup': 'RRR',
        'ds_inGroup': 'diameter',
        'f_SC_strand_inGroup': 'fsc',
        'f_ro_eff_inGroup': 'f_rho_effective',

        'alphasDEG': 'alphaDEG_ht',
        'rotation_block': 'rotation_ht',
        'mirror_block': 'mirror_ht'
    }

    returned_key = lookup[key] if key in lookup else None
    return returned_key


def lookupModelDataToTFMStrands(key: str):
    """
    Retrieves the correct StrandsTFM parameter name for a DataModelMagnet input
    """
    lookup = {
        'df_inGroup': 'filament_diameter',
        'ds_inGroup': 'diameter',
        'f_SC_strand_inGroup': 'fsc',
        'f_ro_eff_inGroup': 'f_rho_effective',
        'Lp_f_inGroup': 'fil_twist_pitch',
        'RRR_Cu_inGroup': 'RRR',
        'dfilamentary_inGroup': 'd_filamentary',
        'dcore_inGroup': 'd_core',
    }

    returned_key = lookup[key] if key in lookup else None
    return returned_key


########################################################################################################################
############################### FUNCTIONS TO CHANGE .FUNC PRAAMETERS IN THE LIB FILE  ###################################

def change_library_EqLoop(path_file: Path, element: str, frequency: np.ndarray, L_eq: np.ndarray, R_eq: np.ndarray, M_eq: np.ndarray, groups: int = 2, force_new_name: Path = ''):
    '''
    Helper function that changes the TFM magnet .lib file and includes in Table function the given R,L,M parameter

    element = Element, for which the RLM to be inserted e.g. BS, CPS, ED ...

    If L_eq, M_eq or R_eq are empty, they will not be written
    '''
    if groups==1:
        if L_eq.size: L_eq = L_eq.reshape((len(L_eq), 1))
        if R_eq.size: R_eq = R_eq.reshape((len(R_eq), 1))
        if M_eq.size: M_eq = M_eq.reshape((len(M_eq), 1))


    #### Creating string for equivalent inductance
    str_L = []
    if L_eq.size:
        for i in range(groups):
            group = [f'{element}_L_{i+1}(1)', '{TABLE{FREQ}=']
            str_group_L = f'.FUNC' + ' ' + ' '.join("{:<20}".format(g) for g in group)
            L = L_eq[:,i]
            for j in range(len(frequency)):
                str_group_L = str_group_L + f'({frequency[j]},{L[j]})     '
            str_group_L = str_group_L + '}\n'
            str_L.append(str_group_L)

    #### Creating string for equivalent resistance
    str_R = []
    if R_eq.size:
        for i in range(groups):
            group = [f'{element}_R_{i + 1}(1)', '{TABLE{FREQ}=']
            str_group_R = f'.FUNC' + ' ' + ' '.join("{:<20}".format(g) for g in group)
            R = R_eq[:, i]
            for j in range(len(frequency)):
                str_group_R = str_group_R + f'({frequency[j]},{R[j]})     '
            str_group_R = str_group_R + '}\n'
            str_R.append(str_group_R)

    #### Creating string for equivalent mutual inductance
    str_M = []
    if M_eq.size:
        for i in range(groups):
            group = [f'{element}_M_{i + 1}(1)', '{TABLE{FREQ}=']
            str_group_M = f'.FUNC' + ' ' + ' '.join("{:<20}".format(g) for g in group)
            M = M_eq[:, i]
            for j in range(len(frequency)):
                str_group_M = str_group_M + f'({frequency[j]},{np.real(M[j])}+{np.imag(M[j])}J)     '
            str_group_M = str_group_M + '}\n'
            str_M.append(str_group_M)

    ## Opening library file
    lib_path = path_file
    with open(lib_path) as f:
        lines = f.readlines()

    ## Changing elements in library
    for k in range(len(lines)):
        line = lines[k]
        for i in range(groups):
            if line.startswith(f'.FUNC {element}_L_{i+1}') and str_L:
                lines[k] = str_L[i]
            elif line.startswith(f'.FUNC {element}_R_{i+1}') and str_R:
                lines[k] = str_R[i]
            elif line.startswith(f'.FUNC {element}_M_{i+1}') and str_M:
                lines[k] = str_M[i]

    text_lib = ''.join(lines)

    if not force_new_name:
        new_lib_path = Path('..//lib//MB_TFM_General_Adjusted.lib').resolve()
    else:
        new_lib_path = force_new_name
    with open(new_lib_path, 'w') as f:
        f.write(text_lib)
    return new_lib_path

def change_library_MutualCoupling(path_file: Path, element: str, frequency: np.ndarray, M_eq: np.ndarray):
    '''
    Helper function that changes the mutual coupling values of element to M_eq. Can be multiple values, e.g. a
    changing coupling over frequency
    '''

    #### Creating string for equivalent mutual inductance
    str_group_M = f'.FUNC {element}(1)					' + '{TABLE{FREQ} =  '
    for j in range(len(frequency)):
        str_group_M = str_group_M + f'({frequency[j]},{np.real(M_eq[j])}+{np.imag(M_eq[j])}J)     '
    str_group_M = str_group_M + '}\n'

    ## Opening library file
    lib_path = path_file
    with open(lib_path) as f:
        lines = f.readlines()

    ## Changing elements in library
    for k in range(len(lines)):
        line = lines[k]
        if line.startswith(f'.FUNC {element}'):
            lines[k] = str_group_M

    text_lib = ''.join(lines)

    with open(path_file, 'w') as f:
        f.write(text_lib)
    return path_file

########################################################################################################################
################################## FUNCTION TO CALCULATE TAU OF CB AND WEDGE   ########################################

# def calculate_tau(P_tot: np.ndarray, frequency: np.ndarray) -> int:
#     '''
#     Helper function to calculate the tau_index corresponding to the frequency vector for a specific effect
#
#     :param P_tot: P vector used to calculate the tau
#
#     :return: tau_index corresponding to the frequency vector
#     '''
#     #interpolate P+f np.logspace(0,5,1000)
#     # Calculate first derivative
#     dPdt = np.diff(P_tot) / P_tot[1:]
#     # Calculate second derivative
#     dPdt2 = np.diff(dPdt) / dPdt[1:]
#     sm_dPdt2 = smooth_curve(dPdt2, 5, n_pad=1)
#
#     # # Find first peak using specified thresholds to avoid choosing peaks due to noise
#     min_peak_height = 0.005
#     min_peak_prominence = 0.005
#     idx_first_min = find_peaks(-sm_dPdt2, height=min_peak_height, prominence=min_peak_prominence)[0][0]
#     # Calculate the sign of sm_dPdt2 after the first index to check the first time sm_dPst2 crosses 0 after the first minimum
#     # and calculate tau
#     sign = np.sign(sm_dPdt2)[idx_first_min:]
#     indices = np.where((sign[:-1] < 0) & (sign[1:] > 0))[0][0] - 1
#     tau_index = indices + idx_first_min - 1 - (len(P_tot) - len(sm_dPdt2))
#     # Check for plateaus in sm_dPdt2
#     plateau_indices = np.where(np.diff(sm_dPdt2) <= 0.0003)[0]
#     if tau_index in plateau_indices:
#         list_index = []
#         index = np.where(plateau_indices == tau_index)[0][0]
#         # Take the left part of the plateau (respect to tau_index) and reverse it
#         plateau_indices_left = plateau_indices[:index][::-1]
#         # Take the values which are -1 or -2 comparing to the previous value
#         for i in range(len(plateau_indices_left)):
#             if i == 0:
#                 list_index.append(plateau_indices_left[i])
#             elif (plateau_indices_left[i - 1] - plateau_indices_left[i] <= 2):
#                 list_index.append(plateau_indices_left[i])
#             else:
#                 break
#         # Take the right part of the plateau (respect to tau_index)
#         plateau_indices_right = plateau_indices[index + 1:]
#         # Take the values which are +1 or +2 comparing to the previous value
#         for i in range(len(plateau_indices_right)):
#             if i == 0:
#                 list_index.append(plateau_indices_right[i])
#             elif (plateau_indices_right[i] - plateau_indices_right[i - 1] <= 2):
#                 list_index.append(plateau_indices_right[i])
#             else:
#                 break
#         tau_index = int((np.min(list_index) + np.max(list_index)) / 2)
#
#
#     return tau_index

def calculate_tau(P_tot: np.ndarray, frequency: np.ndarray) -> int:
    '''
    Helper function to calculate the tau_index corresponding to the frequency vector for a specific effect

    :param P_tot: P vector used to calculate the tau

    :return: tau_index corresponding to the frequency vector
    '''
    # Interpolation
    s = np.log10(frequency[2])

    dPdt = np.diff(P_tot) / P_tot[1:]
    dPdt2 = np.diff(dPdt) / dPdt[1:]
    # spl = make_interp_spline(frequency[2:], dPdt2, k=5)
    # dPdt2_interp = spl(frequency_interp)# k=5 for quintic
    spl = make_interp_spline(frequency[2:], dPdt2, k=5)
    frequency_interp = np.logspace(0, 5, 1000)
    sm_dPdt2 = spl(frequency_interp)
    sm_dPdt2 = abs(sm_dPdt2[0]) + sm_dPdt2

    # # Find first peak using specified thresholds to avoid choosing peaks due to noise
    min_peak_height = 0.0005
    min_peak_prominence = 0.0005
    idx_first_min = find_peaks(-sm_dPdt2, height=min_peak_height, prominence=min_peak_prominence)[0][0]
    # Calculate the sign of sm_dPdt2 after the first index to check the first time sm_dPst2 crosses 0 after the first minimum
    # and calculate tau
    sign = np.sign(sm_dPdt2)[idx_first_min:]
    indices = np.where((sign[:-1] < 0) & (sign[1:] > 0))[0][0]
    tau_index = indices + idx_first_min
    # Check for plateaus in sm_dPdt2
    tau = 1 /frequency_interp[tau_index]
    # plateau_indices = np.where(np.abs(sm_dPdt2 - tau_value) <= 0.0003)[0]
    # if tau_index in plateau_indices:

    #     list_index = []
    #     index = np.where(plateau_indices == tau_index)[0][0]
    #     # Take the left part of the plateau (respect to tau_index) and reverse it
    #     plateau_indices_left = plateau_indices[:index][::-1]
    #     # Take the values which are -1 or -2 comparing to the previous value
    #     for i in range(len(plateau_indices_left)):
    #         if i == 0:
    #             list_index.append(plateau_indices_left[i])
    #         elif (plateau_indices_left[i - 1] - plateau_indices_left[i] <= 2):
    #             list_index.append(plateau_indices_left[i])
    #         else:
    #             break
    #     # Take the right part of the plateau (respect to tau_index)
    #     plateau_indices_right = plateau_indices[index + 1:]
    #     # Take the values which are +1 or +2 comparing to the previous value
    #     for i in range(len(plateau_indices_right)):
    #         if i == 0:
    #             list_index.append(plateau_indices_right[i])
    #         elif (plateau_indices_right[i] - plateau_indices_right[i - 1] <= 2):
    #             list_index.append(plateau_indices_right[i])
    #         else:
    #             break
    #
    #     tau_index = int((np.min(list_index) + np.max(list_index)) / 2)
    #     tau = 1/frequency_interp[tau_index]


    return tau





########################################################################################################################
################################################### HELPER FUNCTIONS   #################################################

def smooth_curve(y: np.ndarray, box_pts: int, n_pad: int = 20) -> np.ndarray:
    '''
    Helper function that smoothes a curve with a box filter
    :param y: np.ndarray - Array to be smoothed
    :param box_pts: int - width of the box filter (generally 3 or 5)
    :param n_pad: int - width of zero-padding
    :return: the smoothed array
    '''
    box = np.ones(box_pts) / box_pts
    if len(y.shape)>1:
        y_smooth = np.zeros(y.shape)
        for i in range(y.shape[0]):
            y_padded = np.pad(y[i,:], n_pad, mode='constant',constant_values=(y[i,0],y[i,-1]))
            y_filtered = np.convolve(y_padded, box, mode='same')
            y_smooth[i, :] = y_filtered[n_pad:-n_pad]
    else:
        y_padded = np.pad(y, n_pad, mode='constant', constant_values=(y[0], y[-1]))
        y_smooth = np.convolve(y_padded, box, mode='same')
    return y_smooth[n_pad: -n_pad]


def is_positive_definite(matrix):
    return np.all(np.linalg.eigvals(matrix) >= 0)

