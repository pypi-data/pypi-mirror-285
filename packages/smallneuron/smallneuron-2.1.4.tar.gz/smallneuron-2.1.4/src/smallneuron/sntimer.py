#
# Este modulo es un simple timer, que coloc un evento con paramtros despues de 
# del tiempo indicado
#
import re
import threading
import os.path
import traceback
from .logger import Logger
from time import sleep
from .smallneuron import  EventManager

log=Logger("smallneuron.SnTimer")

    
class SnTimer():
    def __init__(self, eventManager:EventManager):
        self.eventManager = eventManager
        log.info("start")

    def callback(self, time=1.0):
        sleep(time)
        return { "time":time } 

    # Los eventos agregado con timer son por defecto 
    # solo validos para el siguiente estado
    def watchEvent(self, event, event_params={}, time=1.0, valid=1):
        log.debug("putEvent:", event,event_params,time,valid)
        if valid != None:
            event_params["validUntil"] = self.eventManager.count+valid

        return self.eventManager.watchEvent(event=event, event_params=event_params, 
                callback_obj=self, callback_function_args={"time":time},
                mode="noloop")


