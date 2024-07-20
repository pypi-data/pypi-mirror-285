#------------------------------------------------------------------------
# 참조 모듈 목록.
#------------------------------------------------------------------------
import builtins
import os
from setuptools import setup, find_packages
from dotenv import load_dotenv


#------------------------------------------------------------------------
# 환경 변수 목록 파일 로드.
#------------------------------------------------------------------------
load_dotenv(dotenv_path = ".env", override = True)
NAME = os.getenv("NAME")
VERSION = os.getenv("VERSION")
AUTHOR = os.getenv("AUTHOR")
AUTHOR_EMAIL = os.getenv("AUTHOR_EMAIL")
DESCRIPTION = os.getenv("DESCRIPTION")
LONG_DESCRIPTION_CONTENT_TYPE = os.getenv("LONG_DESCRIPTION_CONTENT_TYPE")
URL = os.getenv("URL")
PYTHON_REQUIRES = os.getenv("PYTHON_REQUIRES")
builtins.print(f"pyappcore: {VERSION}")


#------------------------------------------------------------------------
# 패키지 라이브러리 빌드.
#------------------------------------------------------------------------
setup(
	name = NAME,
	version = VERSION,
	author = AUTHOR,
	author_email = AUTHOR_EMAIL,
	description = DESCRIPTION,
	long_description = open(file = "README.md", mode = "r", encoding = "utf-8").read(),
	long_description_content_type = LONG_DESCRIPTION_CONTENT_TYPE,
	url = URL,
	packages = find_packages(),
	include_package_data = True,
	package_data = {
		"": [
			"res/*"
		],
	},
	scripts = [

	],
	entry_points = {
		"console_scripts": [
			"pyappcore=pyappcore.command:Run",
		]
	},
    install_requires = [
		"pyinstaller",
		"debugpy"
	],
	classifiers = [
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	python_requires = PYTHON_REQUIRES
)