def show(text):
    from pyfiglet import Figlet
    f = Figlet(font='slant')
    print(f.renderText(text))

def pic():
    p = """
       .-""""-.        .-""""-.
      /        \      /        \
     /_        _\    /_        _\
    // \      / \\  // \      / \\
    |\__\    /__/|  |\__\    /__/|
     \    ||    /    \    ||    /
      \        /      \        /
       \  __  /        \  __  /
        '.__.'          '.__.'
         |  |            |  |
         |  |            |  |
	"""
    print(p)

def lotto():
    import random
    l = random.sample((range(1,46)),6)
    print(l)
