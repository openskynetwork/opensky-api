# OpenSky API Documentation

We are using [Sphinx](http://www.sphinx-doc.org/).

The latest compiled version of this documentation is accessible [here](https://opensky-network.org/apidoc)


## Build<sup>[1](#fn1)</sup>

If you need to build the docs, follow these steps:

1. Install Sphinx with your package manager or any other method described [here](http://www.sphinx-doc.org/en/stable/install.html).

    apt-get install python-sphinx

2. Install the [Read the Docs Theme](https://github.com/snide/sphinx_rtd_theme)

    pip install sphinx_rtd_theme

3. Create the Sphinx documentation and Javadoc<sup>[2](#fn2)</sup>

    make

The results can be found in ``free/_build/html``.

<a name="fn1">[1]</a>: Package installation examples for Ubuntu
<a name="fn2">[2]</a>: If you don't have ```make``` or ```maven```: ```apt-get install build-essential maven```
