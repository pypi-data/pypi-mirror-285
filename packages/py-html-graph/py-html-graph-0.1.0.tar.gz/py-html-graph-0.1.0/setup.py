from setuptools import setup

with open("README.md", "r") as f:
    long_description = f.read()


setup(
    name='py-html-graph',
    version='0.1.0',
    author='Tiancheng Jiao',
    author_email='jtc1246@outlook.com',
    url='https://github.com/jtc1246/py-html-graph',
    description='A high-performance interactive numpy line chart viewer, good supplement for the awful matplotlib.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=['py_html_graph'],
    package_data={
        'py_html_graph': ['html/*', 'ssl/*']
    },
    install_requires=['matplotlib', 'myHttp', 'myBasics', 'mySecrets'],
    python_requires='>=3.9',
    platforms=["all"],
    license='GPL-2.0 License'
)
