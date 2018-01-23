from setuptools import setup, find_packages

setup(
    name='quilldelta',
    author='Mario César Señoranis Ayala',
    author_email='mariocesar.c50@gmail.com',
    version='0.1',
    url='https://github.com/mariocesar/python-quill-delta',
    description='',
    packages=find_packages('', exclude='tests/*'),
    python_requires='>=3.6',
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'pytest-cov'],
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: MIT License',
    ],
)
