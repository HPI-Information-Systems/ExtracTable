# ExtracTable

Tables are a commonly used way for organizing and exchanging data. 
To allow generic use, tables are stored in plain text files that might include non-table content such as metadata. 
Comma-separated values (CSV) and layout features (ASCII) are two prevalent ways to represent tables.
Although there is a specification for the CSV format, users develop variations with customized field separators and table layouts. Thus, before data scientists can analyze the data of such tables, they need to configure the parsers for each file manually. This process is not only time-consuming but also repetitive and error-prone.

Given that we want to help data scientists to spend less time with data preparation, we propose a solution that automatically extracts tables from plain text files.
While humans can easily locate tables with semantic understanding, machines struggle as they lack such information.

Existing work tackles the table extraction problem for CSV files using heuristics or pattern-based approaches. None of the related work covers a parser that is capable of handling files containing multiple tables.
We propose ExtracTable, an algorithm that exploits the data type consistency within columns to extract tables from plain text files. In contrast to existing solutions, ExtracTable works with multi-table files, tables represented in ASCII or CSV, and CSV dialects deviating more from the specification RFC 4180.

We evaluate our algorithm on a data set consisting of about 1,000 files taken from various open data portals. Compared to existing approaches, ExtracTable is 20% better at recognizing the table ranges and returns the accurate table boundaries for 70% of the tables. When comparing the parsing accuracy, the algorithm detects the correct dialects for 90% of the CSV tables similar to existing approaches. ExtracTable is the only solution supporting ASCII tables and returns the proper column boundaries for 76% of them.
To demonstrate the capabilities of ExtracTable, we developed a demo web app, available from within the university network.

Content of this repository:
- [Expose](Expose.pdf)
- [Master thesis](Master%20thesis.pdf)
- [ExtracTable Implementation (Python)](table-extraction)
- [Annotation tool (React)](labeling-tool)
- [Evaluation code (Python)](evaluation)
- [Evaluation baseline scripts](scripts)
- [Evaluation notebooks (Jupyter)](notebooks)
- [Demo web app (Flask and React)](demo-web-app)
