# Run from repository root. No automatic dataset downloads or redistribution.
source("R/snapshot_features.R")
root <- Sys.getenv("BDB_DATA_DIR", "data/raw")
files <- file.path(root,c("plays.csv","tracking2018.csv","tracking2019.csv","tracking2020.csv"))
if (!all(file.exists(files))) stop(paste("Missing licensed input files:", paste(files[!file.exists(files)],collapse=", ")))
plays <- read.csv(files[1]); t <- do.call(rbind,lapply(files[-1],read.csv))
d <- snapshot_features(t,plays)
d$season <- as.integer(substr(as.character(d$gameId),1,4))
train <- d[d$season %in% c(2018,2019), ]; test <- d[d$season==2020, ]
if(nrow(train)<20 || nrow(test)<20) stop("Insufficient chronological holdout")
model <- lm(kickReturnYardage ~ returner_x+returner_y+nearest_player+mean_player_distance,data=train)
print(heldout_metrics(test$kickReturnYardage,predict(model,test),train$kickReturnYardage))
cat("Descriptive reception baseline; no causal or current kickoff-rule claims.\n")
