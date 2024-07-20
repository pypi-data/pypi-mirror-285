# pyappcore

## 개요

파이썬 기반의 앱 프레임워크 패키지.


## 설치방법

    python pip install pyappcore


## 개발 환경 및 사용 환경

    OS: Windows 11 Pro  
    Python: 3.12.4 (64-Bit)   
    IDE: Visual Studio Code   


## 사용한 외부 패키지

    setuptools   
    wheel   
    twine   
    debugpy  
    python-dotenv   


## 패키지 설치시 선행 설치가 필요한 의존성 패키지.

    pyinstaller
    debugpy


## 추가 명령어

**프로젝트 생성:**   

    pyappcore create --type project --path "{project root path based pyappcore}"
    pyappcore create --type project --path "{project root path based pyappcore}"


**애플리케이션 빌드: (작업 예정)**   

    pyappcore build --type app --srcpath "{project root path based pyappcore}"


**휠 라이브러리 빌드: (작업 예정)**   

    pyappcore build --type wheel --srcpath "{project root path based pyappcore}"