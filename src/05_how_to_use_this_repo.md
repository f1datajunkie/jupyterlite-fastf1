# How To Use This Repository

The [`f1datajunkie/jupyterlite-fastf1/`](https://github.com/f1datajunkie/jupyterlite-fastf1/) repository is defined as a template repository, which means you can easily clone it and use it to construct your own JupyterLite environment.

The repository includes a Github Action that will build an appropriately configured JupyterLite site.

The intention is also to publish a pre-configured `xeus-python` kernel bundling all required packages, but this is currently waiting on the appearance of a couple of packages in *emscripten-forge*.

Notes on getting `fastf1` running in JupyterLite:

- __unsupported dependencies__: the `fastf1` package has a top-level requirement on the `rapidfuzz` package. If `rapidfuzz` isn’t available, you can't use `fastf1`. BUT, there is no generic any platform wheel available for `rapidfuzz`, and (currently) no *emscripten-forge* build available, which means we can’t easily install the package. But after raising an issue on the repo, a pyodide wasm build was made available there, so now we can install the package manually in a Pyodide kernel. This can either be done via a locally vendored package, or by loading the package direct from a URL.

```python
# Pyodide kernel
import micropip
await micropip.install("emfs:/drive/packages/rapidfuzz-3.11.0-cp312-cp312-pyodide_2024_0_wasm32.whl")
# The wheel can also be downloaded from a URL
# The Github action associated with the repo will publish the wheel
# to a wheelhouse on the repo's Github Pages site on the path: ./wheelhouse/
#await micropip.install("https://f1datajunkie.github.io/jupyterlite-fastf1/wheelhouse/rapidfuzz-3.11.0-cp312-cp312-pyodide_2024_0_wasm32.whl")

# Now we can install and import the fastf1 package
%pip install fastf1
import fastf1
```

- __CORS issues__: which is to say, *Cross-Origin Request* issues. The `formula1.com` API doesn’t like cross-origin requests, which means we can’t directly request data from that source from our JupyerLite web environment. Instead, we need to make the request via a proxy. I had previously produced a very simple package for generating proxy URLs based around the `corsproxy.io` service, but that was no direct way of using those URLs in the `fastf1` package. But given that I know it’s possible to build a package that can monkey patch the requests package to add cacheing to it (the `requests-cache` package, which is used by fastf1) I wondered whether we could do something similar to patch fastf1 that would allow us to make proxied requests against particular domains. So I asked `claude.ai` to help, and it generated class to do that for me, which I bundled in the `jupyterlite-simple-cors-proxy` package [here](https://github.com/innovationOUtside/jupyterlite-simple-cors-proxy/blob/main/jupyterlite_simple_cors_proxy/fastf1_proxy.py). Here’s how we can use it:

```python
%pip install jupyterlite_simple_cors_proxy
 
from jupyterlite_simple_cors_proxy.fastf1_proxy import enable_cors_proxy as fastf1_cors_proxy
 
# Then enable a CORS proxy with or without debug logging
fastf1_cors_proxy(
    domains=["api.formula1.com", "livetiming.formula1.com"],
    # debug=True,
    # By default, the proxy path is:
    # https://api.allorigins.win/raw?url=
    # Or we can specify our own
    proxy_url="https://corsproxy.io/",
)
 
# fastf1 will now make proxied requests on specified domains.
```

- __cache issues__: the recommended way of using `fastf1` is to cache api calls. However, `sqlite`, which is used to maintain an index to the cached files, doesn’t play nicely with the JupyterLite homedir filesystem, so we need to fettle how we handle the cache by using another top level directory, either the top level `/tmp` directory, or a directory we create ourselves. To persist data across JupyterLite sessions, we need to manually copy the cache directory to/from the JupyterLite `/drive` directory, which is saved to browser storage.

```python
# Create a cache dir
import os
CACHE_DIR = "/fastf1cache"
if not os.path.exists(CACHE_DIR):
    os.mkdir(CACHE_DIR)
 
# If we have previously created and stashed a cache dir:
# import shutil
# PERSISTED_CACHE_DIR = "/drive/fasff1cache"
# shutil.copytree(PERSISTED_CACHE_DIR, CACHE_DIR)
# Stash cachedir as:
# shutil.copytree(CACHE_DIR, PERSISTED_CACHE_DIR)
 
fastf1.Cache.enable_cache(CACHE_DIR)
```

## The Jupyter Book Site

The GitHub Action provided in the template repository also publishes a Jupyter Book on the Github Pages `./book` path.

The intention is to eventually provide a working example of using [`thebe-lite`](https://github.com/jupyter-book/thebe) to support `fastf1` code execution in the book web pages.

## The Python wheelhouse

The GitHub Action provided in the template repository also publishes a Python package wheelhouse on the Github Pages `./wheelhouse` path.

The intention is to eventually provide additional actions that can compile Python packages to appropriate WASM wheels so they can be used in the `pyodide` and `xeus-python` kernels if appropriate wheels are not available elsewhere.

## `R` support

I'd also like to be able to demo a [JupyterLite R kernel](https://github.com/r-wasm/jupyterlite-webr-kernel) running [`f1dataR`](https://github.com/SCasanova/f1dataR), and R based wrapper for `fastf1`. To use `fastf1` in an R context probably requires something like a WASM version of `reticulate` that could talk to `pyodide` and run `fastf1` there, but as yet, I don't think such a thing is available...

## `.devcontainer` support

In passing, I have added a devcontainer config script to support the creation of a preconfigured containerised environment running `fastf1` that can be used with Docker via VS Code on your desktop or run via Github Codespaces. *This is currently untested.*

