cd .. 

# ##
# SRCDIR="/Archive/Videos/Collection/2016/20160708 --- 08-Julio-2016 (Prueba Soporte GoPro HUD San Antonio)"
# python hudint.py $1 -t "Subida desde Fresnedillas a San Antonio (Robledo)" -s -o  config_white.xml "$SRCDIR/1246927351.fit" "$SRCDIR/GOPR0167.MP4" "$SRCDIR/san-antonio-road-climb.avi"
# python hudint.py $1 -t "Bajada desde San Antonio a Robledo" -s -o  config_white.xml "$SRCDIR/1246927351.fit" "$SRCDIR/GOPR0168.MP4" "$SRCDIR/san-antonio-road-downhill.avi"
#
# ##
SRCDIR="/Archive/Videos/Collection/2016/20160713 --- 13-Julio-2016 (Pruebas Soporte Gopro HUD MTB)"
#done #python hudint.py $1 -t "Bajada desde las Minas de Colmenar al cementerio" -s  config_interpolated.xml "$SRCDIR/1254561415.fit" "$SRCDIR/GOPR0205.MP4" "$SRCDIR/colmenar-mtb-downhill.avi"
#
#
# ##
# SRCDIR="/Archive/Videos/Collection/2016/20160717 --- 17-Julio-2016 (Pruebas Soporte Gopro HUD Casillas)"
# python hudint.py $1 -t "Subida desde Sotillo hacia Casillas" -s -o  config_white.xml "$SRCDIR/data.fit"  "$SRCDIR/GOPR0207.MP4" "$SRCDIR/climb-casillas.avi"
# python hudint.py $1 -t "Bajada desde el puerto hacia Sotillo" -s -o  config_white.xml "$SRCDIR/data.fit"  "$SRCDIR/GOPR0208.MP4" "$SRCDIR/downhill-casillas.avi"
# python hudint.py $1 -t "Bajada desde Cadalso hacia la M501" -s -o  config_white.xml "$SRCDIR/data.fit"  "$SRCDIR/GOPR0209.MP4" "$SRCDIR/downhill-cadalso.avi"
# python hudint.py $1 -t "Caza y sprint en la M501" -s -o  config_white.xml "$SRCDIR/data.fit"  "$SRCDIR/GOPR0240.MP4" "$SRCDIR/chase-M501.avi"
#
SRCDIR="/Archive/Videos/Collection/2016/20160727 --- 27-Julio-2016 (Pruebas Soporte Manillar HUD Colmenar)"
## WITH OFFSET, THE SPEED IS CALCULATED WRONG (low)
#python hudint.py $1 -t "Bajada desde Chapineria al cruce" -s -o 60 config_white.xml "$SRCDIR/data.fit"  "$SRCDIR/GOPR0241.MP4" "$SRCDIR/downhill-chapineria-cruce-e.avi"
python hudint.py $1 -t "Bajada desde Chapineria al cruce" -s config_white.xml "$SRCDIR/data.fit"  "$SRCDIR/GOPR0241.MP4" "$SRCDIR/downhill-chapineria-cruce-e.avi"


#
# SRCDIR="/Archive/Videos/Collection/2016/20160730 --- 30-Julio-2016 (Pruebas Soporte HUD Brunete)"
# python hudint.py $1 -t "Bajada de la Almenara a Robledo" -s -o  config_white.xml "$SRCDIR/data.fit"  "$SRCDIR/GOPR0242.MP4" "$SRCDIR/downhill-almenara-robledo-e.avi"
# python hudint.py $1 -t "Bajada desde la Cruz Verde a Zarzalejo" -s -o  config_white.xml "$SRCDIR/data.fit"  "$SRCDIR/GOPR0243.MP4" "$SRCDIR/downhill-cv-zarzalejo-e.avi"
# python hudint.py $1 -t "Bajada Zarzalejo a la estacion" -s   config_white.xml "$SRCDIR/data.fit"  "$SRCDIR/GOPR0244.MP4" "$SRCDIR/downhill-zarzalejo-estacion-e.avi"
#

SRCDIR="/Archive/Videos/Collection/2016/20160806 --- 06-Agosto-2016 (Carretera - Cuca - Cesar - Robledo)"
#done python hudint.py $1 -t "Bajada de Fresnedillas a Zarzalejo" -s   virb.xml "$SRCDIR/data.fit"  "$SRCDIR/GOPR0245.MP4" "$SRCDIR/downhill-fres-zarzalejo.avi"


SRCDIR="/Archive/Videos/Collection/2016/20160807 --- 07-Agosto-2016 (Carretera - Cenicientos)"
#done python hudint.py $1 -t "Bajada del Encinar a la rotonda de Almorox" -s  virb.xml "$SRCDIR/data.fit"  "$SRCDIR/GOPR0352.MP4" "$SRCDIR/downhill-encinar-almorox.avi"


cd test


# colmenar-mtb-downhill             interpolated    black               (IMPERIAL)
# downhill-chapineria-cruce-e.avi   non_interp      white               SI
# downhill-fres-zarzalejo.avi       interpolated    virb    offset 60s  SI
# downhill-encinar-almorox.avi      interpolated    virb                SI