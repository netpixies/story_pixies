# Storypixies

## Video Tour
Want to check it out before installing? See the [Storypixies Tour](https://youtu.be/kmsz7FFOG1o)

## Installation

### Python version

Storypixies currently uses Python 2.7. While Kivy supports Python 3, it is not at the same level as the support for Python 2.7.

### Current Supported Platforms
#### Mac

- Download the dmg (330MB) from [Google Drive](https://drive.google.com/open?id=1m6WMrFLurgOJdwwa2RJ3AjCDORFY7evU) - md5sum 65a4f272f8e4f4e3d57676967a12a7f1
- Open the dmg and drag to Applications
- Under Applications, right click and open storypixies
- Uninstall by moving the Storypixies application to the trash

#### Ubuntu Linux
It is recommended to use a VM.

- The following link is summed up below. [Install Kivy](https://kivy.org/doc/stable/installation/installation-linux.html)

```
sudo add-apt-repository ppa:kivy-team/kivy
sudo apt-get update
sudo apt-get install -y python-kivy
```
- Install gstreamer for audio, video

```
sudo apt-get install -y \
    libgstreamer1.0 \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good
```
- Install dependencies

```
sudo apt-get install -y python-pip git
sudo pip install pathlib2
```

- Clone the repo

```
git clone https://github.com/netpixies/storypixies.git
```

- Run main

```
cd storypixies
python main.py
```

#### Windows
Not yet supported

#### Android and IOS
Not yet supported
