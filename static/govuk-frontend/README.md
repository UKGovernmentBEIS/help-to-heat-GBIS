# GOV.UK Frontend

Contains a copy of code released from https://github.com/alphagov/govuk-frontend, with slight modification used to make it compatible with our code setup.

## Updating GDS Frontend

When changing the version, download a release from the GDS Frontend repo and replace the existing GDS files here.
Then, make the following edits:
1. In the `.css` file of the GDS frontend, replace all references to `/assets/**` with `/static/govuk-frontend/assets/**`. For instance `/assets/images/govuk-crest.png` -> `/static/govuk-frontend/assets/images/govuk-crest.png`.
2. Our base html pages reference the GDS files by name, which contain the version number. When the version number changes this will need to be updated. Search the project for the old version number and update as appropriate.
