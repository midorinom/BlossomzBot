# BlossomzBot

## Table of Contents
* [Introduction](#Introduction)
* [Technologies Used](#Technologies)
* [Data Model](#Data)
* [Features](#Features)
    * [Managing Guests](#Guests)

<a name="Introduction"></a>
## Introduction

<a name="Technologies"></a>
## Technologies Used
Architecture Diagram:
<img src="/documentation/Architecture Diagram.png" alt="Architecture Diagram" title="Architecture Diagram">

The app was built using Python and the Interactions.py library. It is connected to a MySQL database. Any changes made to the main branch in Git will automatically trigger the deploy script in Github Actions to deploy the app into an AWS EC2 instance, where the app is hosted. The MySQL instance in the AWS environment is hosted using AWS RDS. The app is integrated with Google Sheets by making API calls to API endpoints created in SheetDB, which interacts with Google Sheets, where an automatically triggered script in Apps Script updates the sheet accordingly.

<a name="Features"></a>
## Features

<a name="Guests"></a>
#### Managing Guests
Test
