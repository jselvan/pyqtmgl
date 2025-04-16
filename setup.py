from setuptools import setup, find_packages

setup(
    name='pyqtmgl',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'moderngl',
        'numpy',
        'PyQt5',
        'pyglm',
    ],
    entry_points="""
        [console_scripts]
        pyqtmgl-points=pyqtmgl.test.points:main
    """,
    author='Janahan Selvanayagam',
    author_email="me@janahan.ca",
    description='ModernGL wrapper for PyQt5',
    license='MIT',
    keywords='moderngl pyqt5',
    zip_safe=False,
)