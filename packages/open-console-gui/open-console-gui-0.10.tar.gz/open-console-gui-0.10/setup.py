from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.10'
DESCRIPTION = '✧ Interactive Console Menus & Loading Bars ✧'
LONG_DESCRIPTION = '''▁▂▃▄▆ OpenConsoleGUI is a library for creating interactive console UI elements.

《✩》 FEATURES 《✩》
◉ Interactive menus with keyboard navigation
◉ Predefined / custom styles for menus

◉ Interactive progress-bars with a ton of options
◉ Predefined / custom styles for progress-bars

《✩》 EXAMPLES 《✩》
LoadingBar (predefined style-0) :
    █████████████████████████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ 50%

LoadingBar (predefined style-1) :
    |█████████████████████████                         | 50%

LoadingBar (predefined style-2) :
    ■■■■■■■■■■■■■■■■■■■■■■■■■□□□□□□□□□□□□□□□□□□□□□□□□□ 50%

LoadingBar (predefined style-3) :
    ▰▰▰▰▰▰▰▰▰▰▰▰▰▱▱▱▱▱▱▱▱▱▱▱▱▱▱ 50%

Menu (predefined style-0) :
     |[MenuTitle]|
    >  0.Option0
       1.Option1
       2.Option2

Menu (predefined style-1) :
     【MenuTitle】
    ▶  0.Option0
       1.Option1
       2.Option2

Menu (predefined style-2) :
     ☾MenuTitle☽
   ➤  0.Option0
       1.Option1
       2.Option2

Menu (predefined style-3) :
     𓇼MenuTitle𓇼
    ✦  0.Option0
       1.Option1
       2.Option2

《✩》 Install & Usage 《✩》
◉ For more information on how to use the tool, please head over to the GitHub repos.
❖ GitHub : https://github.com/SHARKgamestudio/OpenConsoleGUI
'''

setup(
    name="open-console-gui",
    version=VERSION,
    author="SHARKstudio (Jay Morrington)",
    author_email="<animating.du.38@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['keyboard'],
    keywords=['python', 'menu', 'progress-bar', 'gui', 'terminal', 'console'],
    classifiers=[
        "Intended Audience :: Developers",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
