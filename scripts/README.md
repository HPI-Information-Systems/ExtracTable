# Usage

All command-line scripts require a path as input and return the detected dialect.
The conda environment 'evaluation' contains most of the required packages.
All scripts return a single JSON document in the format of:

```
{
  'delimiter': str,
  'quotechar': str,
  'escapechar': str,
}
```

## Hypoparsr

`Rscript hypoparsr.R <path to file>`

*Note* Make sure to install the hypoparsr library when executing the script the first time.

## CleverCSV

`clevercsv detect -j <path to file>`

## Sniffer

`python sniffer-cmd.py detect --file_path <path to file>`
