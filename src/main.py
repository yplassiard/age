# *-* coding: utf-8 *-*
"""AGE -- AudioGame Engine
Main program
"""

import traceback

import core
import speech


if __name__ == '__main__':
    try:
        core.initialize()
        core.run()
    except KeyboardInterrupt:
        speech.terminate()
    except Exception as ex:
        print("Uncaught exception: {e}".format(e=ex))
        traceback.print_tb(ex.__traceback__)
