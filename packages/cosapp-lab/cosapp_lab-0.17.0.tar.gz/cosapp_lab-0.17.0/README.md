# CosApp Lab - Toolbox for managing and deploying CoSApp powered dashboards.

[![Readthedocs](https://readthedocs.org/projects/cosapp-lab/badge/?version=latest)](https://cosapp-lab.readthedocs.io/en/latest/)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gl/cosapp%2Fcosapp_lab/master?urlpath=lab/tree/examples/SysExplorer.ipynb)

## Introduction

The primary goal of **CoSApp Lab** is to help users transform existing CoSApp
modules into interactive dashboards, with almost no additional development or
configuration.

### Examples

#### Using CosApp Lab in JupyterLab

CoSApp Lab provides a JupyterLab extension named **SysExplorer** for creating interactive dashboards. This extension allows users to dynamically customize the layout and fill their dashboard with multiple predefined widgets, such as charts, controllers (sliders, _etc._), 3D visualization panels...

![CosApp Lab in JupyterLab](./docs/img/cosapp_lab.gif)

#### Using CosApp Lab standalone mode

Dashboards defined with **SysExplorer** in JupyterLab can also be exported into libraries and served by CoSApp Lab as web applications.

![CoSApp Lab standalone](./docs/img/cosapp_lab_all.gif)

## Documentation

A more detailed **CoSApp Lab** documentation is available at:

https://cosapp-lab.readthedocs.io/

## Installation

### Stable release

The easiest way to obtain `cosapp_lab` is to install the conda package:

```shell
conda install -c conda-forge cosapp_lab
```

`cosapp_lab` is also available on PyPI. However, since `pythonocc-core` is not, users can install `cosapp_lab` with _pip_, but the 3D viewer widget will not work.

```shell
pip install cosapp-lab
```

`JupyterLab` is not a direct dependency of `cosapp_lab`, but users need to have JupyterLab (>3.0) in order to create CoSApp dashboard in notebooks.

### Development

#### Setup development environment

```shell
    # create a new conda environment
    conda create -n cosapplab -c conda-forge python jupyterlab nodejs
    conda activate cosapplab

    # download cosapp_lab from gitlab
    git clone --recursive https://gitlab.com/cosapp/cosapp_lab.git

    # install JS dependencies, build and install JupyterLab extension in development mode
    cd cosapp_lab
    npm run install
    npm run build:all
    npm run install:extension

    # install cosapp_lab in editable mode
    python -m pip install -e .
```

#### Testing

```shell
    # Test python code
    python -m pytest

    # Test typescript code
    npm run test
```

#### Build documents

```shell
cd docs
sphinx-build -b html -d _build/doctrees . _build
```
