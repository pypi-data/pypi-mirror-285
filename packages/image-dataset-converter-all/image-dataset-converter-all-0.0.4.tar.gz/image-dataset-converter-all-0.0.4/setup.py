from setuptools import setup


def _read(f):
    """
    Reads in the content of the file.
    :param f: the file to read
    :type f: str
    :return: the content
    :rtype: str
    """
    return open(f, 'rb').read()


setup(
    name="image-dataset-converter-all",
    description="Meta-library that combines all image-dataset-converter libraries.",
    long_description=(
            _read('DESCRIPTION.rst') + b'\n' +
            _read('CHANGES.rst')).decode('utf-8'),
    url="https://github.com/waikato-datamining/image-dataset-converter-all",
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Scientific/Engineering :: Image Processing',
    ],
    license='MIT License',
    install_requires=[
        "image-dataset-converter>=0.0.4",
        "image-dataset-converter-imgaug>=0.0.4",
        "image-dataset-converter-imgstats>=0.0.1",
        "image-dataset-converter-imgvis>=0.0.2",
        "image-dataset-converter-pdf>=0.0.1",
        "image-dataset-converter-redis>=0.0.2",
        "image-dataset-converter-video>=0.0.1",
    ],
    version="0.0.4",
    author='Peter Reutemann',
    author_email='fracpete@waikato.ac.nz',
)
