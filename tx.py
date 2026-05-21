def mm():
    import random
    b='0123456789'
    c='ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    d=b+c
    a=''.join(random.choice(d) for i in range(6))
    return a

def sj():
    from datetime import datetime
    now=datetime.now()
    e=now.strftime('%Y年%m月%d日 %H:%M;%S')
    return e
