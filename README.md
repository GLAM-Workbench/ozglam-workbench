# OzGLAM data workbench

**Please note this is experimental and unfinished. I'm still learning about the capabilities of Jupyter. Things might change radically!**

A collection of Jupyter notebooks to help you explore data from Australian GLAM institutions.

### View on GitHub

You can view the contents on GitHub, but note that these will be static versions so you won't be able to run any of the code.

### Run locally with Jupyter

If you have Jupyter installed, you can clone this repository, and then run Jupyter:

```
git clone https://github.com/wragge/ozglam-workbench.git
cd ozglam-workbench
jupyter notebook
```

### Run online with MyBinder

To use a live version without installing any software, try MyBinder:

[![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/wragge/ozglam-workbench/master)

MyBinder launches the notebooks in a custom computing environment with all the software you'll need pre-installed. But note that these environments aren't persistent, so you'll need to make sure you download any data you want to keep.

### Run locally with Docker

I've created a Docker image that includes these notebooks and all the necessary software. Assuming you have Docker installed, just open up a terminal and run:

``` shell
docker run -it --name=Workbench -v WorkbenchData:/home/jovyan/workbench -p 8888:8888 wragge/ozglam-workbench
```

This creates a persistent data volume and runs the workbench image. Once Jupyter starts up it'll display a url in the terminal that looks something like:

```
http://localhost:8888/?token=262718512d11cc3efcb1b2878f4jja9uca071924e328d554
```

Just copy and paste this into your browser to open the notebooks.

To restart the `WorkBench` container using the same data volume:

``` shell
docker start -ai Workbench
```
