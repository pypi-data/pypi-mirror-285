from distutils.core import setup

setup(
  name = 'landerslabutils',
  packages = ['landerslabutils'],
  version = '0.0.3',
  license='MIT',
  description = 'Landers Lab utilities for ALS compute project',
  long_description="""LandersLabUtils functions \n

Library overview: \n


* hail_init(): Initializes a Hail session with specific project and workspace settings. \n
* genetable_fromMT(): Filters a Hail MatrixTable by gene and variant type, then exports the results as a TSV file. \n
* singlesample_fromMT(): Filters a Hail MatrixTable for a single sample and exports the results as either a table or a VCF file. \n
* jointVCF_fromMT(): Filters a Hail MatrixTable by sample groups and exports the results as VCF files for each chromosome. \n
* extract_regions(): Filters a Hail MatrixTable based on genomic regions. \n

\n
A comprehensive documentation is available at: https://albertobrusati.github.io/LandersLabUtils/
 
 \n

			For any doubt, please write to a.brusati@auxologico.it""",
  long_description_content_type="text/markdown",
  author = 'alberto brusati',
  author_email = 'a.brusati@auxologico.it',
  url = 'https://github.com/albertobrusati/LandersLabUtils',
  keywords = ['bioinformatic', 'molecular data', 'hail', 'genetics'],
  install_requires=[
          'hail',
          'pandas',
          'bokeh'
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Programming Language :: Python :: 3.11',
  ]
)
