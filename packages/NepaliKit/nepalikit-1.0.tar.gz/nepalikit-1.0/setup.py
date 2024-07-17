from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name='NepaliKit',
    version='1.0',
    packages=find_packages(),
    install_requires=[
        'torch',
        'sentencepiece'
    ],
    entry_points={
        'console_scripts': [
            'nepalikit-cli = NepaliKit.__main__:main',
        ],
    },
    author='Prabhash Kumar Jha',
    author_email='prabhashj07@gmail.com',
    description='A Nepali language processing library',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/prabhashj07/NepaliKit.git',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)

