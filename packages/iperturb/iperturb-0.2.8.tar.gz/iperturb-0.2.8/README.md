# iPerturb: An Introduction

## Overview

iPerturb is an efficient tool for integrating single-cell RNA sequencing (scRNA-seq) data with multiple samples and multiple conditions, focusing on removing batch effects while retaining condition-specific changes in gene expression. This document will introduce how to use iPerturb to process and analyze scRNA-seq datasets from different experimental conditions.

## Installation

Install using pip:

```bash
pip install iperturb
```

## Dataset Description

We applied iPerturb to analyze droplet-based scRNA-seq data from peripheral blood mononuclear cells (PBMCs). The dataset consists of two groups: one group includes peripheral blood cells treated with interferon-β (INF-β), and the other group includes untreated control cells. You can download the dataset from [here](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE96583).

Specifically, gene expression levels were measured from 8 experimental samples treated with INF-β (stimulated group; N = 7466 cells) and 8 control samples (control group; N = 6573 cells) to assess condition-specific changes in gene expression.

## Loading

Let's start by loading the required packages. We import the `iPerturb.iperturb` package as `iPerturb`. We also need to import the following two packages to ensure iPerturb works properly:

- `scanpy`: iPerturb is built on the `scanpy` framework and accepts single-cell data files in the h5ad format.
- `torch`: iPerturb uses `pytorch` to build the variational autoencoder and use `cuda` to accelerate the inference, we need to detect if cuda is avaliable.

```python
import iperturb as iPerturb
import torch
import scanpy as sc

cuda = torch.cuda.is_available()
if cuda:
    print('cuda is available')
else:
    print('cuda is not available')

anndata = sc.read_h5ad('/data/chenyz/iPerturb_project/data/PBMC.h5ad')
```
## Preprocessing

Data preprocessing of `anndata` included the following steps:

1. **Quality Control**: Removal of low-quality cells and genes (default: min_genes=200, min_cells=3).
   
2. **Normalization**: Standardizing gene expression data (default: `normalize_total()`, `log1p()`).
   
3. **Dataset initiation**: Batch, condition, and groundtruth (optional) information are added to `anndata.obs` and set as category types.

4. **Find highly variable genes**: Annotate highly variable genes to accelerate integration (default: n_top_genes=4000).


In iPerturb, we provide a unified function `preprocess.data_load()` to accomplish this:
```python
# Load necessary datasets and parameters such as batch_key, condition_key, and groundtruth_key (optional)
batch_key = 'batch_2'
condition_key = 'batch'
groundtruth_key = 'groundtruth'  # Used for calculating ARI
datasets,raw,var_names,index_names = iPerturb.preprocess.data_load(anndata, batch_key = batch_key ,condition_key = condition_key , groundtruth_key = groundtruth_key ,n_top_genes = 4000)

datasets.X = datasets.layers['counts'] # if mode = 'possion'
# datasets.X = datasets.layers['lognorm'] # if mode ='lognorm'
```
## Model initiating
After preprocessing the data, the next step is to initiate the model. Here are the steps to set up and initiate the iPerturb model:

1. **Create Hyperparameters**: We start by creating the hyperparameters for the model using the `utils.create_hyper()` function.

2. **Define Training Parameters**: We define the training parameters including the number of epochs and the optimizer. In this example, we use the Adam optimizer.

3. **Initialize the Model**: Next, we initialize the iPerturb model using the `model.model_init_ function()`. This function sets up the model with the specified hyperparameters, latent dimensions, optimizer, learning rate, and other parameters. Here are the explanation of Parameters:

- `hyper`: The hyperparameters created in step 1.
   
- `latent_dim1`, `latent_dim2`, `latent_dim3`: Dimensions of the latent variable of Z, Z_t and Z_s.
   
- `optimizer`: The optimizer used for training, in this case, Adam.
   
- `lr`: Learning rate for the optimizer.
   
- `gamma`: Learning rate decay factor.
   
- `milestones`: Epochs at which the learning rate is decayed.
   
- `set_seed`: Random seed for reproducibility.
   
- `cuda`: Boolean indicating whether to use GPU for training.
   
- `alpha`: Regularization parameter.

Finally, we got 3 key component as output to strat VAE infernce(reference by [Pyro](https://pyro.ai/)):
- `svi`: Stochastic Variational Inference (SVI) object used for optimizing the variational inference objective in the variational autoencoder (VAE) model.
  
- `scheduler`: Learning rate scheduler that adjusts the learning rate during training based on the specified milestones and gamma.
  
- `iPerturb_model`: The initialized iPerturb model, which includes the variational autoencoder (VAE) architecture configured with the specified hyperparameters and settings.

```python
# create hyperparameters
hyper = iPerturb.utils.create_hyper(datasets, var_names, index_names)
# train
epochs = 15
optimizer = torch.optim.Adam

svi, scheduler, iPerturb_model = iPerturb.model.model_init_(hyper, latent_dim1=100, latent_dim2=20, latent_dim3=20, 
                                                            optimizer=optimizer, lr=0.006, gamma=0.2, milestones=[20], 
                                                            set_seed=123, cuda=cuda, alpha=1e-4, mode='possion')
```
## Model training
Once the iPerturb model is initialized, we proceed to train the model using the `model.RUN()` function. The parameter `if_likelihood` is used to compute the model's t_logits. The model returns two results: `x_pred`, which represents the corrected matrix, and `reconstruct_data`, which represents the corrected AnnData.

iPerturb is computationally efficient, with a typical runtime of approximately 5-10 minutes in this example.
```python
x_pred, reconstruct_data = iPerturb.model.RUN(datasets, iPerturb_model, svi, scheduler, epochs, hyper, raw, cuda, batch_size=100, if_likelihood=True)

reconstruct_data.write(os.path.join(savepath, 'iPerturb.h5ad'))
```
    
`
