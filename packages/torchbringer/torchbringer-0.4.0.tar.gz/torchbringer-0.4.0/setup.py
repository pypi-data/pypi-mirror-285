from setuptools import setup, find_namespace_packages

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='torchbringer',
    long_description=long_description,
    long_description_content_type='text/markdown',
    version='0.4.0',    
    description='A PyTorch library for deep reinforcement learning ',
    url='https://github.com/moraguma/TorchBringer',
    author='Moraguma',
    author_email='g170603@dac.unicamp.br',
    license='MIT',
    packages=find_namespace_packages(),
    install_requires=[
        'setuptools>=70.0.0',
        'torch==2.3.0',
        'gymnasium==0.29.1',
        'aim==3.19.3',
        'numpy',
        'opencv-python',
        'protobuf',
        'grpcio',
        'flask==3.0.3'             
    ],

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',  
        'Operating System :: POSIX :: Linux',    
        'Environment :: GPU :: NVIDIA CUDA',  
        'Programming Language :: Python'  # TODO : Specify Python versions
    ],
)
