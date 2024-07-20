from setuptools import setup, find_packages

setup(
    name='uuv_mission_simulator',
    version='0.1.0',
    description='A UUV ocean data collection mission simulator based on an ocean model (ROMS)',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Ratna Prakarsha Kandukuri',
    author_email='rpkandukuri@outlook.com',
    url='https://github.com/Prakarsha01/UUVMissionSim',
    packages=find_packages(),
    install_requires=[
        'xarray',
        'numpy',
        'pandas',
        'joblib',
        'xroms',
        'matplotlib'
    ],
    python_requires='>=3.6',
)