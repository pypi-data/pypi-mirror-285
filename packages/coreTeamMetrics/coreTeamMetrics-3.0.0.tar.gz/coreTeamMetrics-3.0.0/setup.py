from setuptools import setup, find_packages

setup(
    name='coreTeamMetrics',
    version='3.0.0',
    description='A Prometheus metrics collector for runtime metrics',
    author='core-team',
    author_email='coreteam@example.com',
    packages=find_packages(),
    install_requires=[
        'prometheus_client',
    ],
    python_requires='>=3.6',
)