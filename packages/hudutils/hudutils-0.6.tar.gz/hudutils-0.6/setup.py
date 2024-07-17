# setup.py

from setuptools import setup, find_packages

setup(
    name='hudutils',
    version='0.6',
    packages=find_packages(),
    install_requires=[],
    include_package_data=True,
    description='Huds regularly used utilities ',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/huddaannaa/hudutils',
    author='Hud Daannaa',
    author_email='hdaannaa@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
)


