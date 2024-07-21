import setuptools
from pkg_resources import parse_requirements
with open("requirements.txt", encoding="utf-8") as fp:
    install_requires = [str(requirement) for requirement in parse_requirements(fp)]

setuptools.setup(
    name='eiten',
    version='1.0.1',
    description='eiten',
    python_requires='>=3.6',
    author='Chenkechao',
    author_email='chenkechao123@163.com',
    long_description='eiten',
    long_description_content_type="text/markdown",
    license='GNU General Public License v3 or later (GPLv3+)',
    url="https://test.com",
    # What does your project relate to?
    keywords=['eiten'],

    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers = [
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Financial",
        "Topic :: Software Development"
    ],

    install_requires=install_requires,
)
