from metrics import *

if __name__ == "__main__":

    # Put to true to solid background

    parser = argparse.ArgumentParser()

    parser.add_argument("-d", "--duration", help="duration in seconds")
    parser.add_argument("-o", "--offset", help="offset in seconds")
    parser.add_argument("gpx_file", help="GPX 1.1 file")
    args = parser.parse_args()


    hrmmanager = HRMManager(verbose=True, overwrite=True)
    gpx_points = hrmmanager.GetTimeRangeFIT(args.gpx_file, int(args.offset), int(args.duration))

    series = CreateSeries(gpx_points)
    #series_s = Smooth(series, [ "slope", "elevation_delta", "distance_delta", "speed" ])
    series_s = Smooth(series, [ "slope", "speed" ])

    #csv <- read.delim("E:\\Dropbox\\arpyro\\hrm\\videosync\\data.csv", header=TRUE, sep=" ")
    #eprint("Date Time Latitude Longitude Elevation Distance Speed Slope ElevDelta")
    eprint(series[0].header())

    for s in series_s:
        #eprint("%s %s %s %s %s %s %s %s" % (s.time,s[1],s[2],s[3],s[4],s[5],s[6], s[7]))
        eprint(s)


#ds = DataSerie(['time', 'latitude', 'longitude', 'elevation', 'distance_delta', 'speed', 'slope', 'elevation_delta'])