# setup.py
from setuptools import setup, find_packages

setup(
    name='AILungMeasure',
    version='0.1.0',
    packages=find_packages(include=['AILungMeasure', 'AILungMeasure.*']),
    install_requires=[
        'torch',
        'Pillow',
        'torchvision',
        'matplotlib',
        'opencv-python',
        'numpy',
        'imutils',
        'requests'
    ],
    author='Mostafa Ismail',
    author_email='mostafa.ismail.k@gmail.com',
    description='Automated lung size measurements using deep learning and computer vision on portable chest radiographs.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/AILungMeasure',  # Update with your project URL
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    include_package_data=False,
)

