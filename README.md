# VideoSync Python Video Overlay 2.0

This project creates a customizable overlay on a video clip that shows data
recorded previously with a GPS unit, sincronized with the video.

* [Video 1](https://www.youtube.com/watch?v=WGJBNHz-4Bk&t=32s)
* [Video 2](https://www.youtube.com/watch?v=SGQ2KWcBtwY)
* [Video 3](https://www.youtube.com/watch?v=Fg8Sf4fPCwY&t=70s)


## USAGE

1. Sync the camera's date & time with GPS time
2. Start the GPS unit to record (better at 1s interval)
3. Create clips
4. Go home
5. Download video files.
6. Download GPS unit files.
7. Run the program with the configuration file, gps file and video files.

```

```

## DETAILED INFO

The project uses the stored date & time metadata field in the video clip to sync the GPS info with the video frames. After getting this value, the 
program walks across the frames, looking for the right point info (the
point nearest in time to frame's time). Then, based on a customizable 
XML configuration file, it draws each video frame with the data (e.g speed, distance, cadence... etc). After that, a new video clip is build with the overlay. Sound, Resolution and Quality if fully preserved.

## TEST RIG

My test rig is:

- Garmin EDGE 1000 configured to save 1s intervals, no zeroes in
        power, neither cadence. No autostop, no autolap.
- Gopro HERO 3 at 1280 x 720 / 50 fps.
- Stages power (left crack arm).
    
## SYNCING CAMERA TIME

Easy: Put the SAME data & time that GPS unit. With GOPRO is really  easy: Get the GOPRO app (Android, IOS), go to settings, press Set Date & Time. This syncs the date with NTP (internet) date and everything go fine. ITS VERY IMPORTANT TO SYNC THE DATE. For now, the sync DATE can't be passed as argument to the program, but in a future I can put this functionality.
    
## CONFIGURATION FILES

The configuration is done using XML file format. You can configure
layout, data fields, images, rectangles, lines, fonts, colors,
interpolation mode, and units. See the configuration files for more
details.
    
## FEATURE SET

- Support FIT files (e.g. to extract Power, Cadence, Temperature ... etc)
- Support GPS files (more basic information)
- Imperial Units (mi/h, ft, mi, F)
- SI Units (km/h, m, m, C)
- Any frame rate (30, 50, 100 fps)
- Any video resolution (more res, more time)
- Autosync video time
- Filtering & Smoothing (currently activated for slope, speed)
    (points are convoluted to remove spikes and to smooth the data curve)
- Smart gradient calculation (se above)
- Draws a Map based on Open Street Map of the current segment.
- Support Video offset (to process only the relevant segment).
- Create matte overlay (e.g. to use the overlay in Final Cut Pro).    

- Configurable:
    - Fonts
    - Colors
    - Data fields:
        slope           slope, in % 
        distance        distance travelled
        elevation       elevation from sea level
        speed           speed
        label           generic label (e.g. the title or the credits)
        time            current VIDEO time (when clip was recorded, updated)
        cadence         RPM
        temperature     In the right unit
        hr              Heart Rate
        power           in Watts (supports animation)
        gpsinfo         Latitude, Longitude info
        osmmap          A customizable Open Street Map (with caching)
        altgraph        Altitude Graph (Fully customizable)
        bearing         Bearing (a nifty compass)
        picture         Generic PIL image support (e.g. Watermark or icons)
        rect            Draws a RECTangle in the screen
        line            Draws a Line in the screen
        
        Each field can be customized in location, size, color, transparency,
        fonts, and specific configuration (e.g. ossmap). You can have 
        MULTIPLE items (e.g. the icons) and can customized each one 
        individually.
        
     If not data is available (e.g. Power in GPX file) and still you have
     configured the data field, a "--" is shown. Each data field is updated
     each frame (to archieve good smooth transitions).
     
     - Supports INTERPOLATION. The GPS values are stored at maximum 1sec
       interval, but I managed to write some functions to interpolate the 
       values for specificic frame intervals (e.g. 1/50 sec). This allows the program to create smooth value changes, instead 1-sec updates. See altgraph or ossmap widgets to get the difference between 1-sec update (non interpolated) and Interpolated (continuous) udpates.
       
Have more things, but I can't remember every feature of the project :)
   
## RUNNING PLATFORMS & STATUS
    
* Currently works on Windows 7, Windows 10 and MacOS 10.13.6.
    
* Based on Python 3.11 with the following dependencies:
    - OpenCV
    - PIL (PILLOW)
    - PyGame
    - FITParse
    - GPXPy (used my own modified version)
    - NumPy
    - Hachoir
    - Imutils
    - TimeCode

This project is multi-platform, and should work on Linux without 
problems. Currently the distribution status of this work is 
"functional prototype" that means that works well (there are some
hidden bugs, by sure) but is not "distributable" in the mean that
to install it you haven't any package or installer (by now).

## LICENSING (TODO)

The code uses the GNU General Public license version 3.0 for personal and Non Profit organizations. For Commercial use, please contact me before using the code.

## WARRANTY

No warranty is given for this project. Is a personal development, and It's not distributed neither released.

## INSTALL

```bash
% python311\python.exe -m pip install opencv-contrib-python
% python311\python.exe -m pip install pillow
% python311\python.exe -m pip install pygame
% python311\python.exe -m pip install fitparse
% python311\python.exe -m pip install gpxpy
% python311\python.exe -m pip install numpy


% python311\python.exe -m pip install imutils
% python311\python.exe -m pip install timecode
% python311\python.exe -m pip install hachoir



FFMPEG binaries (https://www.gyan.dev/ffmpeg/builds/)
```