from setuptools import setup, find_packages
import re

package = "mgefit"

def find_version(package):
    version_file = open(package + "/__init__.py").read()
    rex = r'__version__\s*=\s*"([^"]+)"'
    return re.search(rex, version_file).group(1)

def read_docstring(package, name):
    main_file = open(package + "/" + name + ".py").read()
    rex = r'class ' + name + r':\n\s*"""([\W\w]+?)"""'
    docstring = re.search(rex, main_file).group(1)
    return docstring.replace("\n    ", "\n")

setup(name=package,
      version=find_version(package),
      description='MgeFit: Multi-Gaussian Expansion Fitting of Galactic Images',
      long_description=open(package + "/README.rst").read()
                       + read_docstring(package, "mge_fit_sectors")
                       + read_docstring(package, "mge_fit_1d")
                       + read_docstring(package, "find_galaxy")
                       + "\n\nLicense\n=======\n\n"
                       + open(package + "/LICENSE.txt").read()
                       + open(package + "/CHANGELOG.rst").read(),
      long_description_content_type= 'text/x-rst',
      url="https://purl.org/cappellari/software",
      author="Michele Cappellari",
      author_email="michele.cappellari@physics.ox.ac.uk",
      license="Other/Proprietary License",
      packages=find_packages(),
      package_data={package: ["*.rst", "*.txt", "*.pdf", "*/*.txt", "*/*.fits"]},
      install_requires=['capfit', 'numpy', 'scipy', 'matplotlib', 'astropy'],
      classifiers=["Development Status :: 5 - Production/Stable",
                   "Intended Audience :: Developers",
                   "Intended Audience :: Science/Research",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python :: 3"],
      zip_safe=True)
