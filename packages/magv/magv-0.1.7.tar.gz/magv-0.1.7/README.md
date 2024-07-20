## Mangrove - A PostgreSQL Extension Manager

This is a PostgreSQL extension manager, a command-line tool to download and install PostgreSQL extensions. You can download extension supported by [PGXN](https://pgxn.org/) or [Mangrove Index](https://atomgit.com/haorongxu/magv-index).

## Installation

Mangrove is available on [Github](https://github.com/HaorongX/magv/), [AtomGIT](https://atomgit.com/zouxiangneihe/Mangrove), and [PyPI](https://pypi.org/project/magv/). It can be installed via `pip`
```
pip3 install magv
```

Then execute `python3 -m magv' and `sudo python3 -m magv` to perform initialization. You shall see a warning message in your console after initialization.

```
WARNING: YOU SHOULD CHANGE YOUR CONFIGURE FILE MANUALLY AT ~/.magv/config.json TO USE MANGROVE
```

By the way, you may specify a shell script for Mangrove to run when the program starts. You may specify this script in your configure file using "Postscript" option, here is an example:

```
{
    "Index-Repo" : "https://atomgit.com/haorongxu/magv-index.git",
    "Postscript" : "~/test.sh"
}
```

#### Upgrading

You may upgrade mangrove by running `pip3 install magv --upgrade`. But if you are using PyPI mirror you might **NOT** get the latest version.

## Usage

> Tips: You can find the usage of `magv` by executing `magv -h`

### Searching

```
python3 -m magv -s/--search [extension]
```
This command returns a list of extensions which names contains `[extension]`.

**e.g.**
![search_eg](img/search.png)

### Downloading

```
python3 -m magv -d/--download [extension]
```
Similar to searching command, this function also gives you a list of extensions, then you'll be asked to specify which version to download. Downloaded file is stored in `~/.magv/`

### Installing

```
sudo python3 -m magv -i/--install [extension]
```
This function does pretty much the same job as downloading function, but it automatically install the extension. (However, you'll need to install all required library manually). You may also install an extension from a local folder by add argument `-p [path to extension]`.

WARNING: In case you need to install an extension from local folder with `root` permission, please always specify -p arugument if you ran `magv -d` with other users. Nevertheless, remember to set $PATH appropriately for root.

**e.g.**

![installeg](img/install.png)
![installeg2](img/install2.png)

### Get Involved

You can upload you own extension to [Mangrove Index](https://atomgit.com/zouxiangneihe/magv-index)

And you can make contribution to Mangrove by creating a PULL REQUEST.