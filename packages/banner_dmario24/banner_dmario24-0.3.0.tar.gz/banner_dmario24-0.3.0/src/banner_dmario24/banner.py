from pyfiglet import Figlet

def show():
    f = Figlet(font='slant')
    print(f.renderText('dMari24'))

def pic():
    p = """
               %=**++*##%@@
               @=***++*@@
    """
    print(p)

def lotto():
    import random
    l = random.sample(range(1,46), 6)
    print(l)



