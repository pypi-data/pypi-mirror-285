# banner_baechu805

# **pyfiglet**
```
    __                    __          ____  ____  ______
   / /_  ____ ____  _____/ /_  __  __( __ )/ __ \/ ____/
  / __ \/ __ `/ _ \/ ___/ __ \/ / / / __  / / / /___ \
 / /_/ / /_/ /  __/ /__/ / / / /_/ / /_/ / /_/ /___/ /
/_.___/\__,_/\___/\___/_/ /_/\__,_/\____/\____/_____/

```

# show-banner

show-banner is a simple command that prints input text in banner format using figlet.

# Requirements

figlet needs to be installed. figlet is a tool that converts text into stylish ASCII art banners.

## Pyfiglet is also a library that can be used in python code:

```py
from pyfiglet import Figlet
f = Figlet(font='slant')
print(f.renderText('text to render'))
```

or

```py
import pyfiglet
f = pyfiglet.figlet_format("text to render", font="slant")
print(f)
```
If you have found some new fonts that you want to use, you can use the
command line interface to install your font file as follows:

`pyfiglet -L <font file>`

The font file can be a ZIP file of lots of fonts or just a single font.
Depending on how you installed pyfiglet, you may find that you need
root access to install the font - e.g. `sudo pyfiglet -L <font file>`.

## Ubuntu/Debian

```sh
sudo apt-get update
sudo apt-get install figlet

