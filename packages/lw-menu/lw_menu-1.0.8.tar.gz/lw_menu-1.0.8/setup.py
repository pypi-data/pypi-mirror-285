# import codecs
# import os
#
# from setuptools import find_packages, setup
#
# # these things are needed for the README.md show on pypi
# here = os.path.abspath(os.path.dirname(__file__))
#
# with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
#     long_description = "\n" + fh.read()
#
#
# VERSION = '1.0.4'
# DESCRIPTION = 'A light weight command line menu that supports Windows'
# LONG_DESCRIPTION = 'A light weight command line menu. Supporting Windows. It has support for hotkeys'
#
# # Setting up
# setup(
#     name="lw_menu",
#     version=VERSION,
#     author="lw",
#     author_email="2976638734@qq.com",
#     description=DESCRIPTION,
#     long_description_content_type="text/markdown",
#     long_description=long_description,
#     packages=find_packages(),
#     install_requires=[
#         'getch; platform_system=="Unix"',
#         'getch; platform_system=="MacOS"',
#     ],
#     keywords=['python', 'menu', 'lw_menu', 'windows', 'mac', 'linux'],
#     classifiers=[
#         "Development Status :: 1 - Planning",
#         "Intended Audience :: Developers",
#         "Programming Language :: Python :: 3",
#         "Operating System :: Unix",
#         "Operating System :: MacOS :: MacOS X",
#         "Operating System :: Microsoft :: Windows",
#     ]
# )

from setuptools import setup, find_packages
import os
import codecs
here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()
setup(
    name='lw-menu',
    version='1.0.8',
    packages=find_packages(),
    install_requires=[
        # 依赖库列表
    ],
    author='lw',
    author_email='2976638734@qq.com',
    description='A short description of your package',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)