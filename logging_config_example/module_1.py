def vvod_xoda(n, m, s):
    dct = {1: [0,0], 2:[0, 1], 3:[0,2], 4:[1,0], 5:[1,1], 6:[1,2], 7:[2,0], 8:[2,1], 9:[2,2]}
    if s[dct[n][0]][dct[n][1]] == '.':
        s[dct[n][0]][dct[n][1]] = m
    else:
        print("Клетка занята, выберите другую!")

def win():
    for i in range(q):
        for j in range(q):
            print(f'{s[i][j]}'.ljust(3), end="")
        print()
    exit()

q = 3
ooo = {'x': 'Крестики', 'o': 'Нолики'}
s = [["."]*q for _ in range(q)]

while True:
    for i in range(q):
        for j in range(q):
            print(f'{s[i][j]}'.ljust(3), end="")
        print()

    n = int(input("Введите номер клетки: "))
    m = input("Введите свой знак (x или o): ")

    vvod_xoda(n, m, s)
    try:
        for b in range(q):
            u, uu = [], []
            for v in range(q):
                u.append(s[b][v])
                uu.append(s[v][b])
            a = ''.join(u)
            z = ''.join(uu)

            if a == 'xxx' or a == 'ooo' or z == 'xxx' or z == 'ooo':
                a == z
                print(f'Победили: {ooo[z[0]]}')
                win()

            elif s[0][0] == s[1][1] == s[2][2] and s[0][0] != '.':
                print(f'Победили: {ooo[s[0][0]]}')
                win()

            elif s[0][2] == s[1][1] == s[2][0] and s[0][2] != '.':
                print(f'Победили: {ooo[s[0][2]]}')
                win()

            else:
                d = []
                for i in range(q):
                    for j in range(q):
                        d.append(s[i][j])
                if '.' not in d:
                    print("Ничья!")
                    win()
    except ValueError:
        pass
