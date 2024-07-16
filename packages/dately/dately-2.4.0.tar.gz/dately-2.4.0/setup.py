from setuptools import setup, find_packages
import sys

# Check if the system is Windows
if sys.platform != 'win32':
    raise RuntimeError('This package is only compatible with Windows.')

## -- Beta
setup(
    name='dately',
    version="2.4.0",  # Beta version
    author='Cedric Moore Jr.',
    author_email='cedricmoorejunior5@gmail.com',
    description='A comprehensive Python library for advanced date and time manipulation.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/cedricmoorejr/dately/tree/v2.4.0',
    project_urls={
        'Source Code': 'https://github.com/cedricmoorejr/dately/releases/tag/v2.4.0',
    },
    packages=find_packages(),
    package_data={
        'dately': [
            'mold/pyd/*.pyd',
            'mold/pyd/cdatetime/*.pyd',
            'sources/timezone_data.json',
            'sources/holiday.json',
            'mold/include/*.h',
            'mold/pyx/*.pyx',
            'mold/src/*.c',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',        
    ],
    python_requires='>=3.8',
    install_requires=[
        'numpy',
        'pandas',
        'pytz',
        'requests',
    ],
    license='MIT',
)


# import sys
# from setuptools import setup, find_packages, Extension
# from Cython.Build import cythonize
# 
# # Define OS-specific dependencies
# extra_requires = {
#     'win32': ['numpy', 'pandas', 'pytz', 'requests'],
#     'other': ['numpy', 'pytz', 'requests']  # Simpler dependencies for non-Windows
# }
# 
# # Define package data and extensions conditionally
# package_data = {
#     'dately': [
#         'sources/timezone_data.json',
#         'sources/iana_zones.json'
#     ] + (['mold/pyd/*.pyd', 'mold/pyd/cdatetime/*.pyd'] if sys.platform == 'win32' else [])
# }
# 
# # Start with an empty list of extensions
# extensions = []
# 
# if sys.platform != 'win32':
#     extensions = cythonize([
#         Extension("dately.clean_str", 
#                   sources=["dately/mold/pyx/clean_str.pyx", "dately/mold/src/clean_str_impl.c"],
#                   include_dirs=["dately/mold/include"]),
#         Extension("dately.Compiled",
#                   sources=["dately/mold/pyx/Compiled.pyx"],
#                   include_dirs=["dately/mold/include"]),
#         Extension("dately.iso8601T",
#                   sources=["dately/mold/pyx/iso8601T.pyx", "dately/mold/src/iso8601T_impl.c"],
#                   include_dirs=["dately/mold/include"]),
#         Extension("dately.iso8601Z",
#                   sources=["dately/mold/pyx/iso8601Z.pyx", "dately/mold/src/iso8601Z_impl.c"],
#                   include_dirs=["dately/mold/include"]),
#         Extension("dately.time_zones",
#                   sources=["dately/mold/pyx/time_zones.pyx", "dately/mold/src/time_zones_impl.c"],
#                   include_dirs=["dately/mold/include"]),
#         Extension("dately.UniversalDateFormatter",
#                   sources=["dately/mold/pyx/UniversalDateFormatter.pyx"],
#                   include_dirs=["dately/mold/include"]),
#         Extension("dately.whichformat",
#                   sources=["dately/mold/pyx/whichformat.pyx"],
#                   include_dirs=["dately/mold/include"]),
#     ])
# # Setup requires different libraries based on the platform
# install_requires = extra_requires['win32'] if sys.platform == 'win32' else extra_requires['other']
# setup_requires = ['Cython'] if ('bdist_wheel' in sys.argv or sys.platform != 'win32') else []
# 
# setup(
#     name='dately',
#     version="2.2.0b2",
#     author='Cedric Moore Jr.',
#     author_email='cedricmoorejunior5@gmail.com',
#     description='A comprehensive Python library for advanced date and time manipulation.',
#     long_description=open('README.md').read(),
#     long_description_content_type='text/markdown',
#     url='https://github.com/cedricmoorejr/dately',
#     project_urls={
#         'Source Code': 'https://github.com/cedricmoorejr/dately/tree/main/dately',
#     },
#     packages=find_packages(),
#     package_data=package_data,
#     classifiers=[
#         'Programming Language :: Python :: 3',
#         'License :: OSI Approved :: MIT License',
#         'Operating System :: Microsoft :: Windows',
#         'Operating System :: POSIX :: Linux',
#         'Operating System :: MacOS :: MacOS X',
#         'Development Status :: 5 - Production/Stable',
#         'Intended Audience :: Developers',
#         'Natural Language :: English',
#         'Programming Language :: Python :: 3.8',
#         'Programming Language :: Python :: 3.9',
#         'Programming Language :: Python :: 3.10',
#     ],
#     python_requires='>=3.8',
#     install_requires=install_requires,
#     setup_requires=setup_requires,
#     ext_modules=extensions,
#     license='MIT',
# )













