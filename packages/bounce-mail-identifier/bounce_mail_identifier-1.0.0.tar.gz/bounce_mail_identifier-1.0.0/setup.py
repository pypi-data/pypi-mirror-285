from setuptools import setup, find_packages

setup(
    name='bounce-mail-identifier',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'openpyxl',
    ],
    entry_points={
        'console_scripts': [
            'bounce-mail-identifier=bounce_mail_identifier.bounce_mail_handler:main',
        ],
    },
    author='Around With Us',
    author_email='mscrabe@gmail.com',
    description='A package to fetch bounce emails and save them to an Excel file',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    keywords=['Bounce Emails', 'Email Handling', 'Python package', 'Email Processing', 'Email Automation'],
)
