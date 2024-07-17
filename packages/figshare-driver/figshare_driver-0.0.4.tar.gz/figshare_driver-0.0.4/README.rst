================
Figshare Driver
================

Driver to retrieve metrics from the Figshare portal.

Refer to https://figshare.com to get the user and password from.

For more information about the OPERAS metrics, go to
https://metrics.operas-eu.org/


Troubleshooting
===============

At the moment of development, the endpoint https://stats.figshare.com/tome/breakdown/
only takes one item_id per call, making the data fetching inefficient,
Once the api is ready for ingesting a list of ids we will be able to overcome this issue.

Release Notes:
==============

[0.0.4] - 2024-06-16
---------------------
Changed
.......
    - Refactored logic and deleted unnecessary statement.
    - Removed unused requirement pandas.

[0.0.3] - 2024-06-12
---------------------
Changed
.......
    - Corrections to the urls.
    - Added the ability to fetch results by start_date and end_date.

[0.0.2] - 2024-06-12
---------------------
Added
.......
    - Added 'retrieve_doi' method to get the article's doi.
    - Added unittests.

[0.0.1] - 2024-06-10
---------------------
Added
.......
    - Logic to initialise the Figshare driver.
