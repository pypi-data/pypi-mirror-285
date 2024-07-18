# This file needs to be run with arguments as
# python3 setup.py sdist bdist_wheel --formats=zip
import setuptools
import os
import sys

ROOT_PATH = os.path.abspath(os.path.dirname(__file__))

with open(f'{ROOT_PATH}/README.rst', 'r') as file:
    long_description = file.read()

project_name = "cmrseq"
author_list = "Jonathan Weine, Charles McGrath"
author_email_list = "weine@biomed.ee.ethz.ch, mcgrath@biomed.ee.ethz.ch"
url =  'https://gitlab.ethz.ch/jweine/cmrseq'

project_urls = {
    'Documentation': 'https://people.ee.ethz.ch/~jweine/cmrseq/latest/index.html',
    'Source': 'https://gitlab.ethz.ch/ibt-cmr/mri_simulation/cmrseq',
    'Institute': 'https://cmr.ethz.ch/'
}

# Get version tag
if '--version' in sys.argv:
    tag_index = sys.argv.index('--version') + 1
    current_version = sys.argv[tag_index]
    sys.argv.pop(tag_index-1)
    sys.argv.pop(tag_index-1)
else:
    raise ValueError('No version as keyword "--version" was specified')

with open(f'{project_name}/__init__.py', 'r+') as module_header_file:
   content = module_header_file.read()
   module_header_file.seek(0)
   module_header_file.write(f"__version__ = '{(current_version)}'\n" + content)

setuptools.setup(
    name=project_name,
    url=url,
    project_urls=project_urls,
    version=current_version,
    author=author_list,
    author_email=author_email_list,
    long_description=long_description,
    long_description_type="rst",
    include_package_data=True,
    packages=setuptools.find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    python_requires=">=3.6",
    install_requires=["numpy", "pint", "matplotlib", "tqdm", "scipy"]
)
