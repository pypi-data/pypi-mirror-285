# Always prefer setuptools over distutils
from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(name='rasl-artnet',
      version='0.1.1',
      description='ARTNet server and gui',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='http://github.com/VU-RASL/ARTNet',
      author='Alexandra Watkins',
      author_email='alexandra.watkins@vanderbilt.edu',
      license='MIT',
      package_dir={"":"src"},
      packages=['artnet'],
      python_requires=">=3.12, <4",
      install_requires=[
        'pyzmq',
        'protobuf',
        'python-dotenv',
        'pyaudio'
      ],
      entry_points = {
        'console_scripts': ['artnet-gui=artnet.command_line:artnetGui'],
      }
)
      