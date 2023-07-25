#usage: hudint.py [-h] [-o OFFSET] [-v] [-f] [-l] [-s] [-t TITLE]
#                config_file gpx_file video_file output_file
#hudint.py: error: too few arguments

VIDEODIR="/Archive/Videos/Collection/2018/20180421 --- 21-Abril-2018 (IV Maraton Tietar)"
DATADIR="/Archive/Cartography/files/FENIX3/2018"

/usr/local/bin/python hudint.py -o 86400  -v -t "Bajada desde la Centenera al Pueblo" -s virb.xml "$DATADIR/2018-04-21-08-32-54 - [MTB,FENIX3,CANYON_CF] Maratón Bajo Tietar IV Edicion - Corta.fit"  "$VIDEODIR/GOPR0433.MP4" "$VIDEODIR/salida.avi"


