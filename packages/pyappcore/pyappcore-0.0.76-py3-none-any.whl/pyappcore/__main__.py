#------------------------------------------------------------------------
# 참조 모듈 목록.
#------------------------------------------------------------------------
from __future__ import annotations
from typing import Any, Final, Optional, Type, TypeVar, Union
import builtins
import os
from dotenv import load_dotenv


#------------------------------------------------------------------------
# 파일 진입점.
#------------------------------------------------------------------------
if __name__ == "__main__":
	load_dotenv(dotenv_path = ".env", override = True)
	version = os.getenv("VERSION")
	builtins.print(f"pyappcore: {version}")
	pass