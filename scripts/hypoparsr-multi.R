# this script uses the file-overview.csv and executes the hypoparsr for each file, storing the result in a second csv file

install.packages("remotes")
library(remotes)
install_version("hypoparsr", "0.1.0")
install.packages("sjmisc")
install.packages("purrr")

MENDELET_ROOT <- '/home/datasets/mendeley/'
OUTPUT_ROOT <- '/home/leonardo.huebscher/extracting-tables-from-plain-text/notebooks/output/mendeley-analysis/'

counter <- 0
hypoparsrMapper <- function(filePath) {
  counter <<- counter + 1
  print(counter)
  print(Sys.time() - startTime)
  result <- hypoparsr::parse_file(toString(filePath))
  if (!is.null(result$error)) {
    print(result$error)
    write(paste(toString(filePath), 0, sep = ' '), file = paste(OUTPUT_ROOT, 'backup-hypoparsr-txt.csv', sep=''), append=TRUE)
    return(0)
  }
  write(paste(toString(filePath), length(result$results), sep = ' '), file = paste(OUTPUT_ROOT, 'backup-hypoparsr-txt.csv', sep=''), append=TRUE)
  return(length(result$results))
}

fileSet <- read.csv(file = paste(OUTPUT_ROOT, 'txt-files2.csv', sep = ''))
startTime <- Sys.time()
fileSet$hypoparsr = as.integer(purrr::map(as.list(fileSet$absolute.path), hypoparsrMapper))
# write.csv(x = fileSet, file = paste(OUTPUT_ROOT, 'hypoparsr-txt.csv', sep = ''))
