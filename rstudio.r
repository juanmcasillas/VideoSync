require(ggplot2)
theme_set(theme_bw())

data <- read.delim("E:\\Dropbox\\arpyro\\hrm\\videosync\\data.csv", header=TRUE, sep=" ")
ggplot(aes(x = Time, y = Elevation), data = data) + geom_point()
plot(data$Elevation, typ="l")

plot(data$Elevation, type="l", col="blue")
par(new=TRUE)
plot(data$Slope, typ="l", col="red")