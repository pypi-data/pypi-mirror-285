[![PyPi version](https://img.shields.io/pypi/v/pqdata)](https://pypi.org/project/pqdata)

# pqdata

Experimental Parquet-based I/O for [scverse](https://scverse.org) data structures.

## Installation

```
pip install pqdata
# or
pip install git+https://github.com/gtca/pqdata
```

> [!WARNING]
> This package is experimental, and API can change between versions as well as the file structure.

## Motivation

TODO

## Features and integrations

TODO

### I/O

[Example notebook](/docs/examples/pqdata-serialization-intro.ipynb). I/O with pqdata works like this:

```py
from pqdata import write_anndata, write_mudata
write_anndata(adata, "pbmc3k_anndata.pqdata")
write_mudata(mdata, "pbmc5k_citeseq_mudata.pqdata")

from pqdata import read_anndata, read_mudata
adata = read_anndata("pbmc3k_anndata.pqdata")
mdata = read_mudata("pbmc5k_citeseq_mudata.pqdata")
```
