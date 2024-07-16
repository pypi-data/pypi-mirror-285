# banner_s00zzang

## **Usage**
안뇽.. Pyfiglet 사용법에 대해 알려줄게..~

도움이 필요하다면 --help를 사용하면 돼.
아마.. -f를 이용해 폰트를 바꾸는 것만 할 것 같긴 해......

### Pyfiglet 사용법 :

```py
from pyfiglet import Figlet
f = Figlet(font='slant')
print(f.renderText('ㅠ'))
```

사용하고 싶은 폰트가 있으면 커맨드 라인에다가
`pyfiglet -L <font file>`
사용하면 돼..
만일 안 된다면.. 
`sudo pyfiglet -L <font file>`
를 사용하도록...

## show-pic :
```
    [][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][]
    []                                                            []
    []  [][][][][][][][][][][][][][][][][][][][][][][][][][][][]  []
    []  []                                                    []  []
    []  []                                     iiii           []  []
    []  []     ooo       aaaaa    ssssss      iiii  ssssss    []  []
    []  []    ooooo     aa   aa  sss   sss         sss   sss  []  []
    []  []   oo   oo       aaaa   sss   ss   iiii    sss  ss  []  []
    []  []  oo    oo    aaaaaa      ss      iiii      ss      []  []
    []  []  oo    oo   aa   aa       ss     iiii       ss     []  []
    []  []  oo   oo   aa    aa  ss    sss  iiii   ss    sss   []  []
    []  []   oo oo    aa    aa   sss sss   iiii    sss sss    []  []
    []  []    ooo       aaaaaaa   sssss   iiii      sssss     []  []
    []  []                                                    []  []
    []  [][][][][][][][][][][][][][][][][][][][][][][][][][][][]  []
    []                                                            []
    [][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][]
```
이건 말이죠~
```py
def pic():
	p = """
	(해당 이미지)
	"""

print(p)
```

## show-lotto : 
```
[23, 14, 26, 13, 18, 36]
```
이거는~~
```py
def lotto():
	import random
	l = random.sample(range(1,46),6)
	print(l)
```

장미꽃 한송이 놓고 갑니다..
@>---------

