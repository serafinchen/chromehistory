# Chrome History Extraction

This Project extracts Chrome Artifacts from C:\Users\user\AppData\Local\Google\Chrome\User Data\Default\History
using the ccl_chromium_reader (https://github.com/cclgroupltd/ccl_chromium_reader)
It is displayed with dash and networkx.

Make sure Chrome is closed because otherwise the access to the database is locked.
Install the requiered packages and execute the App.py file.

Choose a Session and click on the nodes in the Graph to get Details about the visit.


## Setup

pip install networkx

pip install git+https://github.com/cclgroupltd/ccl_chromium_reader.git

pip install dash

pip install Brotli

pip install pandas

pip install plotly

pip install pytest
