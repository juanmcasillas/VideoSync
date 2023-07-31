from metrics import *

if __name__ == "__main__":

    # Put to true to solid background

    parser = argparse.ArgumentParser()

    parser.add_argument("gpx_file", help="GPX 1.1 file")
    args = parser.parse_args()

    hrmmanager = HRMManager(verbose=True, overwrite=True)
    gpx_points = hrmmanager.GetTimeRangeFIT(args.gpx_file, 0, -1)

    series = CreateSeries(gpx_points)
    series_s = CreateSeries(gpx_points)
    #series_s = Smooth(series, [ "slope", "elevation_delta", "distance_delta", "speed" ])
    # join SMOOTH and non smooth SLOPE & SPEED
    series_s = Smooth(series_s, [ "slope", "speed" ])

    eprint("Slope SlopeS Speed SpeedS")
    for i in range(len(series)):
        eprint("%s %s %s %s" % (series[i].slope, series_s[i].slope, series[i].speed, series_s[i].speed))


