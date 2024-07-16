import random ##lotto

def show():
    from pyfiglet import Figlet
    f = Figlet(font='slant')
    print(f.renderText('s00zzang'))

def pic():
    p = """
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

    """
    print(p)

def lotto():
    l = random.sample(range(1,46),6)
    print(l)

    
