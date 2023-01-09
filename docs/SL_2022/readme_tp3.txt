	Go to the folder in which you want to work. Create and activate a new conda environment:

conda create -n dqn python=3.9
conda activate dqn

	To deactivate the environnement (don't do that now), use 'conda deactivate'.

	Install python packages:

pip install jupyterlab
pip install -r https://raw.githubusercontent.com/rlberry-py/rlberry/main/requirements.txt
pip install git+https://github.com/rlberry-py/rlberry.git
pip install ipywidgets pyglet==1.5.27

	Install ffmpeg (for videos)
	For windows, visit https://ffmpeg.org/download.html, download ffmpeg and place ffmpeg.exe in your work folder
	For linux, type

apt-get install ffmpeg

	Once the installation is done, open a notebook

jupyter notebook