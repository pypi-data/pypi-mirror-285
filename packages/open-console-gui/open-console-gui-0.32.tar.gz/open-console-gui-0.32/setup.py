from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.32'
DESCRIPTION = '✧ Interactive Console Menus & Loading Bars ✧'
LONG_DESCRIPTION = '''▁▂▃▄▆ OpenConsoleGUI is a library for creating interactive console UI elements.\n
\n
\n
《✩》 FEATURES 《✩》\n
◉ Interactive menus with keyboard navigation\n
◉ Predefined / custom styles for menus\n
\n
◉ Interactive progress-bars with a ton of options\n
◉ Predefined / custom styles for progress-bars\n
\n
\n
《✩》 EXAMPLES 《✩》\n
LoadingBar (predefined style-0) :\n
    █████████████████████████························· 50%\n
\n
LoadingBar (predefined style-1) :\n
    |█████████████████████████                         | 50%\n
\n
LoadingBar (predefined style-2) :\n
    ■■■■■■■■■■■■■■■■■■■■■■■■■□□□□□□□□□□□□□□□□□□□□□□□□□ 50%\n
\n
LoadingBar (predefined style-3) :\n
    ▰▰▰▰▰▰▰▰▰▰▰▰▰▱▱▱▱▱▱▱▱▱▱▱▱▱▱ 50%\n
\n
Menu (predefined style-0) :\n
     |[MenuTitle]|\n
    >  0.Option0\n
       1.Option1\n
       2.Option2\n
\n
Menu (predefined style-1) :\n
     【MenuTitle】\n
    ▶  0.Option0\n
       1.Option1\n
       2.Option2\n
\n
Menu (predefined style-2) :\n
     ☾MenuTitle☽\n
    ➤  0.Option0\n
        1.Option1\n
        2.Option2\n
\n
Menu (predefined style-3) :\n
     𓇼MenuTitle𓇼\n
    ✦  0.Option0\n
       1.Option1\n
       2.Option2\n
\n
\n
《✩》 Install & Usage 《✩》\n
◉ For more information on how to use the tool, please head over to the GitHub repos.\n
❖ GitHub : https://github.com/SHARKgamestudio/OpenConsoleGUI\n
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
