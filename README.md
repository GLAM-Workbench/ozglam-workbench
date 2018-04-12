# OzGLAM data workbench

**Please note this is experimental and unfinished. I'm still learning about the capabilities of Jupyter. Things might change radically!**

A collection of Jupyter notebooks to help you explore data from Australian GLAM institutions.

* You can browse here on GitHub.
* Play with it live on MyBinder [![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/wragge/ozglam-workbench/master)
* Run it from Docker

## Docker details

This creates a persistent data volume and runs the workbench image:

``` shell
docker run -it --name=Workbench -v WorkbenchData:/home/jovyan/workbench -p 8888:8888 wragge/ozglam-workbench
```

To restart using the same data volume:

``` shell
docker start -ai Workbench
```
