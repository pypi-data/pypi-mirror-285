from setuptools import setup, find_packages

setup(
    name='ergo3d',  # Name of your package
    version='0.1.10',  # Version number
    description='A Python package for 3D ergonomic calculations.',  # Short description of your package
    url='https://github.com/LeyangWen/ergo3d',  # URL for your package's homepage
    author='Leyang Wen',  # Your name
    author_email='wenleyan@umich.edu',  # Your email
    license='MIT',  # License type for your package
    packages=find_packages(),  # Automatically find all packages and subpackages
    install_requires=[  # List of dependencies
        'numpy',
        'matplotlib',
        'opencv-python',
        'pandas'
    ],
    classifiers=[  # Classifiers help users find your project by categorizing it
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
    ],
    python_requires='>=3.6',  # Minimum version of Python your package requires
)


# import ast
# import os
#
# def get_imports(filepath):
#     with open(filepath, 'r') as file:
#         root = ast.parse(file.read(), filepath)
#
#     for node in ast.iter_child_nodes(root):
#         if isinstance(node, ast.Import):
#             for alias in node.names:
#                 yield alias.name
#         elif isinstance(node, ast.ImportFrom):
#             yield node.module
#
# def get_all_imports_in_project(project_path):
#     imports = set()
#     for dirpath, dirnames, filenames in os.walk(project_path):
#         for filename in filenames:
#             if filename.endswith('.py'):
#                 filepath = os.path.join(dirpath, filename)
#                 for module in get_imports(filepath):
#                     imports.add(module)
#     return imports
#
# project_path = '.'  # path to your project
# all_imports = get_all_imports_in_project(project_path)
# print('\n'.join(sorted(all_imports)))
