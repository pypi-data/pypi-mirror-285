import numpy as np

def addGaussianNoiseBySTD(var_dataset, var_name, std):
    var_data = var_dataset[var_name]
    std = np.std(var_data) 
    noise = np.random.normal(loc=0, scale=std, size=var_data.shape)
    noisy_data = var_dataset + noise
    return noisy_data   

def addGaussianNoiseByDepthSTD(var_dataset, var_name):
    for depth in var_dataset[var_name].z.data:
        var_data = var_dataset[var_name].sel(z=depth)
        std = np.std(var_data) 
        noise = np.random.normal(loc=0, scale=std, size=var_data.shape)
        noisy_data = var_data + noise
        var_dataset[var_name].loc[{'z': depth}] = noisy_data
    return var_dataset