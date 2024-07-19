#  PyNetCheck

## Python Network Checker

This project provides examples to extend the IP Fabric platform with custom device testing.

## Requesting New CVEs

To request a new CVE to be added to the checker please open an
[issue on GitLab](https://gitlab.com/ip-fabric/integrations/pynetcheck/-/issues) or
send an email to [contact-project+ip-fabric-integrations-pynetcheck-cve@incoming.gitlab.com](mailto:contact-project+ip-fabric-integrations-pynetcheck-cve@incoming.gitlab.com).

Please include the CVE ID or link to documentation.

## Requirements

* `Configuration saved` task must be enabled in [IP Fabric Discovery Settings](https://docs.ipfabric.io/latest/IP_Fabric_Settings/Discovery_and_Snapshots/Discovery_Settings/disabled_discovery_tasks/) for running against most vendors.
  * This was previously disabled in older versions however it was determined there is no known impact to the network or devices after enabling it.
  * Enabling this will allow you to see `Management > Saved Config Consistency` table which will report devices that are supported if their running configs have been saved.
* Environment variables or command line arguments with IP Fabric URL and credentials.

### IP Fabric Arguments

Currently implemented arguments:

* `--ipf-url https://demo.ipfabric.io`
* `--ipf-token 7bb0e03827d32f3dfb4d5995824f2e01` - Token to use for authentication.
* `--insecure` - Disable SSL verification, use flag if using a self-signed certificate.
* `--snapshot 33162920-8928-437d-9e4c-b125321f5686` - Defaults to `$last`.

These will take precedence over any environment variables or `.env` file settings.

### Environment Variables

These can be set in the environment or in a file named `.env` in the directory you are running.
Environment variables take precedence over `.env` variables.

```bash
IPF_URL=https://demo.ipfabric.io

# Use IPF_TOKEN OR (IPF_USERNAME AND IPF_PASSWORD):
IPF_TOKEN=TOKEN
# IPF_USERNAME=user
# IPF_PASSWORD='p@ssw0rd'

# OPTIONAL:

# IPF_SNAPSHOT defaults to $last
IPF_SNAPSHOT=$last
# IPF_SNAPSHOT=7e2d4bef-3f90-4c9c-851d-fc2f0990db35

# IPF_VERIFY defaults to True and can also be set to a path
IPF_VERIFY=true
# IPF_VERIFY="path/to/client.pem"

# IPF_TIMEOUT defaults to HTTPX default of 5.0 see https://www.python-httpx.org/advanced/#timeout-configuration
# IPF_TIMEOUT only accepts int/float arguments
IPF_TIMEOUT=5
```

## Installation

The project is available on PyPi and can be installed via pip:

```bash
pip install pynetcheck
```

## Running

### Running Against IP Fabric

To run tests with builtin cases, use the following command:

```bash
(venv) >pynetcheck --tb=line                         
========================================================================================== test session starts ==========================================================================================
platform win32 -- Python 3.9.9, pytest-7.4.2, pluggy-1.3.0
rootdir: C:\Code\_EXAMPLES\config_vulnerability\pynetcheck
configfile: pytest.ini
plugins: anyio-4.0.0, depends-1.0.1, html-reporter-0.2.9
collected 13 items                                                                                                                                                                                       

pynetcheck\tests\cve_2023_20198\ios_xe_test.py ..sFFFF.s.s.s                                                                                                                                       [100%]

=============================================================================================== FAILURES ================================================================================================ 
C:\Code\_EXAMPLES\pynetcheck\tests\cve_2023_20198\ios_xe_test.py:34: AssertionError: Startup - HTTP secure-server Enabled
C:\Code\_EXAMPLES\pynetcheck\tests\cve_2023_20198\ios_xe_test.py:52: AssertionError: Startup - HTTP secure-server Vulnerable
C:\Code\_EXAMPLES\pynetcheck\tests\cve_2023_20198\ios_xe_test.py:30: AssertionError: Running - HTTP server Enabled
C:\Code\_EXAMPLES\pynetcheck\tests\cve_2023_20198\ios_xe_test.py:50: AssertionError: Running - HTTP server Vulnerable
======================================================================================== short test summary info ========================================================================================
FAILED pynetcheck\tests\cve_2023_20198\ios_xe_test.py::TestHTTPServerIPF::test_https_server_disabled[L77R11-LEAF5] - AssertionError: Startup - HTTP secure-server Enabled
FAILED pynetcheck\tests\cve_2023_20198\ios_xe_test.py::TestHTTPServerIPF::test_https_server_vulnerable[L77R11-LEAF5] - AssertionError: Startup - HTTP secure-server Vulnerable
FAILED pynetcheck\tests\cve_2023_20198\ios_xe_test.py::TestHTTPServerIPF::test_http_server_disabled[L67CSR16] - AssertionError: Running - HTTP server Enabled
FAILED pynetcheck\tests\cve_2023_20198\ios_xe_test.py::TestHTTPServerIPF::test_http_server_vulnerable[L67CSR16] - AssertionError: Running - HTTP server Vulnerable
================================================================================ 4 failed, 5 passed, 4 skipped in 1.94s ================================================================================= 
```

### Running Against Configuration Files Directory

To run using a directory that stores a list of configuration files:

```bash
pynetcheck --config-dir /path/to/dir
```

***This will attempt to run tests on all configs in the directory, please ensure the correct vendor and families are 
sorted in separate directories and use pytest marks to filter the tests.***

### Filtering

Pytest Marks have been added to allow for filtering of tests. 
Please see the [Working with custom markers](https://docs.pytest.org/en/latest/example/markers.html) for more information.

* `-m cve` - Filter only CVE tests
* `-m cisco` - Filter only Cisco tests
* `-m paloalto` - Filter only Palo Alto tests

`-m` can be used with `not` to exclude tests or a combination of marks, example: `-m "not cve"` or `-m "cisco and not cve"`.

You can also use the `-k` option to filter tests by name.

### Environment Variables

The following environment variables can be used to override how tests fail or pass:

| Type   | Vendor | Variable           | Accepted Values | Default | Description                           |
|--------|--------|--------------------|-----------------|---------|---------------------------------------|
| Vendor | Cisco  | CISCO_HTTP_SERVER  | DISABLED*       | ENABLED | Will fail if HTTP server is enabled.  |
| Vendor | Cisco  | CISCO_HTTPS_SERVER | DISABLED*       | ENABLED | Will fail if HTTPS server is enabled. |
| Vendor | Cisco  | CISCO_SCP_SERVER   | DISABLED*       | ENABLED | Will fail if SCP server is enabled.   |

*Only valid variable value, no other value will be accepted.

## Results

### HTML

Results are stored in the [pytest_html_report.html](https://gitlab.com/ip-fabric/integrations/pynetcheck/-/raw/main/example/pytest_html_report.html) which can be viewed in any browser.  

![img.png](https://gitlab.com/ip-fabric/integrations/pynetcheck/-/raw/main/example/pytest_html.png)

### Exporting

The `pytest-html-reporter` also provides the ability to export via CSV or Excel formats, example: [pytest.csv](example/pytest.csv).

Table modified to show only the relevant information:

| Suite                               | Test Case                                  | Status | Time (s) | Error Message                                               |
|-------------------------------------|--------------------------------------------|--------|----------|-------------------------------------------------------------|
| tests/cve_2023_20198/ios_xe_test.py | test_saved_config_consistency              | PASS   | 0.21     |                                                             |
| tests/cve_2023_20198/ios_xe_test.py | test_https_server_vulnerable[L77R12-LEAF6] | SKIP   | 0        |                                                             |
| tests/cve_2023_20198/ios_xe_test.py | test_https_server_vulnerable[L77R11-LEAF5] | FAIL   | 0        | E   AssertionError: Startup - HTTP secure-server Vulnerable |
| tests/cve_2023_20198/ios_xe_test.py | test_https_server_vulnerable[L67CSR16]     | SKIP   | 0        |                                                             |
| tests/cve_2023_20198/ios_xe_test.py | test_https_server_disabled[L77R12-LEAF6]   | PASS   | 0        |                                                             |
| tests/cve_2023_20198/ios_xe_test.py | test_https_server_disabled[L77R11-LEAF5]   | FAIL   | 0        | E   AssertionError: Startup - HTTP secure-server Enabled    |
| tests/cve_2023_20198/ios_xe_test.py | test_https_server_disabled[L67CSR16]       | PASS   | 0        |                                                             |
| tests/cve_2023_20198/ios_xe_test.py | test_http_server_vulnerable[L77R12-LEAF6]  | SKIP   | 0        |                                                             |
| tests/cve_2023_20198/ios_xe_test.py | test_http_server_vulnerable[L77R11-LEAF5]  | SKIP   | 0        |                                                             |
| tests/cve_2023_20198/ios_xe_test.py | test_http_server_vulnerable[L67CSR16]      | FAIL   | 0        | E   AssertionError: Running - HTTP server Vulnerable        |
| tests/cve_2023_20198/ios_xe_test.py | test_http_server_disabled[L77R12-LEAF6]    | PASS   | 0.13     |                                                             |
| tests/cve_2023_20198/ios_xe_test.py | test_http_server_disabled[L77R11-LEAF5]    | PASS   | 0.15     |                                                             |
| tests/cve_2023_20198/ios_xe_test.py | test_http_server_disabled[L67CSR16]        | FAIL   | 0.15     | E   AssertionError: Running - HTTP server Enabled           |
