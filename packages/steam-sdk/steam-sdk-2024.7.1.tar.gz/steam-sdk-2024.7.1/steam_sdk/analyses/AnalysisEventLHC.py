import shutil

from ruamel.yaml import YAML

from steam_sdk.analyses.AnalysisSTEAM import AnalysisSTEAM
from steam_sdk.analyses.AnalysisEvent import find_IPQ_circuit_type_from_IPQ_parameters_table, \
    get_circuit_name_from_eventfile, generate_unique_event_identifier_from_eventfile, \
    get_signal_keys_from_configurations_file, determine_config_path_and_configuration, \
    get_circuit_type_from_circuit_name, extract_signal_touples_from_config, get_hard_coded_filename_postfix
from steam_sdk.data.DataAnalysis import ModifyModelMultipleVariables, MakeModel, ParsimEvent, \
    DefaultParsimEventKeys, RunSimulation, RunViewer, CalculateMetrics
import os
import ruamel.yaml
import warnings



def generate_settings_dictionary(settings_file_path, dict_settings_paths: dict = None ):

    # Definition of a default dictionary that contains only the keys needed for an LHC Event Analysis
    default_dict_settings_paths = {
        'library_path': os.path.abspath(os.path.join(os.getcwd(), "..", "..", "..", "steam_models")),
        'PSPICE_path': None,
        'XYCE_path': None,
        'PSPICE_library_path': None,
        'local_PSPICE_folder': None,
        'local_XYCE_folder': None,
        'directory_config_files': None,
        'output_directory_yaml_files': os.path.join(os.getcwd(), 'output', 'yaml_files'),                               #TODO: put by default every single file in the simulation folder
        'output_directory_parsim_sweep_files': os.path.join(os.getcwd(), 'output', 'parsim_sweep_files'),
        'output_directory_initialization_file_viewer': os.path.join(os.getcwd(), 'output', 'initialization_files_viewer'),
        'path_postmortem_offline_data_folder': None,
        'filepath_to_temp_viewer_csv': None,
        'path_output_pdf_report': None ,
        'metrics_to_calculate':None,
        'local_library_path': None,
        "timeout_s": None
    }

    # Fill up non user specific keys of the default dictionary with keys from the settings system.yaml
    with open(settings_file_path, 'r') as yaml_file:
        yaml = ruamel.yaml.YAML(typ="safe", pure=True)
        settings_file_yaml_data = yaml.load(yaml_file)

    for key, _ in default_dict_settings_paths.items():
        if key in settings_file_yaml_data and default_dict_settings_paths[key] is None:
            default_dict_settings_paths[key] = settings_file_yaml_data[key]
            print(f"Took over {key} from settings file")

    # If user provides a settings dictionary, overwrite the default values with the dictionary, provided by the user
    for key, _ in default_dict_settings_paths.items():
        if dict_settings_paths and key in dict_settings_paths and dict_settings_paths[key]:
            default_dict_settings_paths[key] = dict_settings_paths[key]
        else:
            message = f"Key {key} not defined by user in dictionary took over default value {default_dict_settings_paths[key]}"
            warnings.warn(message)

    # Now, dict_settings_paths contains the updated values from the YAML file
    # print(default_dict_settings_paths)
    return default_dict_settings_paths

