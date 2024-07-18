from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.develop import develop
from setuptools.command.egg_info import egg_info
import subprocess
import os 
import sys
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

def _patch():
    # Apply the patch to graphium
    print("Applying patch to graphium...")
    graphium_path = subprocess.check_output([sys.executable, '-c', 'import graphium; print(graphium.__path__[0])']).decode('utf-8').strip()
    graphium_file_path = os.path.join(graphium_path, 'nn', 'architectures', 'global_architectures.py')
    patch_file = str(this_directory / "graphium_patch.diff")
    # Apply the patch
    try:
        with open(patch_file, 'r') as patch:
            subprocess.call(['patch', '--forward', '--reject-file=-', graphium_file_path], stdin=patch)
        print("Patch applied successfully.")
    except subprocess.CalledProcessError as e:
        if "Reversed (or previously applied) patch detected" in str(e.stderr):
            print("Patch is already applied.")
        else:
            raise e

    # Verify graphium installation
    import graphium
    print("Graphium is installed and imported successfully.")


class CustomInstallCommand(install):
    def run(self):
        subprocess.check_call([sys.executable, "-m", "pip", "install", "torch>=2.0"])
        install.run(self)
        _patch()

class CustomDevelopCommand(develop):
    def run(self):
        print('develop')
        develop.run(self)
        _patch()

class CustomEggCommand(egg_info):
    def run(self):
        print('egg_info')
        egg_info.run(self)
        _patch()


setup(
    name='minimol',
    version='0.3.1',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'minimol.ckpts.minimol_v1': [
            'state_dict.pth',
            'config.yaml',
            'base_shape.yaml'
        ],
        '': ['graphium_patch.diff'],
    },
    install_requires=[
        "typer",
        "loguru",
        "omegaconf >=2.0.0",
        "tqdm",
        "platformdirs",
        # scientific
        "numpy",
        "scipy >=1.4",
        "pandas >=1.0",
        "scikit-learn",
        "fastparquet",
        # ml
        "hydra-core",
        "lightning >=2.0",
        "torchmetrics >=0.7.0,<0.11",
        "ogb",
        "torch-geometric >=2.0",
        "wandb",
        "mup",
        "torch_sparse >=0.6",
        "torch_cluster >=1.5",
        "torch_scatter >=2.0",
        # viz
        "matplotlib >=3.0.1",
        "seaborn",
        # cloud IO
        "fsspec >=2021.6",
        "s3fs >=2021.6",
        "gcsfs >=2021.6",
        # chemistry
        "datamol >=0.10",
        "graphium==2.4.7",
    ],
    url='https://github.com/graphcore-research/minimol',
    author='Blazej Banaszewski, Kerstin Klaser',
    author_email='blazej@banaszewski.pl, kerstink@graphcore.ai',
    description='Molecular fingerprinting using pre-trained deep nets',
    long_description=long_description,
    long_description_content_type='text/markdown',
    python_requires='>=3.9',
    cmdclass={
        'install': CustomInstallCommand,
        'develop': CustomDevelopCommand,
        'egg_info': CustomEggCommand,
    },
)
