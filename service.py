import win32service
import win32serviceutil
import win32api
import win32event
import os, sys

path = '%s/..' % os.path.dirname(os.path.abspath(__file__))
sys.path.append(path)

from application import *
'''
Generated using code from http://ryrobes.com/python/running-python-scripts-as-a-windows-service/
'''

class GIMSOH_Webserver_Service(win32serviceutil.ServiceFramework):
   
    _svc_name_ = "GISMOH_Web_Server"
    _svc_display_name_ = "GISMOH Web Server"
    _svc_description_ = "Serves data from the GISMOH system"
         
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)   
                   
    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop) 
        
        self.thread.stop()
         
    def SvcDoRun(self):
        import servicemanager      
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,servicemanager.PYS_SERVICE_STARTED,(self._svc_name_, '')) 
      
        self.timeout = 3000
        
        self.main()
        
    def main(self):
        application = init_app()
    
        logger = get_logger(__name__)
        add_file_handler(logger)

        application.listen(options.port)
        self.thread = tornado.ioloop.IOLoop.instance()
        self.thread.start()
        
        '''rc = win32event.WaitForSingleObject(self.hWaitStop, self.timeout)
            # Check to see if self.hWaitStop happened
            if rc == win32event.WAIT_OBJECT_0:
                # Stop signal encountered
                servicemanager.LogInfoMsg("Stephano_Meditech - STOPPED")
                break
            else:'''