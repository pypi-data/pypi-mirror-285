#!/usr/bin/env python
import math
import os
from autosubmit_api.logger import logger
from autosubmit_api.components.jobs.utils import convert_int_default
from autosubmit_api.config.ymlConfigStrategy import ymlConfigStrategy
from autosubmit_api.config.basicConfig import APIBasicConfig
from autosubmit_api.components.jobs.job_factory import SimJob
from autosubmit_api.config.config_common import AutosubmitConfigResolver
from abc import ABCMeta, abstractmethod
from autosubmit_api.common.utils import JobSection, parse_number_processors, timestamp_to_datetime_format, datechunk_to_year
from typing import List

from autosubmit_api.persistance.experiment import ExperimentPaths

class ProjectType:
  GIT = "git"
  SVN = "svn"

class ConfigurationFacade(metaclass=ABCMeta):
  """

  """

  def __init__(self, expid, basic_config):
    # type: (str, APIBasicConfig) -> None
    self.basic_configuration = basic_config # type: APIBasicConfig
    self.expid = expid # type: str
    self.experiment_path = "" # type: str
    self.pkl_path = "" # type: str
    self.tmp_path = "" # type: str
    self.log_path = "" # type: str
    self.pkl_filename = "" # type: str
    self.structures_path = "" # type: str
    self.chunk_unit = "" # type: str
    self.chunk_size = "" # type: int
    self.current_years_per_sim = 0.0 # type: float
    self.sim_processors = 0  # type: int
    self.experiment_stat_data = None # type: os.stat_result
    self.warnings = [] # type: List[str]
    self._process_basic_config()

  def _process_basic_config(self):
    # type: () -> None
    exp_paths = ExperimentPaths(self.expid)
    self.pkl_filename = os.path.basename(exp_paths.job_list_pkl)
    self.experiment_path = exp_paths.exp_dir
    self.pkl_path = exp_paths.job_list_pkl
    self.tmp_path = exp_paths.tmp_dir
    self.log_path = exp_paths.tmp_log_dir
    self.structures_path = self.basic_configuration.STRUCTURES_DIR
    if not os.path.exists(self.experiment_path): raise IOError("Experiment folder {0} not found".format(self.experiment_path))
    if not os.path.exists(self.pkl_path): raise IOError("Required file {0} not found.".format(self.pkl_path))
    if not os.path.exists(self.tmp_path): raise IOError("Required folder {0} not found.".format(self.tmp_path))

  @abstractmethod
  def _process_advanced_config(self):
    pass

  @abstractmethod
  def get_autosubmit_version(self):
    pass

  @abstractmethod
  def _get_processors_number(self, conf_sim_processors):
    # type: (str) -> int
    pass

  @abstractmethod
  def get_model(self):
    # type: () -> str
    pass

  @abstractmethod
  def get_branch(self):
    # type: () -> str
    pass

  @abstractmethod
  def get_owner_name(self):
    # type: () -> str
    pass

  @abstractmethod
  def get_owner_id(self):
    # type: () -> int
    pass

class BasicConfigurationFacade(ConfigurationFacade):
  """ BasicConfig and paths """
  def __init__(self, expid, basic_config):
    # type: (str, APIBasicConfig) -> None
    super(BasicConfigurationFacade, self).__init__(expid, basic_config)

  def _process_advanced_config(self):
    raise NotImplementedError

  def get_autosubmit_version(self):
    raise NotImplementedError

  def _get_processors_number(self, conf_sim_processors):
    raise NotImplementedError

  def get_model(self):
    raise NotImplementedError

  def get_branch(self):
    raise NotImplementedError

  def get_owner_name(self):
    raise NotImplementedError

  def get_owner_id(self):
    raise NotImplementedError

