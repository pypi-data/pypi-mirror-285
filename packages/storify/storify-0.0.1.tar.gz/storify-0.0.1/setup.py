from setuptools import setup, find_packages

setup(
    name='storify',
    version='0.0.1',
    packages=find_packages(),
    include_package_data=True,
    license='MIT',
    description='A lightweight database system for Python',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Ben Baptist',
    author_email='sawham6@gmail.com',
    url='https://github.com/benbaptist/storify',
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
    install_requires=[
        'msgpack',
    ],
)