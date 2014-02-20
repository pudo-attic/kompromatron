from setuptools import setup, find_packages


setup(
    name='kompromatron',
    version='0.1',
    description="Who's in charge in Germany...",
    long_description=None,
    classifiers=[],
    keywords='',
    author='Friedrich Lindenberg, Stefan Wehrmeyer',
    author_email='friedrich@pudo.org',
    url='https://github.com/pudo/kompromatron',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    zip_safe=False,
    install_requires=[
        "grano-client>=0.2",
        "Flask==0.10.1",
        "Flask-Assets==0.8"
    ],
    tests_require=[],
    entry_points=\
    """ """,
)
