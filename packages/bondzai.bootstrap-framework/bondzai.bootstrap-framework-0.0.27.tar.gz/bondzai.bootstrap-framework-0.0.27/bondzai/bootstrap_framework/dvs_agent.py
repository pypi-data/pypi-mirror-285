import traceback
import numpy as np

from bondzai.davinsy_py.davinsy import  alloc_mms_ring, dump_dbm_raw_data

from .dvs_config import DvsConfig
from .logger import logger
from .dvs_com import DvsCom
from .file_handler import read_binary


class DvsAgent:
    """
    Agent object, represent the direct interface to DavinSy
    """
    def __init__(self, config: DvsConfig = None,link: DvsCom = None, data_path = None):
        """
        Load agent for its config
        Args:
            config: Config object
            dataset: Dataset object
        """

        logger.debug("Agent init")

        # Load from config
        if config is None:
            self.config = DvsConfig(data_path)
        else:
            self.config = config

        # Manage communication protocol
        self.link = link

        # Define default values
        self.consistentDataChecker = None
        self.vm = []
        self.mode = None
        self.preproc = {}
        self.signalConditionning = {}  # TODO : load graph
        
        self.rawDataMaxSize = 0
        self.vmTable = None
        self.datTable = None
        self.ctxTable = None
        self.uids = None

        self.source_mem = {} # will contain the adress for the source buffer (static mode)
        self.lifecycle = -1


    def pre_boot(self,ini_path: None):
        boot_config = self.config.load_agent_ini(ini_path)

        davinsy_ini_content = {}
        if "davinsy" in boot_config:
            davinsy_ini = boot_config["davinsy"]
            for key in davinsy_ini :
                # filter key if necessary
                val = davinsy_ini[key]
                davinsy_ini_content[key]=val

        if "gateway" in boot_config:
            gateway_ini = boot_config["gateway"]
            for key in gateway_ini :
                # filter key if necessary
                val = gateway_ini[key]
                davinsy_ini_content[key]=val

        if "agent" in boot_config:
            agent_ini = boot_config["agent"]
            if "id" in agent_ini:
                agid = agent_ini["id"]
                self.config.set_agent_id(agid)
            if "reload_raw_data" in agent_ini:
                if agent_ini["reload_raw_data"] == "1":
                    self.config.enable_reload_raw_data()
            if "self_test" in agent_ini:
                if agent_ini["self_test"] == "1":
                    self.config.enable_selftest()
            if "self_test_kill" in agent_ini:
                if agent_ini["self_test_kill"] == "1":
                    self.config.config_selftest({"kill_agent_after_test":1})

        self.config.save_davinsy_ini(davinsy_ini_content)


    def set_data_path(self,data_path):
        self.config.set_data_path(data_path)

    def get_data_path(self):
        return self.config.get_data_path()

    def set_max_nb_raw_data (self,max_nb_raw_data:int):
        if self.lifecycle != -1:
            raise Exception(" Max Number of raw data in DavinSy Database must be changed earlier in the boot steps ")
        self.config.set_max_nb_raw_data(max_nb_raw_data)

    def set_agent_id(self,agent_id):
        self.config.set_agent_id(agent_id)


    def enable_reload_raw_data(self):
        self.config.enable_reload_raw_data()

    def disable_reload_raw_data(self):
        self.config.disable_reload_raw_data()

    def init_and_load(self):
        """
        Init memory and prepare data structure for agent
        """
        self.lifecycle = self.link.get_life_cycle()

        logger.info(f"Device lifecycle: {self.lifecycle}")

        # back-up internal dataset in json after each train
        self.link.on_preproc_batch_done(self.backup_dataset)

        vms = self.config.preload_vms()

        bootstrap_info_list = self.config.get_bootstrap_info_list()

        isConsistent = all([self.check_vm_consistency(vm) for vm in self.vm])
        if not isConsistent:
            return
        if self.lifecycle == 1:
            logger.info("Device not initialized, initializing...")

            rowsize = 0
            for vm in vms:
                rowsize = max(rowsize, vm.get_vm_row_size())

            # create the VM table here 
            logger.debug(f"create_vm_table {rowsize}, {len(vms)} vms")
            self.vmTable = self.link.create_vm_table(rowsize,len(vms))
            
            uids = self.link.get_uids()
            
            #logger.debug(f"VM UID {uids}")
            # add to config ?
            logger.debug("import_virtual_model")
            for vm in vms:
                vm.set_uid2id(uids)
                row,preproc = self.link.import_virtual_model(vm,self.vmTable)
                # add to config
                self.preproc.update(preproc)

            for vm in vms:
                if vm.model["deeplomath"]["nbInstances"] == 0:
                    vm_name = vm.get_name() 
                    if vm_name in bootstrap_info_list :
                        info = bootstrap_info_list[vm_name]
                        if "source" in info:
                            # keep this preprocess for the initial dataset (data-conditionning)
                            self.signalConditionning[info["source"]["id"]] = self.config.get_bootstrap_dataconditionning(self.preproc[vm_name])

            max_raw_data = self.config.get_max_raw_data()
            if (max_raw_data<1):
                raise Exception("Max Raw Data Length (for DavinSy internal storage) not defined")
            max_label = self.config.get_max_labels()
            max_reg_len = self.config.get_max_reg_len()
            if (max_label<1 and max_reg_len < 1):
                raise Exception("Labels and regression size not defined")
            max_nb_raw_data = self.config.get_max_nb_raw_data()
            if (max_nb_raw_data < 1):
                raise Exception("Max Raw Data Length (for DavinSy internal storage) not defined")

            if (max_nb_raw_data*max_raw_data >  self.config.get_max_dbm_raw_data()):
                max_nb_raw_data = int(self.config.get_max_dbm_raw_data()/max_raw_data)
                self.config.set_max_nb_raw_data(max_nb_raw_data)
                logger.warning(f"create_dbm_table limiting : {max_nb_raw_data} elements in DavinSy internal storage")

            logger.debug(f"create_dbm_table max rawdata len: {max_raw_data}, {max_nb_raw_data} elements, with {max_label} label(s) or {max_reg_len} regression vector length")
            self.datTable = self.link.create_dbm_table(max_raw_data,
                                                       max_label,
                                                       max_reg_len,
                                                       max_nb_raw_data
                                                       )
            logger.debug("create_ctx_table")

            self.ctxTable = self.link.create_ctx_table(self.config.get_max_models())

            # create special row for correction
            # Row(self.datTable, -1, "lastin")

    def register_custom_ops_in_agent(self,custom_ops):
        for op in custom_ops:
            self.config.register_external_ops(op,custom_ops[op])

    def load_initial_data(self):
        """
        Load all data from a given dataset
        Args:
        """
        dataset_definition = None
        sourcekey = ""
        ack = 0

        if self.config.reload_raw_data:
            # try with the json file first
            raw_data = self.config.load_raw_data_from_json()
            if len(raw_data) >0:
                for data in raw_data:
                    valid_data = False
                    if "label" in data:
                        is_classification = True
                        if "record" in data:
                            valid_data = True
                            sigVect = data["record"]
    
                        try :
                            sourceid = data["label"]["labels"][0]["source_id"]
                        except Exception as e:
                            valid_data = False
                            logger.warn("Invalid source in raw data")

                        try :
                            groundthruth_for_davinsy = []
                            for lbl in data["label"]["labels"]:
                                groundthruth_for_davinsy.append(lbl["output_id"]) # a.k.a type
                                groundthruth_for_davinsy.append(lbl["label"])
                        except Exception as e:
                            valid_data = False
                            logger.warn("Invalid ground truth in raw data")

                    if valid_data:
                        isLoaded = self.load_one_raw_data(is_classification,inputVect=sigVect, expectedOutput=groundthruth_for_davinsy,source_id=sourceid)
                        ack += int(isLoaded)

                    if ack >= (self.config.get_max_nb_raw_data()-1):
                        logger.warn("DavinSy Internal Storage for raw data might be full")
                        break
                logger.info(f"Re-Loading {ack} raw data")
                return ack

        dataset_list = self.config.get_targz_file_list()

        dataset_list2 = self.config.get_folder_file_list()
        dataset_list += dataset_list2

        cnt_dataset = 0
        for dataset_path in dataset_list:
            sourceid = -1
            valid_file = False

            is_tar = False
            dataset_tar_path = None
            if dataset_path.is_file():
                is_tar = True
                dataset_tar_path = dataset_path

            if is_tar:
                try:
                    logger.debug(f"PRELOAD Initial Dataset {cnt_dataset+1}: {dataset_tar_path.name}")
                    my_tar = self.config.preload_targz(dataset_tar_path)
                    if my_tar.tar:
                        valid_file = True
                except Exception as e:
                    logger.warning(f"Trying to load dataset: {dataset_tar_path.name}, invalide file")
            else:
                valid_file = True

            if valid_file:

                if is_tar:
                    dataset_definition = self.config.load_initial_dataset_definition_targz(my_tar)
                else:
                    dataset_definition = self.config.load_initial_dataset_definition(dataset_path)

                if dataset_definition:
                    cnt_dataset +=1
                    logger.info(f"Loading Initial Dataset {cnt_dataset}: {dataset_path.name}")

                    outputs_definition = dataset_definition["outputs"]
                    dataset = dataset_definition["dataset"]

                    for my_data in dataset:
                        filename = my_data["data"]
                        output = my_data["output"]

                        valid_input = True
                        valid_output = True

                        is_classification = True
                        if "source_id" in my_data:
                            sourcekey = my_data["source_id"]
                            sourceid_new = self.config.get_item_id("sources", my_data["source_id"])
                            if not sourceid_new:
                                sourceid_new = my_data["source_id"]
                                logger.warn(f" Can not find source name for source ID {sourceid_new} during bootstrap")
                        else: 
                            # sourceid = 1
                            logger.warn(f"issue during loading file {filename}, no source")
                            break
                        
                        if sourceid != -1 and sourceid !=sourceid_new:
                            logger.warn(f"multiple sources in a single dataset, ids {sourceid} and {sourceid_new}")

                        sourceid = sourceid_new

                        bootstrap_info = self.config.get_bootstrap_info_from_sourceid(sourceid)
                        if bootstrap_info == {}: # empty dict
                            logger.warn(f"Unable to find bootstrap info for source id {sourceid}")
                            break

                        groundthruth_for_davinsy = []
                        for labeltype in output:
                            # TODO- check if we need to manage the two cases
                            label_type_id = self.config.get_item_id("labels", labeltype)
                            if not label_type_id:
                                label_type_id = outputs_definition[labeltype].get("id", None)
                            if label_type_id is None:
                                logger.warn(f"Unable to find label type id for label type {labeltype}")
                                valid_output = False
                                break

                            label_value = output[labeltype]

                            if label_value == "unknown" : # reserved value for garbage
                                groundthruth_for_davinsy.append(label_type_id)
                                groundthruth_for_davinsy.append(0)
                            elif label_value in outputs_definition[labeltype]:
                                label_value_id = outputs_definition[labeltype].get(label_value, None)

                                if label_value_id is None:
                                    logger.warn(f"Unable to find label value id for {label_value}")
                                    valid_output = False
                                    break
                                groundthruth_for_davinsy.append(label_type_id)
                                groundthruth_for_davinsy.append(label_value_id)
                            else: # manage regression here
                                # only one vector supported for regression
                                groundthruth_for_davinsy = label_value
                                is_classification = False
                        
                        if valid_input and valid_output:
                            if is_tar:
                                raw_input = self.config.load_data_from_dataset_targz(my_tar,filename)
                            else:
                                raw_input = read_binary(dataset_path / filename)

                            if raw_input is None:
                                logger.warn(f"issue during loading file {filename}")

                            # MANAGE frame & hop len
                            if not "source" in bootstrap_info:
                                logger.error(f"Issue with Bootstrap {bootstrap_info}, missing source information")
                                break

                            frame_len = bootstrap_info["source"].get("frame_len",0)
                            file_hop_len = bootstrap_info["source"].get("file_hop_len",0)

                            if frame_len == 0 or frame_len >= len(raw_input):
                                sigVect = self.compute_raw_data(sourceid,data=raw_input)
                                if len(sigVect) < 1:
                                    raise Exception(f"Unable to process data len  {str(len(raw_input))}")
                                isLoaded = self.load_one_raw_data(is_classification,inputVect=sigVect, expectedOutput=groundthruth_for_davinsy,source_id=sourceid)

                                ack += int(isLoaded)

                                if ack >= (self.config.get_max_nb_raw_data()-1):
                                    logger.warn("DavinSy Internal Storage for raw data might be full")
                                    break
                            elif file_hop_len == 0 :
                                raw_input = raw_input[-frame_len:] # remove first sample
                                sigVect = self.compute_raw_data(sourceid,data=raw_input)
                                if len(sigVect) < 1:
                                    raise Exception(f"Unable to process data len  {str(len(raw_input))}")

                                isLoaded = self.load_one_raw_data(is_classification,inputVect=sigVect, expectedOutput=groundthruth_for_davinsy,source_id=sourceid)

                                ack += int(isLoaded)

                                if ack >= (self.config.get_max_nb_raw_data()-1):
                                    logger.warn("DavinSy Internal Storage for raw data might be full")
                                    break
                            else: # frames with over-lap
                                raw_input_rest = raw_input
                                while len(raw_input_rest) >= frame_len:
                                    current_raw_input = raw_input_rest[:frame_len]
                                    sigVect = self.compute_raw_data(sourceid,data=current_raw_input)
                                    if len(sigVect) < 1:
                                        raise Exception(f"Unable to process data len  {str(len(current_raw_input))}")

                                    isLoaded = self.load_one_raw_data(is_classification,inputVect=sigVect, expectedOutput=groundthruth_for_davinsy,source_id=sourceid)

                                    ack += int(isLoaded)

                                    if ack >= (self.config.get_max_nb_raw_data()-1):
                                        logger.warn("DavinSy Internal Storage for raw data might be full")
                                        break

                                    raw_input_rest = raw_input_rest[file_hop_len:]
                    logger.info(f"Loading {ack} data for source {sourcekey} id {sourceid}")

                else:
                    logger.debug("INITIAL DATASET HAVE NO DEFINITION")

                if is_tar:
                    self.config.close_targz(my_tar)

        # CHECK LOAD DATA
        self.backup_dataset()

        return ack
    
    def backup_dataset(self):
        try :
            raw_data = dump_dbm_raw_data()
            if not self.config.save_raw_data_to_json(raw_data=raw_data):
                return -1
            return 0
        except Exception as e:
            logger.error(f"backup_dataset fails because {e}")
        return -1
    
    def compute_raw_data(self, sourceid,data: np.ndarray) -> list:
        """
        Compute signature for a given vector
        Args:
            data: input raw data as list
        Returns:
            processedData: signature vector
        """
        if not sourceid in self.signalConditionning:
            return data
        return self.signalConditionning[sourceid].compute_signature(data)
    

    def load_one_raw_data(self, is_classification,inputVect: list, expectedOutput: list,source_id:int) -> bool:
        """
        Load one data in DavinSy database
        Args:
            inputVect: pre-processed input vector
            expectedOutput: expected output list
        Returns:
            isLoaded: True if data is correctly loaded, else False

        """

        isLoaded = False    
        inputVect = np.array(inputVect, dtype='float32')
        if (len(inputVect) > self.config.get_max_raw_data()):
            raise Exception(f" raw data length {len(inputVect)} higher that expected max raw data {self.config.get_max_raw_data()}")
            # return isLoaded
        try:
            #isLoaded = self.link.import_one_record(self.mode, self.datTable, inputVect, expectedOutput)
            if is_classification:
                expectedOutputVect = np.array(expectedOutput, dtype='int32')
                isLoaded = self.link.import_one_raw_data_classification(self.datTable, inputVect, expectedOutputVect,source_id)
            else:
                expectedOutputVect = np.array(expectedOutput, dtype='float32')
                isLoaded = self.link.import_one_raw_data_regression(self.datTable, inputVect, expectedOutputVect,source_id)

        except Exception as e:
            logger.error("INVALID GT:" + str(expectedOutput) +" DATA LEN "+str(len(inputVect)) + " err: " + str(e))
        return isLoaded
    
    def configure_agent_id(self):
        agent_id = self.config.get_agent_id()
        status = self.link.set_agent_id_in_bld(agent_id)
        
        agent_id_checked = self.link.get_agent_id_from_bld()
        if agent_id_checked != agent_id:
            raise Exception(f" Agent Id not correcly setted {agent_id_checked} instead of {agent_id}")
        logger.info(f" agent identifier {agent_id_checked}")
    def update_tables(self):
        #self.link.get_all_tables()
        return
    