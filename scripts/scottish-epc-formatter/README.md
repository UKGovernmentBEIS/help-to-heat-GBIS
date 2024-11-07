This Scottish EPC Formatter is a tool to format a [Domestic Scottish EPC CSV](https://statistics.gov.scot/data/domestic-energy-performance-certificates) into the form required to perform a data dump into the portal_scottishepcrating table of the database.

It will remap the field names in the CSV to the equivalent fields used in the GBIS database, and remove fields which are not used in the database.
After doing this, it will concatenate all files together into a single ZIP file to be sent to the database.

# Usage
1. Install node, or open this folder in the provided dev container
   1. Reopen this folder in vscode, for instance with `code scripts\scottish-epc-formatter`
   2. Reopen this folder in dev container
2. Place all csvs from the downloaded Scottish ZIP into the `./epc` folder. Create it if it does not exist.
3. Ensure you don't have `out.csv` open if you're running this script for a second time. VSCode is likely to crash if you do!
4. `npm start`.
5. The result will be written to `out.csv` in this folder.