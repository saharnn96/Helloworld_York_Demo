# **********************************************************************************
# * Copyright (C) 2024-present Bert Van Acker (B.MKR) <bert.vanacker@uantwerpen.be>
# *
# * This file is part of the roboarch R&D project.
# *
# * RAP R&D concepts can not be copied and/or distributed without the express
# * permission of Bert Van Acker
# **********************************************************************************
import json

from rpio.clientLibraries.rpclpy.node import Node
from messages import *
import time
from rpio.clientLibraries.rpclpy.utils import timeit_callback
import yaml
#<!-- cc_include START--!>
# user includes here
#<!-- cc_include END--!>

#<!-- cc_code START--!>
# user code here
#<!-- cc_code END--!>

class Execute(Node):

    def __init__(self, config='config.yaml',verbose=True):
        super().__init__(config=config,verbose=verbose)

        self._name = "Execute"
        self.logger.info("Execute instantiated")
        self.handling_anomaly = HandlingAnomalyData()

        #<!-- cc_init START--!>
        # user includes here
        #<!-- cc_init END--!>

    # -----------------------------AUTO-GEN SKELETON FOR executer-----------------------------
    @timeit_callback
    def executer(self,msg):
        isLegit = self.read_knowledge("isLegit",queueSize=1)
        directions = self.read_knowledge("directions",queueSize=1)
        _Direction = Direction()

        #<!-- cc_code_executer START--!>

        for i in range(3):
            self.logger.info("Executing")
            time.sleep(0.1)
        self.logger.info(f"Executed with directions = {directions}");
        self.publish_event(event_key='/spin_config',message=directions)    # LINK <outport> spin_config
        self.handling_anomaly._anomaly = False
        self.write_knowledge(self.handling_anomaly)
        #<!-- cc_code_executer END--!>

    def register_callbacks(self):
        self.register_event_callback(event_key='new_plan', callback=self.executer)        # LINK <inport> new_plan
        self.register_event_callback(event_key='isLegit', callback=self.executer)        # LINK <inport> isLegit

def main(args=None):
    try:
        with open('config.yaml', 'r') as file:
            config = yaml.safe_load(file)
    except:
        raise Exception("Config file not found")
    node = Execute(config)
    node.register_callbacks()
    node.start()

if __name__ == '__main__':
    main()
    try:
       while True:
           time.sleep(1)
    except:
       exit()