from time import sleep, time
import threading
import re
import json
from .logger import Logger
import traceback
from datetime import datetime

log= Logger("snwatcher")


class SnWatcher():
    '''
    Cada instancia de esta clase monitorea la funcion callback() del bridge, con bridge_args como parametros,
    Si la respuesta contiene el bridge_pattern se dispara el evento con event_params que se le agrega "data": respuesta

    Consideraciones importantes de la funcion check:
        1. Debe recibir como parametros los mismo elementos del dict bridge_args de enter()
        2. Debe retornar un diccionario con almenos el elemento data, todo el diccionario retornado
           seran parte del argumento del evento junto a los event_params
        3. Si se repiten los elementos retornados por check() con los events_params mandan los de check()
    una respuesta  hasta que  respuesta, bloqueando
    '''
    def __init__(self, eventManager, event, event_params={}, event_pattern=None):
        self.em=eventManager
        self.event=event
        self.event_params=event_params
        self.event_pattern=event_pattern
        self.stoploop=False
        self.thread=None
        log.debug("SnWatcher created")

    def start(self, callback_obj, callback_function_args={}, mode="loop",period=1):
        '''
        modos validos:
            loop: (default) Se leera permanentenemente hasta el stop, genenrando multiples eventos
            match: Se iterara hasta el primer match, genera 1 evento
            noloop: Termina despues de la primera llamada, puede no generar evento alguno
        '''
        log.debug("SnWatcher.start")
        if self.thread == None or not self.thread.is_alive():
            self.stoploop=False
            try:
                #log.debug("SnWatcher.run Thread create")
                self.thread=threading.Thread(target=SnWatcher._loop_callback, args=(self,[callback_obj,callback_function_args,mode, period]))
                #log.debug("SnWatcher.run Thread to start")
                self.thread.start()
                #log.debug("SnWatcher.run Thread to started")
                return True
            except Exception as e:
                log.error(e)
                log.error(traceback.format_exc())

        log.debug("SnWatcher.run fail")
        return False
        
    def _loop_callback(self, args):
        log.debug("_loop_callback start",args)
        try:
            [callback_obj,callback_function_args,mode, period] = args
            # Pasamos como argumento a la funcion externa un diccionario para los datos
            # que necesite persistir entre llamados
            while not self.stoploop:
                resp=callback_obj.callback(**callback_function_args)
                log.debug("_loop_callback resp",resp)

                # Si la respuesta no es un dict
                # creamos uno con la respuesta como data
                if type(resp) != dict:
                    data=resp
                    resp={"data":data}

                if self.event_pattern == None or re.search(self.event_pattern, resp["data"]) != None:
                    self.em.putEvent(self.event, dict(self.event_params,**resp))
                    log.info("SnWatcher trigger", self.event_params)
                    if mode=="match":
                        log.debug("SnWatcher._check loop exit, match")
                        return

                if mode=="noloop" :
                    log.debug("SnWatcher._check loop exit, noloop")
                    return
                    
                # default mode is loop 
                sleep(period)
            log.debug("SnWatcher._check loop exit, stop")
        except Exception as e:
            log.error(e)
            log.error(traceback.format_exc())
            log.debug("SnWatcher._check loop exit, exception")


    def stop(self, wait_to_finish=False):
        self.stoploop=True
        if wait_to_finish:
            self.thread.join()

 