from setuptools import setup, find_packages

setup(
    name='GDriveOps',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        "google-api-python-client==1.7.2",
        "google-auth==2.14.1",
        "google-auth-httplib2==0.0.3",
        "google-auth-oauthlib==0.4.1",
        'PyMuPDF',
        'python-docx'
    ],
    dependency_links=[
        'https://pypi.org/simple/'
    ],
    entry_points={
        'console_scripts': [
            'GDriveOps=GDriveOps.GDhandler:main',
        ],
    },
    author='Hammed A. Akande',
    author_email='akandehammedadedamola@gmail.com',
    description='A package to handle Google Drive uploads and downloads.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/drhammed/GDriveOps',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)