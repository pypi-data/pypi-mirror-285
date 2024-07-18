from setuptools import setup, find_packages
from os.path import dirname
from os.path import realpath
from os.path import join
import io


def open_config_file(*names, **kwargs):
    current_dir = dirname(realpath(__file__))
    return io.open(
        join(current_dir, *names),
        encoding=kwargs.get('encoding', 'utf8')
    )

install_dependencies = open_config_file('requirements.txt').read().splitlines()

setup(
    name='vrf',
    version='1.0.7',
    author='lucyfer',
    description='VRF with ability to validate',
    packages=find_packages(),
    install_requires=install_dependencies,
    # entry_points={
    #     'console_scripts': [
    #         "test = vrf_py.VRF:func_name",
    #     ]
    # }
)
