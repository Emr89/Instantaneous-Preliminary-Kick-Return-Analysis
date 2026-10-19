# Reception features: one play per row; explicit returner, never first-row distance.
snapshot_features <- function(tracking, plays) {
  keys <- c("gameId", "playId")
  need_t <- c(keys, "frameId", "nflId", "event", "x", "y", "playDirection")
  need_p <- c(keys, "returnerId", "kickReturnYardage")
  if (!all(need_t %in% names(tracking)) || !all(need_p %in% names(plays)))
    stop("Missing required tracking/play columns")
  pk <- function(d, cols) do.call(paste, c(d[cols], sep=":"))
  if (anyDuplicated(pk(plays, keys))) stop("Duplicate play key")
  t <- tracking[tracking$event == "kick_received" & !is.na(tracking$event) & !is.na(tracking$nflId), ]
  if (anyDuplicated(pk(t, c(keys, "frameId", "nflId")))) stop("Duplicate player-frame key")
  groups <- split(t, pk(t, keys))
  rows <- lapply(groups, function(g) {
    if (length(unique(g$frameId)) != 1) stop("Multiple reception frames for a play")
    ix <- match(pk(g[1,,drop=FALSE], keys), pk(plays, keys))
    if (is.na(ix)) stop("Tracking play absent from plays")
    p <- plays[ix,,drop=FALSE]
    r <- which(as.character(g$nflId) == as.character(p$returnerId))
    if (length(r) != 1) stop("Exactly one identifiable returner required")
    if (!all(is.finite(g$x) & is.finite(g$y))) stop("Nonfinite coordinates")
    if (length(unique(g$playDirection)) != 1 || !g$playDirection[1] %in% c("left","right")) stop("Invalid play direction")
    if (g$playDirection[1] == "left") { g$x <- 120-g$x; g$y <- 160/3-g$y }
    distances <- sqrt((g$x-g$x[r])^2 + (g$y-g$y[r])^2)
    d <- distances[-r]
    if (!length(d)) stop("No other players")
    data.frame(gameId=p$gameId,playId=p$playId,returner_x=g$x[r],returner_y=g$y[r],
               nearest_player=min(d),mean_player_distance=mean(d),
               kickReturnYardage=p$kickReturnYardage)
  })
  if (!length(rows)) stop("No reception observations")
  do.call(rbind, rows)
}

heldout_metrics <- function(observed, predicted, train_y) {
  if (!length(observed) || length(observed)!=length(predicted) || any(!is.finite(c(observed,predicted,train_y)))) stop("Invalid metrics input")
  denom <- sum((observed-mean(observed))^2)
  c(rmse=sqrt(mean((observed-predicted)^2)), mae=mean(abs(observed-predicted)),
    r_squared=if(denom>0) 1-sum((observed-predicted)^2)/denom else NA_real_,
    training_mean_baseline_rmse=sqrt(mean((observed-mean(train_y))^2)))
}
