from glob import glob

from setuptools import find_packages, setup

package_name = 'pai_final_controller'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        (
            'share/ament_index/resource_index/packages',
            ['resource/' + package_name]
        ),
        (
            'share/' + package_name,
            ['package.xml']
        ),
        (
            'share/' + package_name + '/config',
            glob('config/*.json')
        ),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ubuntu',
    maintainer_email='ubuntu@todo.todo',
    description='CRANE+ V2 AI task controller',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'task_controller = pai_final_controller.task_controller:main',
        ],
    },
)