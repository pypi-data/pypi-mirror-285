from tlpytools.log import logger
from tlpytools.data import data_tables
from tlpytools.data_store import DataStore
import yaml


class run_yaml:
    """usage: run in order
    - load_yaml
    - load_yaml_data
    - load_yaml_spatials (optional)
    - run_steps
    """

    def load_yaml(self, filename=None):
        """
        read yaml, initialize data objects, and returns yaml file
        """
        if filename == None:
            filename = "{}.yaml".format(type(self).__name__)
        with open(filename) as f:
            s = yaml.load(f, Loader=yaml.SafeLoader)
        if "FILES" in s:
            self.load_yaml_data(s)

        self.s = s
        return self.s

    def load_yaml_data(self, s):
        """load yaml global variables and dataframe, and return them.

        Args:
            s (setting from load_yaml): setting from load_yaml

        Returns:
            s, dfs: setting and dataframe dictionary
        """

        self.data_store = DataStore()

        if "RESUME_AFTER" not in s:
            s["RESUME_AFTER"] = ""

        # if RESUME_AFTER has been set, read from existing files
        if s["RESUME_AFTER"] in list(s["STEPS"]):
            vars_obj, dfs_obj, gdfs_obj = self.data_store.load_existing_data(spec=s)
            if vars_obj != None:
                self.resume_after = s["RESUME_AFTER"]
                for var_name in list(vars_obj.keys()):
                    setattr(self, var_name, vars_obj[var_name])
                self.dfs = dfs_obj
                self.gdfs = gdfs_obj
                return self.dfs, self.gdfs
            else:
                self.resume_after = ""
                print(
                    "CONFIG WARNING - RESUME_AFTER is ignored since there's no valid data files available."
                )

        # otherwise, create new data stores
        if "VARS" in s:
            self.resume_after = ""
            for var in s["VARS"].keys():
                setattr(self, var, s["VARS"][var])
        # read table data
        if "FILES" in s:
            self.dfs = {}
            self.gdfs = {}
            if "INPUTS" in s["FILES"]:
                if s["FILES"]["INPUTS"] is not None:
                    self.dfs = data_tables.read_tbl_data(s)
            # read spatial table data
            if "SPATIALS" in s["FILES"]:
                if s["FILES"]["SPATIALS"] is not None:
                    self.gdfs = data_tables.read_spatial_data(s)
        return self.dfs, self.gdfs

    def run_steps(self, s, log=None):
        """run steps specified in setting s

        Args:
            s (dict): specification from yaml
            log (object): logger object
        """
        # handle no logger
        if log == None:
            log = logger()
            log.init_logger()

        # exclude skipped steps
        if (
            s["RESUME_AFTER"] in list(s["STEPS"])
            and self.resume_after == s["RESUME_AFTER"]
        ):
            skip_step_index = s["STEPS"].index(s["RESUME_AFTER"])
            run_step_list = s["STEPS"][skip_step_index + 1 :]
        else:
            run_step_list = s["STEPS"]

        # perform steps
        for step in run_step_list:
            log.info("===={}====".format(step))
            if step not in s:
                s[step] = None
            # run current step
            eval("self.{}".format(step))(spec=s[step], files=s["FILES"])
            # save data at the end of current step
            vars_obj = {}
            for var_name in list(s["VARS"].keys()):
                vars_obj[var_name] = getattr(self, var_name)
            store_save_status = self.data_store.save_all_data(
                vars_obj=vars_obj,
                dfs_obj=self.dfs,
                gdfs_obj=self.gdfs,
                current_step=step,
                spec=s,
            )
            if store_save_status == True:
                log.info("data store for resume after step {} saved.".format(step))
            log.info("step {} completed.".format(step))

    def export_data_csv(self, spec, files):
        """wrapper function for exporting file outputs as csv;
        self.dfs must contain DataFrame tables for export.

        Args:
            spec (dict): large specification containing the imputation settings, see yaml file under 'impute_hh_income'
            files (dict):  a list of input and output file names
        """
        if "OUTPUTS" in files:
            data_tables.export_csv(dict_df=self.dfs, ofiles=files["OUTPUTS"])
        else:
            raise ValueError("data export called when no export files are specified.")

    def export_data_files(self, spec, files):
        """wrapper function for exporting file outputs as csv;
        self.dfs must contain DataFrame tables for export.

        Args:
            spec (dict): large specification containing the imputation settings, see yaml file under 'impute_hh_income'
            files (dict):  a list of input and output file names
        """
        if "OUTPUTS" in files:
            data_tables.export_data(dict_df=self.dfs, ofiles=files["OUTPUTS"])
        else:
            raise ValueError("data export called when no export files are specified.")

    @staticmethod
    def get_sample_spec():
        """returns a sample data specificationf or config"""
        example_spec = {
            "__COMMENT__": "THIS IS AN AUTOGENERATED YAML FILE example.",
            "FILES": {
                "INPUTS": {
                    "tbl1": "td_2017.tbl1.crypt",
                    "tbl2": "td_2017.tbl2.sqlsvr",
                    "tbl3": "data_files/tbl3.csv",
                },
                "SPATIALS": {
                    "region_taz": "Inputs/ShpFiles/TAZ1700_GY_v7.shp",
                    "external_crossings": "Inputs/ShpFiles/external_crossings.json",
                },
                "INPUT_COLUMNS": {"tbl_blended_skim": ["col1", "col2", "col3"]},
                "OUTPUTS": {
                    "tblOut1": "tblOut1.csv",
                },
            },
            "VARS": {
                "colTAZ": "TAZ",
                "colSubSeed": "SubSeedGeo",
                "colSeed": "SeedGeo",
                "tblCTName": "tblCTMV",
                "tblGeoName": "tblGeo",
                "tblHHWgtName": "tblHHWeights",
                "geoStructure": "A1_9_44",
                "clearMem": True,
            },
            "STEPS": ["example_step1", "export_data_csv"],
            "example_step1": {"test": "test_val"},
        }

        return example_spec
