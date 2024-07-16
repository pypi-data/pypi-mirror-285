from pyfiglet import Figlet

def show():
    f = Figlet(font = 'slant')
    print(f.renderText('I dont know'))

def pic():
    p = """
        .　　　,,　＿
    　　／ 　　　 ｀､
    　 /　　　　　● ╮
    　/ ● 　　 　💧　l
    　l　💧　し　 💧　|
    　l　💧　_＿,,ノ 💧l
    　 ＼💧＿´'￣´_💧/
    . 　 /💧　　￣ 💧 ╮
    　 /　💧　　　💧 .╮
    .　|　　💧　　　　.|

    """
    print(p)

def lotto():
    import random
    # 로또
    lotto = []
    num = random.randint(1,45)

    for i in range(6):
        while num in lotto:
            num = random.randint(1,45)
        lotto.append(num)

    lotto.sort()
    print("로또 번호 : {}".format(lotto))
