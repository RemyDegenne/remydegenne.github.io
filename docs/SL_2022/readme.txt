To run the notebook locally, download the .ipynb file and install the required libraries, as explained below.

    Setup virtual environment (optional but recommended):

conda create -n rltutorials python=3.8
conda activate rltutorials

	Install required libraries:

pip install jupyterlab
pip install git+https://github.com/rlberry-py/rlberry.git@v0.3.0#egg=rlberry[default]

	Install videos stuff

pip install ffmpeg-python pyvirtualdisplay
apt-get install -y xvfb python-opengl ffmpeg  

	Create a repository for videos inside the repository in which you will run the notebook 

mkdir videos

    Then you are all set to start the notebook, running the usual "jupyter notebook" command 