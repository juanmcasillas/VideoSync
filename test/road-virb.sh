SRCDIR="/Archive/Videos/Collection/2016/20160807 --- 07-Agosto-2016 (Carretera - Cenicientos)"
cd ..
#python hudint.py $1 -t "Subida desde Fresnedillas a San Antonio (Robledo)" -s -o -v "$SRCDIR/1246927351.fit" "$SRCDIR/GOPR0167.MP4" "$SRCDIR/climb.avi"
python hudint.py $1 -t "Bajada desde el Encinar del Alberche al cruce de Almorox" -s -v virb.xml "$SRCDIR/data.fit" "$SRCDIR/GOPR0352.MP4" "climb.avi"

cd test
