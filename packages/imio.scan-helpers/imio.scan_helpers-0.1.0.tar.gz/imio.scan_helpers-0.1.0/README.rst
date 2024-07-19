imio.scan_helpers
=================
Various script files to handle MS Windows scan tool

Installation
------------
Use virtualenv in bin directory destination

Build locally
-------------
bin/pyinstaller -y imio-scan-helpers.spec

github actions
--------------
On each push or tag, the github action will build the package and upload it to the github release page.
https://github.com/IMIO/imio.scan_helpers/releases

Windows installation
--------------------
The zip archive must be decompressed in a directory (without version reference) that will be the execution directory.

Windows usage
-------------
* imio-scan-helpers.exe -h : displays the help
* imio-scan-helpers.exe : updates the software based on verion and restarts it
* imio-scan-helpers.exe -r tag_name: updates the software with specific release and restarts it
* imio-scan-helpers.exe -nu : runs without update
