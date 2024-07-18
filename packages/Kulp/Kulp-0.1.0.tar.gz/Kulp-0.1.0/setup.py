from setuptools import setup, find_packages

setup(
    name='Kulp',
    version='0.1.0',
    packages=["Kulp"],
    install_requires=[
        "pygame"
    ],
    author='Random Guy',
    author_email='randomguy666998@gmail.com',
    description='Easy-to-use Game development library',
    long_description="This library is alot easier to use than pygame (tho not as versatile)",
    url='https://github.com/devpython88/KulpPython',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
)

