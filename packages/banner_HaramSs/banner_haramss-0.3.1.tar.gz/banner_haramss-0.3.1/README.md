# banner_HaramSs

Usage
pyfiglet can be used is python code:

```bash
from pyfiglet import Figlet
f = Figlet(font='slant')
print(f.renderText('text to render'))

```
or

```bash
import pyfiglet
f = pyfiglet.figlet_format("text to render", font="slant")
print(f)
```
found new font

```bash
pyfiglet -L <font file>
```

root access to install the font

```bash
sudo pyfiglet -L <font file>
```