def update_attributes_from_settings_dictionary(AnalysisSTEAM_object,default_dict_settings_paths):

    #Set the Permanent Settings to True in order to make sure that the settings are not drawn from a file
    AnalysisSTEAM_object.data_analysis.GeneralParameters.flag_permanent_settings = True

    # Check and update settings of the AnalysisSTEAM object passed with entries of the dictionary passed
    for name, _ in default_dict_settings_paths.items():
        if hasattr(AnalysisSTEAM_object.settings, name):
            print(f"Found {name} in settings")
            value = default_dict_settings_paths[name]
            setattr(AnalysisSTEAM_object.settings, name, value)
            if value:
                print('{}: {}. Added.'.format(name, value))
        elif name == 'library_path':
            AnalysisSTEAM_object.library_path = default_dict_settings_paths['library_path']
        else:
            print('{}: not found in the settings. Skipped.'.format(name))

    # Update data_analysis module settings with entries of the dictionary passed
    # AnalysisSTEAM_object.data_analysis.WorkingFolders.library_path = default_dict_settings_paths['library_path']
    AnalysisSTEAM_object.data_analysis.PermanentSettings.PSPICE_path = default_dict_settings_paths['PSPICE_path']
    AnalysisSTEAM_object.data_analysis.PermanentSettings.XYCE_path = default_dict_settings_paths['XYCE_path']
    AnalysisSTEAM_object.data_analysis.PermanentSettings.local_PSPICE_folder = default_dict_settings_paths['local_PSPICE_folder']
    AnalysisSTEAM_object.data_analysis.PermanentSettings.local_XYCE_folder = default_dict_settings_paths['local_XYCE_folder']

def steam_analyze_lhc_event(settings_file_path:str, input_csv_file: str, flag_run_software: bool, flag_calculate_metrics: bool, software: str, overwrite_settings: dict, file_counter: int, modify_model_steps: dict =None):

    #Create a settings_dictionary that contains all the settings needed for an analysis
    settings_dictionary = generate_settings_dictionary(settings_file_path, overwrite_settings)
    circuit_name = get_circuit_name_from_eventfile(event_file=input_csv_file)
    circuit_type = get_circuit_type_from_circuit_name(circuit_name, settings_dictionary['library_path'])

    if circuit_type == "RCD_AND_RCO":
        analyze_RCD_RCO_event(settings_dictionary,os.path.join(os.getcwd(), input_csv_file), flag_run_software, software, file_counter, modify_model_steps)
    else: # All other double circuits like RQs and RCBX can be run with this function as this is how it is implemented in steam_sdk:
        analyze_circuit_event(settings_dictionary,os.path.join(os.getcwd(), input_csv_file), circuit_type, flag_run_software, flag_calculate_metrics, software, file_counter, circuit_name)

