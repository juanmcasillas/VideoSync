
$SAMPLESDIR="C:\\dev\\VideoSync\\samples"
$PYTHON="C:\\software\\python311\\python.exe"
cd ..

#$CURDIR="Cenicientos-ROAD"
#$CURDIR="Chase-M501-ROAD"
#$CURDIR="Fresnedillas-Robledo-ROAD"
$CURDIR="Minas-Colmenar-MTB"
#$CURDIR="Tietar-MTB"

$WORKDIR="$SAMPLESDIR\\$CURDIR"
& $PYTHON hudint.py -t "$CURDIR" -s -v templates\\config_white.xml $WORKDIR\\data.fit $WORKDIR\\video2.MP4 $WORKDIR\\output.avi -o 60 -d 5

cd tests

# PowerShell Scripts:
# allow to run in the system
# Get-ExecutionPolicy -list as admin
# Set-ExecutionPolicy Unrestricted|Bypass as admin