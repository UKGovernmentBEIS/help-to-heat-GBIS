# Load testing

## Installation

To Install JMeter. Either:
    - Go to [this guide](https://octoperf.com/blog/2018/04/16/how-to-install-jmeter-windows/#run-jmeter) and follow the instructions to donwload and run JMeter. Optionally, add the binary folder to your Path
    - Windows (requires `chocolatey`): `choco install jmeter`  
    - Mac (requires `brew`): `brew install jmeter`

## Run load tests

Run `jmeter -n -t [jmx file] -l results.csv -e -o results_html`

You can view the results via the http dashboard in `report folder` or `results file` specified in the command.
You will need to delete or rename the generated results file and report folder before running the test again.

## Editing load tests

You can edit the jmx files files in GUI by calling `jmeter`.

## Known issues

You need your IP whitelisted to run high volume load tests successfully, due to DoS protection.
