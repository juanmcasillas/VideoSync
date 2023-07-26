data <- read.delim("E:\\Dropbox\\arpyro\\hrm\\videosync\\test\\data.txt", header=TRUE, sep=" ")
plot(data$Speed, type='l', col='red')
lines(data$SpeedS, col='blue')

data <- read.delim("/Volumes/Depot/Dropbox/ArPyRo/hrm/videosync/data.txt", header=TRUE, sep=" ")