# Utility scripts

## Install

```sh
pip install virtualenv`
python -m virtualenv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

## Scripts

### update_scottish_epc

Currently WIP

For now this creates a CSV file containing scottish EPC data ready to be loaded into the DB manually,
as described in [Swiki article](https://softwiretech.atlassian.net/wiki/spaces/Support/pages/20520173599/Common+Tasks#How-to-actually-do-an-EPC-data-dump-for-fun-%26-profit).

TODO: Add automatic loading to DB.

The data is deduplicated (using latest only), sorted in order of files, with records without EPC number dropped.

#### Run

`python update_scottish_epc.py`
