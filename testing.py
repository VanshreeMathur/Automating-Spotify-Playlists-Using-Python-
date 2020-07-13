
def cracklepop():
    n = 0

    while n != 99:
        if n % 3 == 0:
            print("Crackle")
            ++n
        elif n % 5 == 0:
            print("Pop")
            ++n
        elif (n % 5 == 0) and (n % 3 == 0):
            print("CracklePop")
            ++n
        elif n == 100:
            break
        else:
            print(n)
            ++n


cracklepop()
