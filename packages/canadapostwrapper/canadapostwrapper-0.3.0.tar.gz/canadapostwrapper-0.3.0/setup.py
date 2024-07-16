from setuptools import setup, find_packages

setup(
    name='canadapostwrapper',
    version='0.3.0',
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
    entry_points={
        'console_scripts': [
            'canadapostwrapper=canadapost:CanadaPostTracker.start_tracking',
        ],
    },
    author='shibakek',
    author_email='wilhemnorman732@gmail.com',
    description='A package to track Canada Post shipments',
    url='https://github.com/shibakek2/canada-post',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)