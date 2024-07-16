from pyfiglet import Figlet

def show():
    f = Figlet(font='slant')
    print(f.renderText('HaramSs'))


def pic():
    p = """
      .'   `.
         .'.-.`-'.-.`.
    ..._:   .-. .-.   :_...
  .'    '-.(o ) (o ).-'    `.
 :  _    _ _`~(_)~`_ _    _  :
:  /:   ' .-=_   _=-. `   ;\  :
:   :|-.._  '     `  _..-|:   :
 :   `:| |`:-:-.-:-:'| |:'   :
  `.   `.| | | | | | |.'   .'
    `.   `-:_| | |_:-'   .'
      `-._   ````    _.-'
          ``-------''
          """
    print(p)

def lotto():
    import random
    l = random.sample((range(1,46)),6)
    print(l)

