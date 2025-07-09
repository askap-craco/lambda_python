from setuptools import setup, find_packages, Command
import subprocess


# need to build exec so you can ssudo setcap it so it can be run without sudo

class BuildExeCommand(Command):
    description = 'Build standalone executable with PyInstaller'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        subprocess.check_call([
            'pyinstaller', '--onefile', 'lambda_python/tools/lambda_config.py'
        ])

setup(
    name='lambda_python',
    version='0.1.0',
    author='Your Name',
    author_email='keith.bannister@csiro.au',
    description='Lambda Tools',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],    
    cmdclass={
        'build_exe': BuildExeCommand,
    },
    python_requires='>=3.6',
    install_requires=[
        # List your package dependencies here
        'numpy',
        'scipy',
        'pandas',
        'matplotlib',
        'scapy',
        'netifaces'
    ],
    entry_points={
        'console_scripts': [
            'lambda_config = lambda_python.tools.lambda_config:main',
            'lambda_monitor = lambda_python.tools.lambda_monitor:main',
            'lambda_mux = lambda_python.tools.lambda_mux:main',
        ]
    }
)