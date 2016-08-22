from setuptools import setup, find_packages

# Customize
package_name = 'SudokuSolver'
version = '0.1.0'
description = 'Solver for Sudoku puzzles that uses logic based techniques'
install_requires = [
]


setup(
    name=package_name,
    version=version,
    description=description,
    url='https://github.com/dlomelin/%s' % (package_name),
    author='David Lomelin',
    author_email='david.lomelin@gmail.com',
    packages=find_packages(),
    install_requires=install_requires,
)
