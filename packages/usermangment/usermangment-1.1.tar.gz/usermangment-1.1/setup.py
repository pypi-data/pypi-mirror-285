from setuptools import setup, find_packages

setup(
    name='usermangment',
    version='1.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Django>=5.0',
        'django-bootstrap5',
        'pillow',
        'django-cleanup',
        'django-allauth',
        'django-htmx',
        'pyjwt',
        'cryptography',
    ],
    entry_points={
        'console_scripts': [
            'manage = manage:main',
        ],
    },
    author="Hamed Jamali",
    author_email="hamed.jamali.software@gmail.com",
    description="A Django project for user management.",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/hamed-jamali-software/usermangment",
    classifiers=[
        'Programming Language :: Python :: 3',
        'Framework :: Django',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)