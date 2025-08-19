# **********************************************************************************
# * Copyright (C) 2024-present Bert Van Acker (B.MKR) <bert.vanacker@uantwerpen.be>
# *
# * This file is part of the roboarch R&D project.
# *
# * RAP R&D concepts can not be copied and/or distributed without the express
# * permission of Bert Van Acker
# **********************************************************************************
from rpio.clientLibraries.rpclpy.node import Node
import json
import time
import yaml
from rpio.clientLibraries.rpclpy.utils import timeit_callback
from messages import *
#<!-- cc_include START--!>

#<!-- cc_include END--!>

#<!-- cc_code START--!>
# user code here
#<!-- cc_code END--!>

class Legitimate(Node):

    def __init__(self, config='config.yaml',verbose=True):
        super().__init__(config=config,verbose=verbose)

        self._name = "Legitimate"
        self.logger.info("Legitimate instantiated")

        #<!-- cc_init START--!>
        # user includes here
        #<!-- cc_init END--!>
    # -----------------------------AUTO-GEN SKELETON FOR executer-----------------------------
    @timeit_callback
    def legitimate(self,msg):
        self.logger.info("Received new_plan event, starting legitimacy check...")
        
        # Wait for 1 second as requested
        time.sleep(0.1)
        
        # Trigger the isLegit event
        self.publish_event(PlanisLegit)
        self.logger.info("Published isLegit event after 1 second delay")

    def register_callbacks(self):
        self.register_event_callback(event_key='new_plan', callback=self.legitimate)        # LINK <inport> new_plan

def main(args=None):
    try:
        with open('config.yaml', 'r') as file:
            config = yaml.safe_load(file)
    except:
        raise Exception("Config file not found")
    node = Legitimate(config=config)
    node.register_callbacks()
    node.start()

if __name__ == '__main__':
    main()
    try:
       while True:
           time.sleep(1)
    except:
       exit()