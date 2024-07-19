from setuptools import setup, find_packages

with open("README.md", "r") as f:
    description = f.read()

setup(
    name='python_runtime_metrics',
    version='1.2.1',
    description='A Prometheus metrics collector for runtime metrics',
    author='medhun',
    author_email='medhun@example.com',
    packages=find_packages(),
    install_requires=[
        'prometheus_client',
    ],
    python_requires='>=3.6',
    long_description=description,
    long_description_content_type="text/markdown"
)