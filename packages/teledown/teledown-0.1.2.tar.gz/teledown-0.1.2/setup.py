from setuptools import setup, find_packages

setup(
    name='teledown',
    version='0.1.2',
    description='A simple CLI tool to download videos from Telegram channels',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Nyi Nyi Lwin',
    author_email='hello.nyinyilwin@gmail.com',
    url='https://github.com/konyilwin/teledown',
    packages=find_packages(),
    install_requires=[
        'click',
        'telethon',
        'tabulate',
        'tqdm',
    ],
    entry_points={
        'console_scripts': [
            'teledown=teledown.__main__:cli',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    include_package_data=True,
)
