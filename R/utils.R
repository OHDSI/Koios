#' Pipe operator
#'
#' See \code{magrittr::\link[magrittr:pipe]{\%>\%}} for details.
#'
#' @name %>%
#' @rdname pipe
#' @keywords internal
#' @export
#' @importFrom magrittr %>%
#' @usage lhs \%>\% rhs
#' @param lhs A value or the magrittr placeholder.
#' @param rhs A function call using the magrittr semantics.
#' @return The result of calling `rhs(lhs)`.
NULL

#' .data Object
#' @name .data pronoun
.data <- NULL

#' Progress report#'
#' @param x Current progress
#' @param max Final progress value
progress <- function (x, max = 100) {
  percent <- x / max * 100
  cat(sprintf('\r[%-50s] %d / %d',
              paste(rep('=', percent / 2), collapse = ''),
              x,
              max))
  if (x == max)
    cat('\n')
}

#' ETA of completion'
#' @param x Current progress
#' @param max Final progress value
#' @param start A Sys.time() call at the beginning of processing
eta <- function(x, max, start) {
  c = (max-x)+1
  if(c!=max){
    timenow = proc.time()[3]
    timeper = (timenow-start)/x
    timeleft = 1.05*c*timeper
    cat(" -  ", prettyunits::vague_dt(as.difftime(timeleft,units = "secs"),
                                    format = "short"),". remaining.", sep = "")
  }
  if (x == max)
    cat('\n')
}

