# Mirage modules

This repository is a place to store my modules written for the mirage frame work.

Mirage can be forund here

https://homepages.laas.fr/rcayre/mirage-documentation/

## Install mirage

First of all, clone the repository :

```bash
git clone https://github.com/RCayre/mirage
```
Then, you can directly launch mirage using the following command (if the dependencies are installed):

```bash
cd mirage
sudo python3 setup.py install
```

## Install the modules from this repository

find the install path for mirage, for example

```bash

ls -lhs /usr/local/lib/python3.11/dist-packages/mirage-1.2-py3.11.egg/mirage

```

if the folder exists cd to the folder


```bash 

cd /usr/local/lib/python3.11/dist-packages/mirage-1.2-py3.11.egg/mirage

```

make a folder to do the download, download the folder

```bash

mkdir DEL
cd DEL
wget https://github.com/jrd3n/mirage_modules/archive/refs/heads/main.zip
unzip main.zip 
```

copy the modules (if applicable)

```bash

cp mirage_modules-main/modules/* ../modules/
```
copy the scenarios (if applicable)

```bash

cp mirage_modules-main/scenarios/* ../scenarios/
```

house keeping

```bash
cd ..
rm -r DEL/
```