class AutosubmitConfigurationFacade(ConfigurationFacade):
  """ Provides an interface to the Configuration of the experiment.  """
  def __init__(self, expid, basic_config, autosubmit_config):
    # type: (str, APIBasicConfig, AutosubmitConfigResolver) -> None
    super(AutosubmitConfigurationFacade, self).__init__(expid, basic_config)
    self.autosubmit_conf = autosubmit_config
    self._process_advanced_config()

  def _process_advanced_config(self):
    """ Advanced Configuration from AutosubmitConfig """
    # type: () -> None
    self.autosubmit_conf.reload()
    self.chunk_unit = self.autosubmit_conf.get_chunk_size_unit()
    self.chunk_size = self.autosubmit_conf.get_chunk_size()
    self.current_years_per_sim = datechunk_to_year(self.chunk_unit, self.chunk_size)
    self.sim_processors = self._get_processors_number(self.autosubmit_conf.get_processors(JobSection.SIM))
    
    # Process for yml
    if isinstance(self.autosubmit_conf._configWrapper, ymlConfigStrategy):
      self.sim_tasks = convert_int_default(self.autosubmit_conf._configWrapper.get_tasks(JobSection.SIM))
      self.sim_nodes = convert_int_default(self.autosubmit_conf._configWrapper.get_nodes(JobSection.SIM))
      self.sim_processors_per_node = convert_int_default(self.autosubmit_conf._configWrapper.get_processors_per_node(JobSection.SIM))
      self.sim_exclusive = self.autosubmit_conf._configWrapper.get_exclusive(JobSection.SIM)
    else:
      self.sim_tasks = None
      self.sim_nodes = None
      self.sim_processors_per_node = None
      self.sim_exclusive = False
    
    self.sim_processing_elements = self._calculate_processing_elements()

    self.experiment_stat_data = os.stat(self.experiment_path)

  def get_pkl_last_modified_timestamp(self):
    # type: () -> int
    return int(os.stat(self.pkl_path).st_mtime)

  def get_pkl_last_modified_time_as_datetime(self):
    # type: () -> str
    return timestamp_to_datetime_format(self.get_pkl_last_modified_timestamp())

  def get_experiment_last_access_time_as_datetime(self):
    # type: () -> str
    return timestamp_to_datetime_format(int(self.experiment_stat_data.st_atime))

  def get_experiment_last_modified_time_as_datetime(self):
    # type: () -> str
    return timestamp_to_datetime_format(int(self.experiment_stat_data.st_mtime))

  def get_experiment_created_time_as_datetime(self):
    # type: () -> str
    """ Important: Under OpenSUSE, it returns the last modified time."""
    return timestamp_to_datetime_format(int(self.experiment_stat_data.st_ctime))

  def get_owner_id(self):
    # type: () -> int
    return int(self.experiment_stat_data.st_uid)

  def get_owner_name(self):
    # type: () -> str
    try:
      stdout = os.popen("id -nu {0}".format(str(self.get_owner_id())))
      owner_name = stdout.read().strip()
      return str(owner_name)
    except:
      return "NA"

  def get_autosubmit_version(self):
    # type: () -> str
    return self.autosubmit_conf.get_version()

  def get_main_platform(self):
    return str(self.autosubmit_conf.get_platform())

  def get_section_processors(self, section_name):
    # type: (str) -> int
    return self._get_processors_number(str(self.autosubmit_conf.get_processors(section_name)))

  def get_section_qos(self, section_name):
    return str(self.autosubmit_conf.get_queue(section_name))

  def get_section_platform(self, section_name):
    return str(self.autosubmit_conf.get_job_platform(section_name))

  def get_platform_qos(self, platform_name, number_processors):
    # type: (str, int) -> str
    if number_processors == 1:
      qos = str(self.autosubmit_conf.get_platform_serial_queue(platform_name))
      if len(qos.strip()) > 0:
        return qos
    return str(self.autosubmit_conf.get_platform_queue(platform_name))

  def get_wrapper_qos(self):
    # type: () -> str
    return str(self.autosubmit_conf.get_wrapper_queue())

  def get_wrapper_type(self):
    # type: () -> str | None
    if self.autosubmit_conf.get_wrapper_type() and self.autosubmit_conf.get_wrapper_type().upper() != "NONE":
      return self.autosubmit_conf.get_wrapper_type().upper()
    return None

  def get_section_wallclock(self, section_name):
    return str(self.autosubmit_conf.get_wallclock(section_name))

  def get_platform_max_wallclock(self, platform_name):
    return str(self.autosubmit_conf.get_platform_wallclock(platform_name))

  def get_safety_sleep_time(self):
    # type: () -> int
    return self.autosubmit_conf.get_safetysleeptime()

  def get_project_type(self):
    # type: () -> str
    return self.autosubmit_conf.get_project_type()

  def get_model(self):
    # type: () -> str
    if self.get_project_type() == ProjectType.GIT:
      return self.get_git_project_origin()
    elif self.get_project_type() == ProjectType.SVN:
      return self.get_svn_project_url()
    else:
      return "NA"

  def get_branch(self):
    # type: () -> str
    if self.get_project_type() == ProjectType.GIT:
      return self.get_git_project_branch()
    elif self.get_project_type() == ProjectType.SVN:
      return self.get_svn_project_url()
    else:
      return "NA"

  def get_git_project_origin(self):
    # type: () -> str
    return self.autosubmit_conf.get_git_project_origin()

  def get_git_project_branch(self):
    # type: () -> str
    return self.autosubmit_conf.get_git_project_branch()

  def get_svn_project_url(self):
    # type: () -> str
    return self.autosubmit_conf.get_svn_project_url()

  def update_sim_jobs(self, sim_jobs):
    # type: (List[SimJob]) -> None
    """ Update the jobs with the latest configuration values: Processors, years per sim """
    for job in sim_jobs:
      job.set_ncpus(self.sim_processing_elements)
      job.set_years_per_sim(self.current_years_per_sim)

  def _get_processors_number(self, conf_job_processors):
    # type: (str) -> int
    num_processors = 0
    try:
        if str(conf_job_processors).find(":") >= 0:
            num_processors = parse_number_processors(conf_job_processors)
            self._add_warning("Parallelization parsing | {0} was interpreted as {1} cores.".format(
                conf_job_processors, num_processors))
        else:
            num_processors = int(conf_job_processors)
    except:
        self._add_warning(
            "CHSY Critical | Autosubmit API could not parse the number of processors for the SIM job.")
        pass
    return num_processors

  def _add_warning(self, message):
    # type: (str) -> None
    self.warnings.append(message)

  def _estimate_requested_nodes(self) -> int:
    if self.sim_nodes:
      return self.sim_nodes
    elif self.sim_tasks:
      return math.ceil(self.sim_processors / self.sim_tasks)
    elif self.sim_processors_per_node and self.sim_processors > self.sim_processors_per_node:
      return math.ceil(self.sim_processors / self.sim_processors_per_node)
    else:
      return 1

  def _calculate_processing_elements(self) -> int:
    if self.sim_processors_per_node:
      estimated_nodes = self._estimate_requested_nodes()
      if not self.sim_nodes and not self.sim_exclusive and estimated_nodes <= 1 and self.sim_processors <= self.sim_processors_per_node:
        return self.sim_processors
      return estimated_nodes * self.sim_processors_per_node
    elif self.sim_tasks or self.sim_nodes:
      warn_msg = 'Missing PROCESSORS_PER_NODE. Should be set if TASKS or NODES are defined. The SIM PROCESSORS will used instead.'
      self._add_warning(warn_msg)
      logger.warning(warn_msg)
    return self.sim_processors