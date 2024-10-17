This Scottish EPC Formatter is a tool to format a [Domestic Scottish EPC CSV](https://statistics.gov.scot/data/domestic-energy-performance-certificates) into the form required to perform a data dump into the portal_scottishepcrating table of the database.

It will remap the field names in the CSV to the equivalent fields used in the GBIS database, and remove fields which are not used in the database.

# Usage
1. Install node, or open this folder in the provided dev container
   1. Reopen this folder in vscode, for instance with `code scripts\scottish-epc-formatter`
   2. Reopen this folder in dev container
2. `node index.js --infile <raw csv path> --outfile <path>` OR `node index.js --infile <raw csv path>` to overwrite