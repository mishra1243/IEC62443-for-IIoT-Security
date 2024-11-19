# Secure-iiot
This repository contains the code, architecture, and setup instructions for deploying security controls based on IEC 62443-4-2 for IIoT environments. The project focuses on implementing foundational and additional security measures to enhance industrial edge device security, aiming to improve resilience against cyber threats in IIoT systems.

# Prerequisites
<ul>
  <li>Python 3.8+: Required for running Python scripts.</li>
  <li>Node-RED: Needed if you intend to use the data_to_nodered.py functionality.</li>Python 3.8+: Required for running Python scripts.
  <li>Shell Access: Required for running shell scripts with elevated permissions (for Superadmin scripts).</li>Python 3.8+: Required for running Python scripts.
  <li>Permissions: Ensure you have appropriate permissions to create users, configure files, and set up logging and monitoring.</li>Python 3.8+: Required for running Python scripts.
</ul>

# Setup
You will need to have 3 users to replicate the setup, One admin user who is responsible for  managing administrative daily tasks, one local user is present whose main task is to observe and monitor and act as a local employee. one superadmin user is there to manage privileges of the other user, manage which commands can be run by the other users and a security console with session controls and other privilege management applications.
You can then copy the scripts as mentioned in the folder structure to the respective users, and download the required libraries to run the python scripts and if you want to automate the running part of the scripts you can make it as a system service and configure them to auto start with the right privilege.
For node red dashboard and flows you can import the json flow and then edit the nodes to suit your respective needs.

For any configuration related setup you can email me at harshguptag467@gmail.com
You can see the demo's for the controls in the following shared folder - https://drive.google.com/drive/folders/1nJ4BMmjMXkSy4gyq90ffWE9QKU0tZhFn?usp=sharing



