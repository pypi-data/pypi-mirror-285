# **pyfiglet**

```
    __                ____ ___  _______
   / /_  __  ______  / __ \__ \<  / __ \
  / __ \/ / / / __ \/ / / /_/ // / /_/ /
 / / / / /_/ / / / / /_/ / __// /\__, /
/_/ /_/\__,_/_/ /_/\____/____/_//____/

```
## **개요**
show-banner 사용하기
## **가이드**
- **1.** 나의 프로젝트 디렉토리에 파일 생성,
프로젝트 디렉토리에 파일 생성 경로
vi src/banner_hun0219/banner.py
```py
from pyfiglet import Figlet

def show():
    f = Figlet(font='slant')
    print(f.renderText('hun0219'))    
```
- **2.** pyproject.toml 파일 수정
banner.py 파일이 실행되는 스크립트를 작성한다
```py
[project.scripts]
show-banner='banner_hun0219.banner:show'
        #banner~디렉토리.파일이름:함수이름
```
- **3.** show-banner로 해당 스크립트 로컬에서 실행
```py
- pyproject.toml파일을 읽고 파일에 정의된 의존성 설치
$ pdm install 
- python 패키지 설치
$ pip install .
- 결과 확인
$ show-banner
    __                ____ ___  _______
   / /_  __  ______  / __ \__ \<  / __ \
  / __ \/ / / / __ \/ / / /_/ // / /_/ /
 / / / / /_/ / / / / /_/ / __// /\__, /
/_/ /_/\__,_/_/ /_/\____/____/_//____/

```
