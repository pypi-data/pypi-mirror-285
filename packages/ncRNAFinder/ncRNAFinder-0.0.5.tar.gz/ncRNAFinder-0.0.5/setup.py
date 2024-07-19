from distutils.core import setup

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
  name = 'ncRNAFinder',         # How you named your package folder (MyLib)
  packages = ['ncRNAFinder'],   # Chose the same as "name"
  version = '0.0.5',      # Start with a small number and increase it with every change you make
  license='GPL',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'ncRNAfinder is an automatic and scalable system for large-scale data annotation analysis of ncRNAs which use both sequence and structural search strategy for ncRNA annotation.',   # Give a short description about your library
  author = 'gregoriovitor',                   # Type in your name
  author_email = 'vitor-gregorio@hotmail.com',      # Type in your E-Mail
  url = 'https://github.com/user/reponame',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/GregorioVitor/ncRNAfinder/archive/refs/tags/v_01.tar.gz',    # I explain this later on
  keywords = ['ncRNA', 'annotation', 'BLAST', 'INFERNAL', 'structure'],   # Keywords that define your package best
  readme = "README.md",
  long_description_content_type='text/markdown',
  long_description=long_description,
  dependencies=["biopython",
          "pandas",
          "matplotlib",
          "numpy",
          "matplotlib-venn",
	        "joblib"
          ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)
