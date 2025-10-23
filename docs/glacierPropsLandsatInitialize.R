#glacierPropsLandsatInitialize.R initializes glacierPropsLandsat.csv

rm(list=ls()) #clear old variables

glaciers=read.csv('glacierProps.csv')

glacierLandsat=glaciers[,1:3]
glacierLandsat$Region='Terminus'
glacierLandsat$LonCenter=glaciers$leafletLon
glacierLandsat$LatCenter=glaciers$leafletLat
glacierLandsat$LonMin=glaciers$leafletLon-.1
glacierLandsat$LonMax=glaciers$leafletLon+.1
glacierLandsat$LatMin=glaciers$leafletLat-.1
glacierLandsat$LatMax=glaciers$leafletLat+.1

write.csv(glacierLandsat,'glacierPropsLandsat.csv',row.names=FALSE,quote=FALSE)

#then switch to test_roi.ipynb for edits to AOIs
#a bit clunky, but easier/faster to iterate than other methods

#recalculate Center from Max/Min?

#TODO: add whole-glacier rows (perhaps combining adjacent glaciers) -
#   complicated by large glaciers that cover multiple Landsat scenes
