SRCDIR="/Archive/Videos/Collection/2016/20160708 --- 08-Julio-2016 (Prueba Soporte GoPro HUD San Antonio)"
cd ..
#python hudint.py $1 -t "Subida desde Fresnedillas a San Antonio (Robledo)" -s -o -v "$SRCDIR/1246927351.fit" "$SRCDIR/GOPR0167.MP4" "$SRCDIR/climb.avi"
python hudint.py $1 -t "Subida desde Fresnedillas a San Antonio (Robledo)" -s -o -v config_white.xml "$SRCDIR/1246927351.fit" "$SRCDIR/GOPR0167.MP4" "climb.avi"

cd test
