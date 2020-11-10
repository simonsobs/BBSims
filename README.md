# LB_mbs
Library for producing map based simulations for the LiteBIRD experiment

## Requirments

- numpy
- healpy
- pysm v3


## Install
The code is under development therefore to install it just use:

```bash
git clone https://github.com/NicolettaK/LB_mbs.git
[sudo] python setup.py develop [--user]
```

## Run
The library installs an executable file ```litebird_mbs```. In order to run, it needs a configuration file. A first example of such a file ```config_v0.py```is in the directory ```./lb_mbs/configs```

to run:

```
litebird_mbs --par_file=...path_to_repo/LB_mbs/lb_mbs/configs/config_v0.py
```
