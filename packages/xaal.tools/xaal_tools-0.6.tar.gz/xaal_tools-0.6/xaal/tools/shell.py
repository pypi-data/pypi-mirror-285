from xaal.lib import AsyncEngine, helpers
import IPython
from IPython.lib import backgroundjobs
import logging

# imported modules for convenient use in the shell
from xaal.lib import tools
from xaal.schemas import devices
from pprint import pprint


def main():
    helpers.setup_console_logger(logging.WARNING)
    #logging.getLogger("blib2to3").setLevel(logging.WARNING)
    #logging.getLogger("parso").setLevel(logging.WARNING)

    eng = AsyncEngine()
    eng.start()
    
    jobs = backgroundjobs.BackgroundJobManager()
    jobs.new(eng.run)

    IPython.embed(banner1="==============================  xAAL Shell ==============================",
                  banner2=f"* AsyncEngine running in background:\n* eng = {eng}\n\n",
                  colors="Linux",
                  confirm_exit = False,
                  separate_in = '',
                  autoawait = True)
    
    print("* Ending Engine")
    eng.watchdog_event.set()
    print("* Bye bye")

if __name__ == '__main__':
    main()
