#========================================================================================================================================
# CyborgAI CC BY-NC-ND 4.0 Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 Internation	https://github.com/cyborg-ai-git # 
#========================================================================================================================================

from enum import IntEnum
class EnumApiAction(IntEnum):
	NONE = 0
	ERROR = 1
	PROGRESS = 2
	PROGRESS_UPLOAD = 3
	PROGRESS_DOWNLOAD = 4
	PARTIAL = 5
	COMPLETE = 6