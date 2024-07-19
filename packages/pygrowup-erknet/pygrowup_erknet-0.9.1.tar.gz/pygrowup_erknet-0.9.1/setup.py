from setuptools import setup, find_packages
from pathlib import Path
from pygrowup_erknet import get_version

package_name = "pygrowup_erknet"
version = get_version().replace(' ', '-')
readme_path = Path(__file__).parent / 'README'

with readme_path.open(encoding='utf-8') as f:
    long_description = f.read()

setup(
    name=package_name,
    version=version,
    license="BSD",

    packages=find_packages(),
    include_package_data=True,
    package_data={
        package_name: ['tables/**/*', 'testdata/**/*']
    },

    author="Evan Wheeler",
    author_email="evanmwheeler@gmail.com",

    maintainer="Eyal Rahmani",
    maintainer_email="eyal.rahmani@med.uni-heidelberg.de",

    description="Calculate z-scores of anthropometric measurements based on WHO and CDC child growth standards",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/eyal-erknet/pygrowup",
    download_url=f"https://github.com/eyal-erknet/pygrowup/archive/{version}.tar.gz",
    install_requires=[],
    classifiers=[
        'Intended Audience :: Healthcare Industry',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: BSD License',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
    ],
)
