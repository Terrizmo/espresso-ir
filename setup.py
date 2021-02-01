from setuptools import setup, find_packages

def read_requirements():
    with open('requirements.txt') as req:
        content = req.read()
        requirements = content.split('\n')

    return requirements


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='espresso_ir',
    version='0.0.2',
    author='Terrizmo',
    author_email='espressoir@outlook.com',    
    description='IR tool for acquiring memory images from windows EC2 instances on AWS',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/terrizmo/espresso_ir",
    #package_dir={'': 'espresso_ir'},
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "Intended Audience :: System Administrators",
        "Environment :: Console",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.7",
        "Topic :: Security",
    ],
    python_requires='>=3.7',
    include_package_data=True,
    install_requires=read_requirements(),
    entry_points='''
        [console_scripts]
        espresso_ir=espresso_ir.cli:cli
        '''
)
