ndn-status - Status page web view
==================================

This branch contains the web page used to view the results of running the status scripts. 


Dependencies
------------
For the web page to work, the following dependencies are required:
* ndn-js

Prerequisites
-------------------
1. Before setting up the page, you will need to clone the ndn-js repository on the <b>machine that is running the log scripts</b> (the scripts in the master branch of this repository).

  Once you have ndn-js, navigate to the wsproxy directory and follow the README to install node and ws. Afterwards, run the wsproxy, for example:

      node wsproxy-udp.js -L 2
      
2. The scripts are set up such that the web page (this branch) and the scripts (the master branch) are on separate machines. The web page will make requests to the remote machine via the scripts in the script/ directory. Thus, the user that the web server is running under (usually www-data), should be able to ssh into the remote machine using a key-pair (no password required).  
    
Setting up the page
--------------------
Once all the prerequisites have been met, setting up the page is as simple as running the configure script.

      ./configure
      
After configuring the web page, point your browser to the status.htm file and the status page will start loading.
