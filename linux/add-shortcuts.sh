#!/bin/bash
LINUX_DIR=$(dirname $(realpath $0))
STORY_DIR=$(dirname $LINUX_DIR)

echo $LINUX_DIR
echo $STORY_DIR

echo -e "#!/bin/bash\n\
cd $STORY_DIR\n\
python main.py\n\
" > $LINUX_DIR/storypixies.sh

echo -e "#!/bin/bash\n\
cd $STORY_DIR\n\
python main.py kids-mode\n\
" > $LINUX_DIR/kidmode.sh

chmod +x $LINUX_DIR/kidmode.sh
chmod +x $LINUX_DIR/storypixies.sh

echo -e "[Desktop Entry]\n\
Version=1.0\n\
Type=Application\n\
Terminal=false\n\
Exec=$STORY_DIR/linux/storypixies.sh\n\
Name=Storypixies Full Mode\n\
Comment=Storypixies Full Mode\n\
Icon=$STORY_DIR/images/storypixies.png\n\
" > ~/Desktop/Storypixies.desktop

echo -e "[Desktop Entry]\n\
Version=1.0\n\
Type=Application\n\
Terminal=false\n\
Exec=$STORY_DIR/linux/kidmode.sh\n\
Name=Storypixies Kids Mode\n\
Comment=Storypixies Kids Mode\n\
Icon=$STORY_DIR/images/storypixies.png\n\
" > ~/Desktop/StorypixiesKids.desktop

chmod +x ~/Desktop/Storypixies.desktop
chmod +x ~/Desktop/StorypixiesKids.desktop
