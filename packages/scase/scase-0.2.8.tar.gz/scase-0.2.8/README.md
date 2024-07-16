# ScaSE

<p align="center">

[//]: # (    <img src="https://github.com/shaham-lab/SpectralNet/blob/main/figures/twomoons.png">)

ScaSE is The official PyTorch implementation of ScaSE from the paper ["Scalable and Generalizable Spectral Embedding via deep neural networks]().<br>
One of many applications of ScaSE is UMAP initialization, as shown in the following figure:<br>

[//]: # (<br><img src="docs/umap_plot.png"><br>)
<br><img src="https://github.com/shaham-lab/ScaSE/blob/main/docs/umap_plot.png"><br>

Initializing UMAP with ScaSE results in a similar embedding to the one obtained by UMAP itself (initialized with Spectral Embedding), but with a much faster runtime for a large number of samples.<br>

[//]: # (## Installation)

[//]: # (You can install the latest package version via)

[//]: # (```bash)
[//]: # (pip install spectralnet)
[//]: # (```)

## Installation
To install the package, simply use the following command:

```bash
pip install scase
```

## Usage

The basic functionality is quite intuitive and easy to use, e.g.,

```python
from scase import ScaSE

scase = ScaSE(n_components=10)  # n_components is the number of dimensions in the low-dimensional representation
scase.fit(X)  # X is the dataset and it should be a torch.Tensor
X_reduced = scase.transfrom(X)  # Get the low-dimensional representation of the dataset
Y_reduced = scase.transform(Y)  # Get the low-dimensional representation of a test dataset

```

You can read the code docs for more information and functionalities.<br>

Out of many applications, ScaSE can be used for UMAP initialization, Fiedler vector and value approximation, and Diffusion Maps approximation. The following is examples of how to use ScaSE for each of these applications:
### UMAP initialization

```python
from scase import ScaSE
from umap import UMAP

scase = ScaSE(n_components=2)
se = scase.fit_transform(X)
umap = UMAP(n_components=2, init=se)
X_reduced = umap.fit_transform(X)
```

### Fiedler vector and value approximation

```python
from scase import ScaSE

scase = ScaSE(n_components=1)
fiedlerVector = scase.fit_transform(X)
fiedlerValue = scase..get_eigenvalues()
```

### Diffusion Maps approximation

```python
from scase import ScaSE

scase = ScaSE(n_components=10)
diffusionMaps = scase.fit_transform(X, t=5)  # t is the diffusion time
```

## Running examples

In order to run the model on the moon dataset, you can either run the file, or using the command-line command:<br>
`python -m examples.reduce_moon`<br>
This will run the model on the moon dataset and plot the results.

The same can be done for the circles dataset:<br>
`python -m examples.reduce_circles`<br>




[//]: # (## Citation)

[//]: # ()
[//]: # (```)

[//]: # ()
[//]: # (@inproceedings{shaham2018,)

[//]: # (author = {Uri Shaham and Kelly Stanton and Henri Li and Boaz Nadler and Ronen Basri and Yuval Kluger},)

[//]: # (title = {SpectralNet: Spectral Clustering Using Deep Neural Networks},)

[//]: # (booktitle = {Proc. ICLR 2018},)

[//]: # (year = {2018})

[//]: # (})

[//]: # ()
[//]: # (```)
