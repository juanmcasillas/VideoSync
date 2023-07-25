SRCDIR="/Archive/Videos/Collection/2016/20160713 --- 13-Julio-2016 (Pruebas Soporte Gopro HUD MTB)"
cd ..
#python hudint.py $1 -t "Bajada desde las Minas de Colmenar al cementerio" -s -o -v "$SRCDIR/1254561415.fit" "$SRCDIR/GOPR0205.MP4" "$SRCDIR/downhill.avi"
#200
python hudint.py $1 -t "Bajada desde las Minas de Colmenar al cementerio" -s -v -o 0 config_white.xml "$SRCDIR/1254561415.fit" "$SRCDIR/GOPR0205.MP4" "downhill.avi"

cd test
