# Pyprobml VAE 

A collection of Variational AutoEncoders (VAEs) implemented in pytorch with focus on reproducibility and creating reusable blocks that can be used in any project. The aim of this project is to provide
a quick and simple working example for many of the cool VAE idea in the textbook. All the models are trained on the [CelebA dataset](http://mmlab.ie.cuhk.edu.hk/projects/CelebA.html)
for consistency and comparison. 

## Requirements
- Python >= 3.7
- PyTorch >= 1.8
- Pytorch Lightning  == 1.4.0
- CUDA enabled computing device

## To download this subdirectory only 

Copy the url of the subdirectory and past it to this [webstie](https://download-directory.github.io) and then download this subdirectory as a zipfile

## Instruction For Training The Model

### Download celeba data

**Important :** Make sure to get your kaggle.json from [these instructions](https://github.com/Kaggle/kaggle-api#api-credentials) then run 

```
mkdir /root/.kaggle 
cp kaggle.json /root/.kaggle/kaggle.json
chmod 600 /root/.kaggle/kaggle.json
rm kaggle.json
```

to copy kaggle.json into a folder first. 

### To Train Model

```
python run.py -config ./configs/vanilla_vae.yaml
```

## To compare and plot the results of different models

Use ```results.ipynb```
