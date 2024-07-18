from evo_framework.core.evo_core_log.utility.ULogger import ULogger
import traceback
class IuLog(object):
    
    @staticmethod
    def doSetLevel(level:str):
        logger = ULogger.getInstance().logger
        logger.setLevel(level)
        
    @staticmethod
    def doVerbose(name, msg, *args, **kwargs):
        logger = ULogger.getInstance().logger
        if logger.level <= 10:
            args_str = ', '.join(str(arg) for arg in args)  
            kwargs_str = ', '.join(f"{k}={v}" for k, v in kwargs.items()) 
            if args and kwargs:
                print(f"\nVERBOSE {name}: {msg} {args_str}; {kwargs_str}")
            elif args: 
                print(f"\nVERBOSE {name}: {msg} {args_str}")
            elif kwargs:  
                print(f"\nVERBOSE {name}: {msg} {kwargs_str}")
            else:  
                print(f"\nVERBOSE {name} {msg}")


    @staticmethod
    def doInfo(name, msg, *args, **kwargs):
        logger = ULogger.getInstance().logger
        logger.name = name
        logger.info(msg, *args, **kwargs)
    
    @staticmethod
    def doDebug(name,msg, *args, **kwargs):
        logger = ULogger.getInstance().logger
        logger.name = name
        logger.debug(msg, *args, **kwargs)
        
    @staticmethod
    def doWarning(name,msg, *args, **kwargs):
        logger = ULogger.getInstance().logger
        logger.name = name
        logger.warning(msg, *args, **kwargs)
        
    @staticmethod
    def doError(name,msg, *args, **kwargs):
        logger = ULogger.getInstance().logger
        logger.name = name
        logger.error(msg, *args, **kwargs)
        
    @staticmethod
    def doFatal(name,msg, *args, **kwargs):
        logger = ULogger.getInstance().logger
        logger.name = name
        logger.fatal(msg, *args, **kwargs)
        
    @staticmethod
    def doException(name,exception:Exception):
        stack_trace_str = traceback.format_exc()
        message = f"Exception:{exception}\n{stack_trace_str}\n"
        logger = ULogger.getInstance().logger
        logger.name = name
        logger.error(message)
        ULogger.getInstance().saveToLog (message)
        