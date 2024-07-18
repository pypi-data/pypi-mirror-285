from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read()

setup(
    name='nhp-prep',
    version='1.0.1',
    author='Hugo Angulo, Zijun Zhao',
    author_email='hugoanda@andrew.cmu.edu, zijunzha@andrew.cmu.edu',
    license='MIT',
    description='Pre-processing data tool for NHP Lab @ CMU',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://caoslab.psy.cmu.edu:32443/monkeylab/preprocessing-scripts',
    py_modules=['nhp-prep', 'app'],
    packages=find_packages(),
    install_requires=[requirements],
    keywords=['nhp-prep', 'caoslab', 'cmu', 'pre-processing'],
    python_requires='>=3.8',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.8",
    ],
    entry_points='''
        [console_scripts]
        nhp-prep=app.__main__:main
    ''',
    include_package_data=True,
    package_data={
        '': ["config/*"]
    }
)
