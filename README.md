# RL-based-ABR-streaming

### Getting Started

For convienience purposes, a Makefile was written in order to simplify the process of 
setting up the repo. Note, this repo was developed and run on an Ubuntu 22 system 
as well as a WSL Ubuntu 22 system. The code is undtested on windows and mac.  

Stable Baselines requires several packages. They can be installed with:
```
sudo make setup
``` 

Next, create a python environment with the command below. This installs all python packages 
required in the `.env` environment, and it also adds the environment to the jupyter notebook
kernels. Make sure to select the `.env` enviroment in vscode or in jupyter lab when running
this project. 
```
make env-create
```

If the environment is ever messed up, it can be wiped with:
```
make env-delete
```


### Data:
Several network traces and movies have been downloaded for this experiment.
They are organized in the following manor:

* `/data/3Glogs`: 3G network traces
* `/data/4Glogs`: 4G network traces
* `/data/sd_fs`: sd FCC web traces
* `/data/hd_fs`: hd FCC web traces
* `/data/bbb.json`: dash manifest of the Big Buck Bunny movie; 4k version is also there
