# Cloud-Virtual-Suggestion-Box
Virtual Suggestion Box on Google Cloud Platform

# Project Overview
This project introduces a cutting-edge digital suggestion box tool, offering organizations a seamless way to gather valuable feedback and suggestions from both employees and customers. Inspired by freesuggestionbox.com, this project aims to provide a cost-effective alternative to existing suggestion box platforms by offering a similar solution as an open-source tool. While omitting features like polls and votes, this project aligns closely with the functionality of current market offerings.

# Architecture Diagram
![Alt Text](https://github.com/Buff-Abhi/Cloud-Virtual-Suggestion-Box/blob/main/Architecture%20Diagram.png)

# Components
* Google Cloud: Leveraging Google Cloud services including Virtual Machine, Storage, Resource Monitoring, and Logging, the project boasts scalability, easy setup, and comprehensive client API documentation for efficient logging and bucket management.
* Virtual Machine: Operating on Ubuntu 22.04, the virtual machine provides a tailored environment for project development, offering online accessibility for cost-effective deployment, scalability, and simplified management with snapshot capabilities.
* Flask: Empowering the web application development process with its flexibility, lightweight nature, and rich documentation, Flask facilitates frontend creation using HTML & CSS, endpoint establishment, and rapid project initiation.
* Storage: Essential for storing data collected through suggestion boxes, the storage component allows for seamless scaling based on evolving storage requirements.
* Logging: Crucial for monitoring and debugging activities, the logging feature enhances debugging efficiency through its support for various severity levels.
* REDIS: Serving as a temporary data repository during suggestion box operation in key-value pairs, REDIS excels in performance, scalability, and flexible data structuring.
* IP API: Enabling IP location tracing for suggestions and sentiment analysis based on regional data, the IP API sets the stage for future analytics integration.

# Interactions
The project's interactions involve starting the Flask server via the Virtual Machine on port 8080 and REDIS on port 6379. Users access the homepage from a browser to create new suggestion boxes by providing a name and clicking "Create." Each box receives a unique URL for suggestion submission. Upon box closure, all data including IP addresses, messages, and sentiment analysis becomes visible. Data flows into REDIS while the box is open and transfers to the Bucket upon closure along with IP location details and sentiment analysis. Logging occurs at every step of the process to ensure thorough monitoring.

# Capabilities and Aim
This project excels in creating multiple suggestion boxes concurrently, each with a distinct URL that collects data exclusively when the box is active. It incorporates IP location tracing and sentiment analysis to facilitate future analytics based on regional insights. The future goals include enhancing the frontend design, implementing additional security measures, and ultimately releasing the application as an open-source solution.
