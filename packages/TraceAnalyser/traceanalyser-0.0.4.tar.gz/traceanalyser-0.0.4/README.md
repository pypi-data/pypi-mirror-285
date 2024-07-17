# TraceAnalyser

[![License MIT](https://img.shields.io/pypi/l/TraceAnalyser.svg?color=green)](https://github.com/piedrro/TraceAnalyser/raw/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/TraceAnalyser.svg?color=green)](https://pypi.org/project/TraceAnalyser)
[![Python Version](https://img.shields.io/pypi/pyversions/TraceAnalyser.svg?color=green)](https://python.org)
[![tests](https://github.com/piedrro/TraceAnalyser/workflows/tests/badge.svg)](https://github.com/piedrro/TraceAnalyser/actions)
[![codecov](https://codecov.io/gh/piedrro/TraceAnalyser/branch/main/graph/badge.svg)](https://codecov.io/gh/piedrro/TraceAnalyser)

A standalone application for analysing time series data, which includes features for processing/labelling/filtering traces and facilitates the detection of hidden states using **Hidden Markov Modelling** (HMM). 
It also includes embdedded pre-trained Deep Learning (InceptionTime) models for classifying/labelling traces.

This is still undergoing development, so some features may not work as expected.

This was built by Dr Piers Turner from the Kapanidis Lab, University of Oxford.

----------------------------------

<!--
Don't miss the full getting started guide to set up your new package:
https://github.com/napari/cookiecutter-napari-plugin#getting-started

and review the napari docs for plugin developers:
https://napari.org/stable/plugins/index.html
-->

## Installation

You can install `TraceAnalyser` via [PyPI]:

    conda create –-name TraceAnalyser python==3.9
    conda activate TraceAnalyser

    pip install TraceAnalyser

You can install `TraceAnalyser` via [GitHub]:

    conda create –-name TraceAnalyser python==3.9
    conda activate TraceAnalyser
    conda install -c anaconda git
    conda update --all

    pip install git+https://github.com/piedrro/TraceAnalyser.git

## To install **MATLAB** engine (Windows):

python 3.9 requires MATLAB >= 2021b

MATLAB compatibility: https://uk.mathworks.com/support/requirements/python-compatibility.html

    pip install matlabengine

This will likely fail due to a MATLAB version issue. 
Read the traceback, and install the recomended verison. 
Then try again:

    pip install matlabengine==XXXX

## Terminal Commands

To launch the Trace Analyser App:

    analysis

To launch an ebFRET instance (requires matlab engine installation):
    
    ebFRET

## Contributing

Contributions are very welcome. Tests can be run with [tox], please ensure
the coverage at least stays the same before you submit a pull request.

## License

Distributed under the terms of the [MIT] license,
"TraceAnalyser" is free and open source software

## Issues

If you encounter any problems, please [file an issue] along with a detailed description.

[napari]: https://github.com/napari/napari
[Cookiecutter]: https://github.com/audreyr/cookiecutter
[@napari]: https://github.com/napari
[MIT]: http://opensource.org/licenses/MIT
[BSD-3]: http://opensource.org/licenses/BSD-3-Clause
[GNU GPL v3.0]: http://www.gnu.org/licenses/gpl-3.0.txt
[GNU LGPL v3.0]: http://www.gnu.org/licenses/lgpl-3.0.txt
[Apache Software License 2.0]: http://www.apache.org/licenses/LICENSE-2.0
[Mozilla Public License 2.0]: https://www.mozilla.org/media/MPL/2.0/index.txt
[cookiecutter-napari-plugin]: https://github.com/napari/cookiecutter-napari-plugin

[file an issue]: https://github.com/piedrro/TraceAnalyser/issues

[napari]: https://github.com/napari/napari
[tox]: https://tox.readthedocs.io/en/latest/
[pip]: https://pypi.org/project/pip/
[PyPI]: https://pypi.org/
