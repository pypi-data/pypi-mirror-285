from setuptools import setup, find_packages

setup(
    name='shppy',
    version='0.0.1',
    description=(
    	"Season's High Performance library for Python"
    	 ),
    long_description=open('README.md').read(),
    author='Chon-Hei Lo',
    author_email='siumabon123@gmail.com',
    maintainer='Chon-Hei Lo',
    maintainer_email='siumabon123@gmail.com',
    license='MIT License',
    url='https://github.com/supercgor/shppy',
    packages=find_packages(),
    entry_points={
    'console_scripts': [
        'shppy = shppy.main:main',
        ]
    },
    package_data={
        'shppy': []
    },
    classifiers=[
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3'
    ],
    python_requires='>=3.9',
    install_requires=[
        'wheel',
		'numpy',
        'numba',
		'scipy',
		'pandas',
		'ase',
		'matplotlib',
    ]
)
