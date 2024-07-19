from setuptools import setup, find_packages
import pathlib 

setup(
    name='EOSpython',
    version='0.0.9',
    description='A set of functions encompassing a centralized Earth Observation Satellite scheduling system',
    long_description=pathlib.Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    url='https://github.com/AlexVasegaard/EOS',
    author='Alex Vasegaard',
    author_email= 'aev@mp.aau.dk',
    licence="MIT",
    keywords=['satellite', 'earth observation', 'operations research', 'optimization', 'simulator', 'scenario generator'],
    packages=find_packages(),
    package_data={
        'EOSpython': ['worldloc.csv'], 
    },
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.11, <4',
    install_requires=['pandas >=2.2.2', 
                      'numpy >=2.0.0', 
                      'ephem >=4.1.5', 
                      'datetime >=5.5', 
                      'requests >=2.32.3',
                      'folium >=0.17.0', 
                      'scipy  >=1.14',
                      'openpyxl >=3.1.5',
                      'geopy >=2.4.1',
                      'cvxopt >=1.3.2',
                      'gurobipy >=11.0.2',
                      'pulp >=2.8.0'],
    extras_require={
        'dev': ['twine>=5.1.1']
    }
)



