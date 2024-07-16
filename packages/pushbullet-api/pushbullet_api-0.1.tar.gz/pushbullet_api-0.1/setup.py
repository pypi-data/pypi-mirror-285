from setuptools import setup, find_packages

setup(
    name='pushbullet_api',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
    author='Patryk Okoń',
    author_email='patryk.okonn@gmail.com',
    description='A Python library for interacting with the Pushbullet API',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/ryba-22/pushbullet_api',  # replace with your GitHub URL
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
