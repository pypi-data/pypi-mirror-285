import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
setuptools.setup(
    name= 'ha_oder',
    version= '0.1',
    author= 'loke_Hawkeye',
    description= 'Something new to try in Python ',
    packages=setuptools.find_packages(),
    classifiers=[
    "Programming Language :: Python :: 3",
    "Operating System :: OS Independent",
    "License :: OSI Approved :: MIT License"
    ]
)