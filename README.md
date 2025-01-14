# jupyterlite-fastf1

This template repository provides an example of running `fastf1` (*not live timing*) in a browser based JupyterLite environment. JupyterLite provides access to JupyterLab and Jupyter notebook environments, with in-browser code exeuction using a Pyodide (WASM Python) environment.

*Although `xeus-python` kernels are availble for JupyterLite, `fastf1` currently only works in a `pyodide` kernel.*

In order to run `fastf1` in a `pyodide` envrionment, you need to manually install several dependencies. See the [`demo.ipynb`](./demo.ipynb) notebook for an example.

Guide to using this reposistory available as a Jupyter Book / ebook [here](https://f1datajunkie.github.io/book).

Example JupyterLite/JupyterLab environment: [view demo](https://f1datajunkie.github.io/jupyterlite-fastf1/lab/index.html?path=demo.ipynb)

Example JupyterLite/notebook environment: [view demo](https://f1datajunkie.github.io/jupyterlite-fastf1/tree/index.html?path=demo.ipynb)

This template repository also includes a Github Action to create the JupyterLite environment and publish it to GitHub Pages. The action also publishes a Jupyter Book generated from specified files in the repository to the `book/` path on the Pages site.

__Related blog posts:__

- [Using fastf1 F1 data analysis package in JupyterLite](https://blog.ouseful.info/2025/01/13/using-fastf1-f1-data-analysis-package-in-jupyterlite/)