def analyze_circuit_event(settings_dictionary: dict, input_csv_file: str,circuit_type: str, flag_run_software: bool, flag_calculate_metrics: bool, software: str, file_counter: int, circuit_name: str):
    aSTEAM = AnalysisSTEAM()
    update_attributes_from_settings_dictionary(aSTEAM, settings_dictionary)
    timeout_s = settings_dictionary["timeout_s"]

    if software == 'PSPICE':
        local_folder = settings_dictionary['local_PSPICE_folder']
        print(f"Changed local folder to {local_folder}")
    elif software == 'XYCE':
        local_folder = settings_dictionary['local_XYCE_folder']
        print(f"Changed local folder to {local_folder}")

    unique_identifier_event = generate_unique_event_identifier_from_eventfile(
        file_name=os.path.basename(input_csv_file))

    #only combination of circuit_name and eventlabel is truely unique since the double circuits
    hard_coded_filename_postfix = get_hard_coded_filename_postfix(unique_identifier_event, circuit_name)

    if not settings_dictionary['filepath_to_temp_viewer_csv']:
        settings_dictionary['filepath_to_temp_viewer_csv'] = \
            fr"C:\temp{software}\{circuit_type}\{file_counter}\temp_viewer{hard_coded_filename_postfix}.csv"

    if not settings_dictionary['path_output_pdf_report']:
        settings_dictionary['path_output_pdf_report'] = \
            fr"C:\temp{software}\{circuit_type}\{file_counter}\report{hard_coded_filename_postfix}.pdf"

    output_directory_yaml_files = settings_dictionary['output_directory_yaml_files']
    output_directory_parsim_sweep_files = settings_dictionary['output_directory_parsim_sweep_files']
    #TODO: include following line in RCD RCO
    output_directory_initialization_file_viewer = settings_dictionary['output_directory_initialization_file_viewer']

    yaml_file_name = f'infile_{unique_identifier_event}.yaml'
    parsim_sweep_file_name = f'parsim_sweep_{software}_{circuit_type}_{unique_identifier_event}_{file_counter}.csv'

    path_output_yaml_file = os.path.join(output_directory_yaml_files,yaml_file_name)
    path_output_parsim_sweep_csv = os.path.join(output_directory_parsim_sweep_files,parsim_sweep_file_name)

    #get all signals that are defined in the config file to later include them in the model using a ModifyModelMultipleVariables
    #step, but since the analysis is not supposed to be dependent from a config file, this
    signals_to_include = ['']
    if settings_dictionary['directory_config_files'] != None:
        full_config_file_path , configuration = determine_config_path_and_configuration(directory_config_files =
                                                                              settings_dictionary['directory_config_files'],
                                                                            steam_circuit_type=circuit_type)
        signals_to_include = get_signal_keys_from_configurations_file(full_config_file_path, configuration = configuration)

        variables_to_analyze = extract_signal_touples_from_config(full_config_file_path, configuration)

    else:
        warnings.warn("no signals from the config file will be included in the model, variables entry will be empty in"
                      " the cir file, causing all signals to be calculated")

    aSTEAM.data_analysis.AnalysisStepDefinition = {
        'makeModel_ref': MakeModel(type='MakeModel', model_name='BM', file_model_data=circuit_type,
                                   case_model='circuit', software=software, simulation_name=None,
                                   simulation_number=None, flag_build=True, verbose=False,
                                   flag_plot_all=False, flag_json=False),
        'modifyModel_probe1': ModifyModelMultipleVariables(type='ModifyModelMultipleVariables', model_name='BM',
                                       variables_to_change=['PostProcess.probe.probe_type'],
                                       variables_value=[['CSDF']], software=software, simulation_name=None,
                                       simulation_numbers=[]),

        #Here I implement an additional step so that all signals (and only those) are safed in the variables
        'modifyModel_include_config_signals': ModifyModelMultipleVariables(type='ModifyModelMultipleVariables', model_name='BM',
                                                          variables_to_change=['PostProcess.probe.variables'],
                                                          variables_value=[[signals_to_include]], software=software,
                                                          simulation_name=None,
                                                          simulation_numbers=[]),

        'runParsimEvent': ParsimEvent(type='ParsimEvent', input_file=input_csv_file,
                                      path_output_event_csv=path_output_parsim_sweep_csv,
                                      path_output_viewer_csv=output_directory_initialization_file_viewer,
                                      simulation_numbers=[file_counter], model_name='BM', case_model='circuit',
                                      simulation_name=circuit_type, software=software, t_PC_off=None,
                                      rel_quench_heater_trip_threshold=None, current_polarities_CLIQ=[],
                                      dict_QH_circuits_to_QH_strips={},
                                      default_keys=DefaultParsimEventKeys(local_LEDET_folder=None,
                                                                          path_config_file=None, default_configs=[],
                                                                          path_tdms_files=None,
                                                                          path_output_measurement_files=None,
                                                                          path_output=local_folder),
                                      path_postmortem_offline_data_folder=settings_dictionary['path_postmortem_offline_data_folder'],
                                      path_to_configurations_folder = settings_dictionary['directory_config_files'],
                                      filepath_to_temp_viewer_csv = settings_dictionary['filepath_to_temp_viewer_csv']
                                      ),
        'run_simulation': RunSimulation(type='RunSimulation', software=software, simulation_name="from_ParsimEvent_step", simulation_numbers=[file_counter],
        timeout_s = timeout_s ),

        "RunViewer": RunViewer(type="RunViewer",
                               file_name_transients=settings_dictionary['filepath_to_temp_viewer_csv'],
                               flag_analyze=True,
                               verbose=True,
                               flag_save_figures=True, viewer_name="viewer_1",
                               path_output_pdf_report=settings_dictionary['path_output_pdf_report']),

        "CalculateMetrics": CalculateMetrics(type="CalculateMetrics",
                                             viewer_name="viewer_1",
                                             metrics_name="metrics",
                                             metrics_to_calculate=settings_dictionary['metrics_to_calculate'],
                                             variables_to_analyze=variables_to_analyze,
                                             metrics_output_filepath = os.path.join(local_folder,circuit_type,str(file_counter),"output_metrics.yaml")
                                             ),
    }
    aSTEAM.output_path = local_folder
    if software == 'PSPICE':
        aSTEAM.data_analysis.PermanentSettings.local_PSPICE_folder = local_folder
    elif software == 'XYCE':
        aSTEAM.data_analysis.PermanentSettings.local_XYCE_folder = local_folder

    AnalysisStepSequence = ['makeModel_ref', 'modifyModel_probe1', 'modifyModel_include_config_signals',
                            'runParsimEvent']

    if flag_run_software == True: AnalysisStepSequence.append('run_simulation')

    # If the flag for running a simulation is set, the run_simulation step will be appended to the analysis step sequence
    if flag_calculate_metrics== True: AnalysisStepSequence.extend(["RunViewer", "CalculateMetrics"])

    aSTEAM.data_analysis.AnalysisStepSequence = AnalysisStepSequence

    if software == 'PSPICE':
        list_output_file = [os.path.join(aSTEAM.settings.local_PSPICE_folder, f'{circuit_type}', f'{file_counter}',
                                     f'{circuit_type}.cir')]
    elif software == 'XYCE':
        list_output_file = [os.path.join(aSTEAM.settings.local_XYCE_folder, f'{circuit_type}', f'{file_counter}',
                                     f'{circuit_type}.cir')]

    if os.path.exists(path_output_yaml_file): os.remove(path_output_yaml_file)
    for file in list_output_file:
        if os.path.exists(file): os.remove(file)

    #act
    aSTEAM.write_analysis_file(path_output_file=path_output_yaml_file)
    aSTEAM.run_analysis(verbose= True)

    # copy the eventfile to the local PSPICE Folder: TODO: this logic will probably not work for double circuits
    if software == 'PSPICE':
            shutil.copyfile(input_csv_file,os.path.join(aSTEAM.settings.local_PSPICE_folder, f'{circuit_type}', f'{file_counter}',f'Eventfile_{unique_identifier_event}.csv'))
    elif software == 'XYCE':
            shutil.copyfile(input_csv_file,os.path.join(aSTEAM.settings.local_XYCE_folder, f'{circuit_type}', f'{file_counter}', f'Eventfile_{unique_identifier_event}.csv'))

    # print summary entry if possible:
    if flag_calculate_metrics:
        average_metrics = aSTEAM.summary
        print("======================== Metrics ========================")
        print(f"The average metrics for this event are {average_metrics}")

