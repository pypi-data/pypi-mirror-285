# banner_s00zzang

## **Usage**
안뇽.. Pyfiglet 사용법에 대해 알려줄게..~

도움이 필요하다면 --help를 사용하면 돼.
아마.. -f를 이용해 폰트를 바꾸는 것만 할 것 같긴 해......

### Pyfiglet is also a library that can be used in python code:

```py
from pyfiglet import Figlet
f = Figlet(font='slant')
print(f.renderText('text to render'))
```

아니면..

```py
import pyfiglet
f = pyfiglet.figlet_format("text to render", font="slant")
print(f)
```

사용하고 싶은 폰트가 있으면 커맨드 라인에다가
`pyfiglet -L <font file>`
사용하면 돼..
만일 안 된다면.. 
`sudo pyfiglet -L <font file>`
를 사용하도록...

행집욕부~
