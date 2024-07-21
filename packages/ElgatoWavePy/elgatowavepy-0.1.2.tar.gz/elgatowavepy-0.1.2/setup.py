
from setuptools import setup, find_packages

setup(
    name='ElgatoWavePy',
    version='0.1.2',
    packages=find_packages(),
    install_requires=[
        'websocket-client'
    ],
    author='Steepy12',
    description='Control Elgato WaveLink with Python',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Steepy12/PyWave',
    project_urls={
        'Documentation': 'https://github.com/Steepy12/PyWave/wiki',  # URL vers le wiki GitHub
        'Source': 'https://github.com/Steepy12/PyWave',
    },
    
    
    
    
    
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
