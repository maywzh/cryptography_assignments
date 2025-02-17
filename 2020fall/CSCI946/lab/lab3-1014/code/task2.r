library(plyr)
library(ggplot2)
library(cluster)
library(lattice)
library(graphics)
library(grid)
library(gridExtra)
library(ggthemes)
data(ruspini)
wss<-numeric(15)
for (k in 1:15) wss[k] <- sum(kmeans(ruspini,centers=k,nstart=25)$withinss)
plot(1:15,wss,type='b',xlab='Number of clusters',ylab='Within sum of squares')
km<-kmeans(ruspini,5)
plot(ruspini[c('x','y')],col=km$cluster,pch=as.integer(ruspini$Species))
points(km$centers[,c('x','y')],col=1:5,pch=8,cex=2)
km$cluster
print(km)
save.image('task2.RData')
