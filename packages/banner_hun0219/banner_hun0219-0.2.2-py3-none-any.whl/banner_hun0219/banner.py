from pyfiglet import Figlet

def show():
    f = pyfiglet.figlet_format(readme = "README.md", font='slant')
    print(f)
