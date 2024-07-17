import time

_starttime = time.time()

def my_clock():
	'''call time.time() to see current running time. 
	This is more accurate than time.clock().
	
	XXX really?
	'''
	return time.time() - _starttime
