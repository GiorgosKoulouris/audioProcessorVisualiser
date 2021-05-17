# AudioProcessor Visualiser 
![GitHub top language](https://img.shields.io/github/languages/top/GiorgosKoulouris/audioProcessorVisualiser) 
![GitHub last commit](https://img.shields.io/github/last-commit/GiorgosKoulouris/audioProcessorVisualiser)

[comment]: <> (![GitHub commit activity]&#40;https://img.shields.io/github/commit-activity/w/GiorgosKoulouris/audioProcessorVisualiser&#41;)

***
## Description
AudioProcessor Visualiser is an under construction open-source app that has the intention of visualising the impact that
a block of DSP code has on a given audio signal. User will be able to load a local audio file and process it 
(or a part of it) using his own implementation of the code that will do the actual signal processing. After that, he 
will be able to see the impact of the code regarding its frequency response and energy/amplitude footprint.

___

### Languages and Libraries
AudioProcessor Visualiser is a project coded using entirely Python. It currently depends on high-level libraries such as
[librosa](https://librosa.org/) and [matplotlib](https://matplotlib.org/) for functions such as loading audio files and
"plotting".

___

### Download

Although the project is in an early stage, feel free to use or manipulate the app. Just clone the repo and install all 
the necessary dependencies using 

`python -m pip install -r Requirements.txt` 

If you install the dependencies in an environment with wheel installed, an empty pip cache directory is suggested:

`rm -rf $(pip cache dir)` and then `python -m pip install -r Requirements.txt`


---

### Contributing

Please, keep in mind that I started the AudioProcessor Visualiser project (as well as learning Python) as a side project 
to help myself fine tune my C++ DSP coding. Plus, I have minimal experience in the fields of Software and Computer Engineering. 
So please feel free to contribute either by proposing changes and features (by commenting or via a pull request), or just 
by commenting out bad code craftsmanship.



***


<img alt="GitHub followers" src="https://img.shields.io/github/followers/GiorgosKoulouris?style=social">
