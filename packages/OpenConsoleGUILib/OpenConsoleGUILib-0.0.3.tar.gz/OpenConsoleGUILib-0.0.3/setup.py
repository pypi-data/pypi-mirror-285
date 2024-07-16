from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.0.3'
DESCRIPTION = 'Create functional menus & loading bars in the terminal with just a few lines.'
LONG_DESCRIPTION = 'Create menus & loading/progress bars in your terminal, you can navigate in theses menus with your keyboard & change the keymaps in real time via code. More features are planned for the future.'

setup(
    name="OpenConsoleGUILib",
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