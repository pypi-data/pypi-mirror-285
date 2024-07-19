
from distutils.core import setup
setup(
  name = 'setga',         
  packages = ['setga'], 
  license='MIT',       
  description = 'library designed to extract a minimal subset from a given set, optimizing a given (set of) objective(s). Based on the DEAP library.',   # Give a short description about your library
  author = 'Nikola Kalábová',              
  author_email = 'nikola@kalabova.eu',     
  url = 'https://github.com/lavakin/setga',  
  version = "v2.0",    
  #version = 1.0,
  keywords = ['Genetic algorithms', 'minimal subset', 'multi-objective', "optimization"],   
  long_description = "library designed to extract a minimal subset from a given set, optimizing a given (set of) objective(s). Based on the DEAP library.",
  project_urls = {"Documentation" :"https://setga.readthedocs.io/en/latest/genindex.html"},
  install_requires=[          
          'numpy',
          'deap',
          "matplotlib",
      ],

  classifiers=[
    'Development Status :: 3 - Alpha',
    'License :: OSI Approved :: MIT License',  
  ],
)
