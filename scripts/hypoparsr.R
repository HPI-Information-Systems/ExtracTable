# this script expects a file to parse as input and returns the detected dialect

# devtools::install_github("tdoehmen/hypoparsr")  # only required at first time

library('rjson')

args = commandArgs(trailingOnly=TRUE)

if (length(args)==0) {
  stop("File path required!", call.=FALSE)
}
filePath = args[1]
startTime <- Sys.time()
result <- hypoparsr::parse_file(filePath)
elapsedTime <- Sys.time() - startTime
if (!is.null(result$error)) {
  quit(status=1)
}

dialect_info <- strsplit(toString(attributes(result$result[result$ranking][[1]]$confidence[5])[1]), "\n")[[1]][3]
delimiter_start <- gregexpr(pattern='delimiter: ', dialect_info)[[1]][1] + nchar('delimiter: ')
delimiter_end <- gregexpr(pattern=' quote: ', dialect_info)[[1]][1]
delimiter <- substr(dialect_info, delimiter_start, delimiter_end - 1)

quote_start <- delimiter_end + nchar(' quote: ')
quote_end <- gregexpr(pattern=' quote method: ', dialect_info)[[1]][1]
quote <- substr(dialect_info, quote_start, quote_end - 1)

quote_method_start <- quote_end + nchar(' quote method: ')
quote_method <- substr(dialect_info, quote_method_start, nchar(dialect_info))
escape <- if (quote_method == 'escape') "\\" else quote
# quote method can only be escape with backslash or 2x quote

dialect <- c(delimiter = delimiter, quotechar = quote, escapechar = escape)
cat(toJSON(dialect))
