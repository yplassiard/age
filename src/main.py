# *-* coding: utf-8 *-*

import core
import speech
		
if __name__ == '__main__':
	print("Test")
	try:
		core.main()
	except KeyboardInterrupt:
		speech.terminate()
	except Exception as e:
		print("Uncaught exception: {e}".format(e=e))
		import traceback
		traceback.print_tb(e.__traceback__)
