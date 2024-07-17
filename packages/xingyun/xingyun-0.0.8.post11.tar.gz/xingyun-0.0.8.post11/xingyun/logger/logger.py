from xingyun.time.my_clock import my_clock
import time
from typing import Callable, List, Any

class Logger:
	'''This is a class to make easy log.'''

	def __init__(self , 
			targets: List[Callable[[str], Any]] = [print] , 
			preprocesses: List[Callable[[str], str]] = [
				lambda s: ("[ %.2fs ] " % my_clock()) + s
			], 
		):
		'''The intialization function class `Logger`.
	
        ### Parameters
            - targets: List of callable objects. Each `log()` will call each target once.
            - prefix: will be called and add to the start of each line. Default to current time.
            - postfix: will be called and add to the end of each line.	
        '''

		self.targets  	 = targets
		self.preprocesses  = preprocesses

	def log(self , content: Any = ""):
		content = str(content)

		content = self.apply_preprocess(content)
		for tar in self.targets:
			tar(content)

	def log_separator(self , num: int = 50 , char: str = "-"):
		'''out put `num` times `char`.
		'''
		self.log(char * num)

	def apply_preprocess(self , content):

		for p in self.preprocesses:
			content = p(content)

		return content
	
