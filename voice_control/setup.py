import os
from glob import glob

from setuptools import find_packages, setup

package_name = 'voice_control'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ubuntu',
    maintainer_email='emmanuelnyame05m@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'nlu_node = voice_control.nlu_node:main',
            'udp_receiver_node = voice_control.udp_receiver_node:main',
            'voice_to_movement_node = voice_control.voice_to_movement_node:main'
        ],
    },

)
