from setuptools import setup, find_packages

setup(
    name='GauAPIs',
    version='2.0.2',
    packages=find_packages(),
    install_requires=[ 'numpy'
        
    ],
    author='Sam Yunteng Liao',
    author_email='lmasgne@gmail.com',
    description='APIs for Gaussian running other calculators through External',
    license='MIT',
    platforms="linux",
    entry_points={ 'console_scripts':['GauAPIs = GauAPIs.main:run',]},
    keywords='Gaussian--external python APIs',
    url='https://github.com/SamYToeL/APIs'
)