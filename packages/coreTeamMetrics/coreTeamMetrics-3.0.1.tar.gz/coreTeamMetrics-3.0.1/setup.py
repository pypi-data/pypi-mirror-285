from setuptools import setup, find_packages

with open("README.md", "r") as f:
    description = f.read()

setup(
    name='coreTeamMetrics',
    version='3.0.1',
    description='A Prometheus metrics collector for runtime metrics',
    author='core-team',
    author_email='coreteam@example.com',
    packages=find_packages(),
    install_requires=[
        'prometheus_client',
    ],
    python_requires='>=3.6',
    long_description=description,
    long_description_content_type="text/markdown"
)