def analyze_RCD_RCO_event(settings_dictionary: dict, input_csv_file: str, flag_run_software: bool, software: str, file_counter: int, modify_model_steps: dict):

    #TODO: include necessary code for the modify_model_steps dict if it proves to be usefull

    if software == 'PSPICE':
        local_folder = settings_dictionary['local_PSPICE_folder']
        print(f"Changed local folder to {local_folder}")
    elif software == 'XYCE':
        local_folder = settings_dictionary['local_XYCE_folder']
        print(f"Changed local folder to {local_folder}")

    unique_identifier_event = generate_unique_event_identifier_from_eventfile(
        file_name=os.path.basename(input_csv_file))

    output_directory_yaml_files = settings_dictionary['output_directory_yaml_files']
    output_directory_parsim_sweep_files = settings_dictionary['output_directory_parsim_sweep_files']

    #yaml_file_name = f'Infile_{software}_{unique_identifier_event}_{file_counter}.yaml'
    parsim_sweep_file_name_RCO = f'parsim_sweep_file_RCO_{software}_RCO_{unique_identifier_event}_{file_counter}.csv'
    parsim_sweep_file_name_RCD = f'parsim_sweep_file_RCD_{software}_RCD_{unique_identifier_event}_{file_counter}.csv'

    path_output_parsim_sweep_RCO_csv = os.path.join(output_directory_parsim_sweep_files, parsim_sweep_file_name_RCO)
    path_output_parsim_sweep_RCD_csv = os.path.join(output_directory_parsim_sweep_files, parsim_sweep_file_name_RCD)

    # arrange
    file_name_analysis = os.path.join(os.getcwd(), "analysisSTEAM_settings.yaml") #file containing settings paths

    aSTEAM_1 = AnalysisSTEAM()
    update_attributes_from_settings_dictionary(aSTEAM_1, settings_dictionary)

    if software == 'PSPICE':
        aSTEAM_1.settings.local_PSPICE_folder = local_folder
    elif software == 'XYCE':
        aSTEAM_1.settings.local_XYCE_folder = local_folder

    #get all signals that are defined in the config file to later include them in the model using a ModifyModelMultipleVariables
    #step, but since the analysis is not supposed to be dependent from a config file, this
    signals_to_include = ['']
    if settings_dictionary['directory_config_files'] != None:
        full_config_file_path, configuration = determine_config_path_and_configuration(directory_config_files =
                                                                              settings_dictionary['directory_config_files'],
                                                                            steam_circuit_type="RCO")
        signals_to_include = get_signal_keys_from_configurations_file(full_config_file_path, configuration = configuration)
    else:
        warnings.warn("no signals from the config file will be included in the model, variables entry will be empty in"
                      " the cir file, causing all signals to be calculated")

    aSTEAM_1.data_analysis.AnalysisStepDefinition = {
         'makeModel_ref': MakeModel(
            type='MakeModel', model_name='BM', file_model_data='RCO',
            case_model='circuit', software=software, simulation_name=None,
            simulation_number=None, flag_build=True, verbose=False,
            flag_plot_all=False, flag_json=False),
         'modifyModel_probe1': ModifyModelMultipleVariables(
             type='ModifyModelMultipleVariables', model_name='BM',
             variables_to_change=['PostProcess.probe.probe_type'],
             variables_value=[['CSDF']], software=software,
             simulation_name=None,
             simulation_numbers=[]),
         # Here I implement an additional step so that all signals (and only those) are safed in the variables
         'modifyModel_include_config_signals': ModifyModelMultipleVariables(
             type='ModifyModelMultipleVariables', model_name='BM',
             variables_to_change=['PostProcess.probe.variables'],
             variables_value=[[signals_to_include]], software=software,
             simulation_name=None,
             simulation_numbers=[]),
        'runParsimEvent': ParsimEvent(
            type='ParsimEvent',input_file=input_csv_file,
            path_output_event_csv=path_output_parsim_sweep_RCO_csv, path_output_viewer_csv=None,
            simulation_numbers=[file_counter], model_name='BM', case_model='circuit',
            simulation_name='RCO', software=software, t_PC_off=None, rel_quench_heater_trip_threshold=None,
            current_polarities_CLIQ=[], dict_QH_circuits_to_QH_strips={},default_keys=DefaultParsimEventKeys(
            local_LEDET_folder=None, path_config_file=None,default_configs=[],path_tdms_files=None,
            path_output_measurement_files=None,path_output=local_folder),
            path_postmortem_offline_data_folder = settings_dictionary['path_postmortem_offline_data_folder'],
            path_to_configurations_folder = settings_dictionary['directory_config_files'],
            filepath_to_temp_viewer_csv = settings_dictionary['filepath_to_temp_viewer_csv']),
        'run_simulation': RunSimulation(type='RunSimulation', software=software, simulation_name='RCO', simulation_numbers=[file_counter])}
    aSTEAM_1.output_path = local_folder
    if software == 'PSPICE':
        aSTEAM_1.data_analysis.PermanentSettings.local_PSPICE_folder = local_folder
    elif software == 'XYCE':
        aSTEAM_1.data_analysis.PermanentSettings.local_XYCE_folder = local_folder
    if flag_run_software == False:
        aSTEAM_1.data_analysis.AnalysisStepSequence = ['makeModel_ref', 'modifyModel_probe1',
                                                       'modifyModel_include_config_signals', 'runParsimEvent']
    else:
        aSTEAM_1.data_analysis.AnalysisStepSequence = ['makeModel_ref', 'modifyModel_probe1',
                                                       'modifyModel_include_config_signals', 'runParsimEvent',
                                                       'run_simulation']

    aSTEAM_2 = AnalysisSTEAM()
    update_attributes_from_settings_dictionary(aSTEAM_2, settings_dictionary)

    if software == 'PSPICE':
        aSTEAM_2.settings.local_PSPICE_folder = local_folder
    elif software == 'XYCE':
        aSTEAM_2.settings.local_XYCE_folder = local_folder

    #get all signals that are defined in the config file to later include them in the model using a ModifyModelMultipleVariables
    #step, but since the analysis is not supposed to be dependent from a config file, this
    signals_to_include = ['']
    if settings_dictionary['directory_config_files'] != None:
        full_config_file_path , configuration = determine_config_path_and_configuration(directory_config_files =
                                                                              settings_dictionary['directory_config_files'],
                                                                            steam_circuit_type="RCD")
        signals_to_include = get_signal_keys_from_configurations_file(full_config_file_path, configuration = configuration)
    else:
        warnings.warn("no signals from the config file will be included in the model, variables entry will be empty in"
                      " the cir file, causing all signals to be calculated")

    aSTEAM_2.data_analysis.AnalysisStepDefinition = {
        'makeModel_ref': MakeModel(type='MakeModel', model_name='BM', file_model_data='RCD',
                                                                                case_model='circuit', software=software, simulation_name=None, simulation_number=None,
                                                                                flag_build=True, verbose=False, flag_plot_all=False, flag_json=False),
                                                     'modifyModel_probe1': ModifyModelMultipleVariables(
                                                         type='ModifyModelMultipleVariables', model_name='BM',
                                                         variables_to_change=['PostProcess.probe.probe_type'],
                                                         variables_value=[['CSDF']], software=software,
                                                         simulation_name=None,
                                                         simulation_numbers=[]),

                                                     # Here I implement an additional step so that all signals (and only those) are safed in the variables
                                                     'modifyModel_include_config_signals': ModifyModelMultipleVariables(
                                                         type='ModifyModelMultipleVariables', model_name='BM',
                                                         variables_to_change=['PostProcess.probe.variables'],
                                                         variables_value=[[signals_to_include]], software=software,
                                                         simulation_name=None,
                                                         simulation_numbers=[]),

                                                     'runParsimEvent': ParsimEvent(type='ParsimEvent', input_file=input_csv_file,
                                                                                   path_output_event_csv=path_output_parsim_sweep_RCD_csv, path_output_viewer_csv=None,
                                                                                   simulation_numbers=[file_counter], model_name='BM', case_model='circuit',
                                                                                   simulation_name='RCD', software=software, t_PC_off=None, rel_quench_heater_trip_threshold=None,
                                                                                   current_polarities_CLIQ=[], dict_QH_circuits_to_QH_strips={},
                                                                                   default_keys=DefaultParsimEventKeys(local_LEDET_folder=None, path_config_file=None,
                                                                                                                       default_configs=[], path_tdms_files=None,
                                                                                                                       path_output_measurement_files=None,
                                                                                                                       path_output=local_folder),
                                                                                   path_postmortem_offline_data_folder = settings_dictionary['path_postmortem_offline_data_folder'],
                                                                                    path_to_configurations_folder = settings_dictionary['directory_config_files'],
                                                                                   filepath_to_temp_viewer_csv = settings_dictionary['filepath_to_temp_viewer_csv']),
    'run_simulation': RunSimulation(type='RunSimulation', software=software, simulation_name='RCD', simulation_numbers=[file_counter])}
    aSTEAM_2.output_path = local_folder
    if software == 'PSPICE':
        aSTEAM_2.data_analysis.PermanentSettings.local_PSPICE_folder = local_folder
    elif software == 'XYCE':
        aSTEAM_2.data_analysis.PermanentSettings.local_XYCE_folder = local_folder
    if flag_run_software == False:
        aSTEAM_2.data_analysis.AnalysisStepSequence = ['makeModel_ref', 'modifyModel_probe1',
                                                       'modifyModel_include_config_signals', 'runParsimEvent']
    else:
        aSTEAM_2.data_analysis.AnalysisStepSequence = ['makeModel_ref', 'modifyModel_probe1',
                                                       'modifyModel_include_config_signals', 'runParsimEvent',
                                                       'run_simulation']

    if input_csv_file.endswith('.csv'):
        # outputfile_1 = os.path.join(os.getcwd(), 'output', 'run_parsim_event_circuit',
        #                             f'TestFile_AnalysisSTEAM_run_parsim_event_circuit_RCO_{file_counter}.yaml')
        # outputfile_2 = os.path.join(os.getcwd(), 'output', 'run_parsim_event_circuit',
        #                             f'TestFile_AnalysisSTEAM_run_parsim_event_circuit_RCD_{file_counter}.yaml')

        yaml_file_name_RCO = f'infile_RCO_{unique_identifier_event}.yaml'
        yaml_file_name_RCD = f'infile_RCD_{unique_identifier_event}.yaml'
        path_output_yaml_file_RCO = os.path.join(output_directory_yaml_files, yaml_file_name_RCO)
        path_output_yaml_file_RCD = os.path.join(output_directory_yaml_files, yaml_file_name_RCD)

        if software == 'PSPICE':
            list_output_file = [
                os.path.join(aSTEAM_1.settings.local_PSPICE_folder, 'RCO', f'{file_counter}', 'RCO.cir'),
                os.path.join(aSTEAM_2.settings.local_PSPICE_folder, 'RCD', f'{file_counter}', 'RCD.cir')]

        elif software == 'XYCE':
            list_output_file = [
                os.path.join(aSTEAM_1.settings.local_XYCE_folder, 'RCO', f'{file_counter}', 'RCO.cir'),
                os.path.join(aSTEAM_2.settings.local_XYCE_folder, 'RCD', f'{file_counter}', 'RCD.cir')]

        if os.path.exists(yaml_file_name_RCO): os.remove(yaml_file_name_RCO)
        if os.path.exists(yaml_file_name_RCD): os.remove(yaml_file_name_RCD)
        for file in list_output_file:
            if os.path.exists(file): os.remove(file)

        # act
        aSTEAM_1.write_analysis_file(path_output_file=path_output_yaml_file_RCO)
        aSTEAM_2.write_analysis_file(path_output_file=path_output_yaml_file_RCD)

        aSTEAM_1.run_analysis()
        aSTEAM_2.run_analysis()

        # copy the eventfile to the local PSPICE Folder:
        if software == 'PSPICE':
            shutil.copyfile(input_csv_file,os.path.join(aSTEAM_1.settings.local_PSPICE_folder, 'RCO', f'{file_counter}',f'Eventfile_{unique_identifier_event}.csv'))
            shutil.copyfile(input_csv_file,os.path.join(aSTEAM_2.settings.local_PSPICE_folder, 'RCD', f'{file_counter}',f'Eventfile_{unique_identifier_event}.csv'))
        elif software == 'XYCE':
            shutil.copyfile(input_csv_file, os.path.join(aSTEAM_1.settings.local_XYCE_folder, 'RCO', f'{file_counter}',f'Eventfile_{unique_identifier_event}.csv'))
            shutil.copyfile(input_csv_file,os.path.join(aSTEAM_2.settings.local_XYCE_folder, 'RCD', f'{file_counter}',f'Eventfile_{unique_identifier_event}.csv'))