""" The long lasting worker thread as demo - just wait some time and create data periodically
Copyright Nanosurf AG 2021
License - MIT
"""
import time
from dataclasses import dataclass
import numpy as np
from PySide6.QtCore import Signal

import nanosurf as nsf
try:
    from nanosurf.lib.spm.studio.wrapper.cmd_tree_spm import Root, RootLu
except ImportError: 
    pass
import settings

class MeasureResult:
    def __init__(self) -> None:
        self.monitor_stream = nsf.SciStream()
        self.last_index : int = -1
        # add more or different results 

class MeasureTask(nsf.frameworks.qt_app.nsf_thread.SPMWorker):
    """ This class implements the background measurement task using a Nanosurf SPM Controller  """

    """ Parameter for the background work with initial parameters. 
        Should be set to desired values by worker.start_background_task() """
    par_sample_points   = 10
    par_time_per_sample = 2.0
    par_monitor_id      = settings.MonitorChannelID.User1Input

    """ signal emitted from worker task"""
    sig_new_result = Signal() # is emitted each time new data are available . Result is read by self.get_result()

    def __init__(self, module: nsf.frameworks.qt_app.ModuleBase):
        self.module = module
        self.result = MeasureResult()
        super().__init__(module)

    def get_task_result(self) -> MeasureResult:
        return self.result
    
    def init_studio(self):
        self.spm:Root
        self.lu:RootLu
        if self.par_monitor_id == settings.MonitorChannelID.User1Input:
            self.lu_adc_in = self.lu.analog_hi_res_in.user1
        elif self.par_monitor_id == settings.MonitorChannelID.Deflection:
            self.lu_adc_in = self.lu.analog_hi_res_in.deflection
            self.lu_ramp_gen = self.lu.ramp_generator.user1
        else:
            raise ValueError("Unknown monitor channel selected")
    
    def init_spm(self):
        if self.par_monitor_id == settings.MonitorChannelID.User1Input:
            self.lu_adc_in = self.lu.AnalogHiResIn(self.lu.AnalogHiResIn.Instance.USER1)
        elif self.par_monitor_id == settings.MonitorChannelID.Deflection:
            self.lu_adc_in = self.lu.AnalogHiResIn(self.lu.AnalogHiResIn.Instance.DEFLECTION)
            self.lu_ramp_gen = self.lu.RampGenerator(self.lu.RampGenerator.Instance.USER1)
        else:
            raise ValueError("Unknown monitor channel selected")
    
    def do_work(self):
        """ This is the working function for the long task"""
        self.result = MeasureResult()
        if self.connect_to_controller():

            # prepare resulting stream
            self.result.monitor_stream = nsf.SciStream(
                source = np.linspace(0, self.par_sample_points*self.par_time_per_sample, self.par_sample_points, endpoint=False),
                x_unit = "s",
                x_name = "Time"
            )    

            if self.spm.is_studio:
                self.init_studio()
            else:
                self.init_spm()
            
            channel_unit = self.lu_adc_in.attribute.current_input_value.unit
            self.result.monitor_stream.set_channel_name(0, settings.MonitorChannelID(self.par_monitor_id).name)
            self.result.monitor_stream.set_channel_unit(0, channel_unit)

            # measures all samples or a user abort is detected
            for cur_point in range(self.par_sample_points):
                new_value = self.lu_adc_in.attribute.current_input_value.value

                self.result.monitor_stream.channels[0].value[cur_point] = new_value
                self.result.last_index = cur_point
                self.sig_new_result.emit()

                if self.is_stop_request_pending():
                    break
                
                time.sleep(self.par_time_per_sample)    




