from setuptools import setup

package_name = 'nav_study_trials'
setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Jayesh chaudhari',
    maintainer_email='127026542+Jayesh518@users.noreply.github.com',
    description='Trial runner and metric code for the Nav2 configuration study.',
    license='Apache-2.0',
    entry_points={'console_scripts': ['run_trials = nav_study_trials.runner:main',
                                      'plan_flip_guard = nav_study_trials.plan_flip_guard:main',
                                      'waypoint_mission = nav_study_trials.waypoint_mission:main']},
)
