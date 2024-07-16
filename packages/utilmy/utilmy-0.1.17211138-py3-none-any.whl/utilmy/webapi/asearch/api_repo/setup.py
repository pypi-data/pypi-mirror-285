# -*- coding: utf-8 -*-
"""
"""
import io, os, subprocess, sys
from setuptools import find_packages, setup

######################################################################################
root = os.path.abspath(os.path.dirname(__file__))



##### Version  #######################################################################
version ='0.0.1'
cmdclass= None
print("version", version)



##### Requirements ###################################################################
install_requires = ['pyyaml',  'python-box', 'fire', 'requests' ]



###### Description ###################################################################
def get_current_githash():
   import subprocess 
   # label = subprocess.check_output(["git", "describe", "--always"]).strip();   
   label = subprocess.check_output([ 'git', 'rev-parse', 'HEAD' ]).strip();      
   label = label.decode('utf-8')
   return label

githash = get_current_githash()


#####################################################################################
ss1 = f"""
MLB 
Hash:
{githash}
"""


long_description = f""" ``` """ + ss1 +  """```"""



### Packages  ########################################################
packages = ["src"] + ["src." + p for p in find_packages("src")]
#packages = ["mlb"] + ["mlb.viz" + p for p in find_packages("mlb.viz")]
packages = ["src"] + [ p for p in  find_packages(include=['src.*']) ]
print(packages)


scripts = [     ]



### CLI Scripts  ###################################################   
entry_points={ 'console_scripts': [

    #'docs      = src.cli:run_cli',


 ] }




##################################################################   
setup(
    name="apiimg",
    description="img",
    keywords='img',
    
    author="",    
    install_requires=install_requires,
    python_requires='>=3.9',
    
    packages=packages,

    include_package_data=True,
    #    package_data= {'': extra_files},

    package_data={
       '': ['*','*/*','*/*/*','*/*/*/*']
    },

   
    ### Versioning
    version=version,
    #cmdclass=cmdclass,


    #### CLI
    scripts = scripts,
  
    ### CLI pyton
    entry_points= entry_points,


    long_description=long_description,
    long_description_content_type="text/markdown",


    classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: Developers',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: Apache Software License',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.6',
          'Topic :: Scientific/Engineering',
          'Topic :: Scientific/Engineering :: ' +
          'Artificial Intelligence',
          'Topic :: Software Development :: Libraries',
          'Topic :: Software Development :: Libraries :: ' +
          'Python Modules',
          'Topic :: Scientific/Engineering :: Information Analysis',
          'Environment :: Console',
          'Environment :: Web Environment',
          'Operating System :: POSIX',
          'Operating System :: MacOS :: MacOS X',
      ]
)


