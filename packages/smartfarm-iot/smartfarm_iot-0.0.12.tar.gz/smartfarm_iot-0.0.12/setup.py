from setuptools import setup, find_packages

setup(
    name='smartfarm_iot',
    version='0.0.12',
    packages=find_packages(include=['smartfarm_iot', 'smartfarm_iot.*',
                                    'config', 'config.*', 'run.sh']),
    install_requires=[
        'paho-mqtt',
        'pyModbusTCP'
    ],
    package_data={
        'smartfarm_iot': ['config/*.json', 'config/*.csv'],
    },
    entry_points={
        'console_scripts': [
            'smartfarm_iot=smartfarm_iot.main:main',
        ],
    },
    author='kimyuri',
    author_email='rikim94@naver.com',
    description='A package for Smart Farm IoT data collection and publishing using Modbus TCP and MQTT',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='http://www.doctor-ag.com/',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
