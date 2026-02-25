This Scottish EPC Formatter is a tool to format a [Domestic Scottish EPC CSV](https://statistics.gov.scot/data/domestic-energy-performance-certificates) into the form required to perform a data dump into the portal_scottishepcrating table of the database.

It will remap the field names in the CSV to the equivalent fields used in the GBIS database, and remove fields which are not used in the database.
After doing this, it will concatenate all files together into a series of CSV files ready to be zipped together to upload.
Files are split every 500,000 lines to ensure they can be imported to the database properly.

# Usage
1. Install node, or open this folder in the provided dev container.
   1. Reopen this folder in vscode, for instance with `code scripts\scottish-epc-formatter`.
   2. Reopen this folder in dev container.
2. Place all csvs from the downloaded Scottish ZIP into the `./epc` folder. Create it if it does not exist.
3. Run `npm start`.
4. The results will be written to `x-epc.csv` in this folder.