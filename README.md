# BlossomzBot

## Table of Contents
* [Introduction](#Introduction)
* [Technologies Used](#Technologies)
* [Development Environment](#DevEnvironment)
* [Features](#Features)
    * [Managing Guests](#Guests)
    * [Welcome Message](#Welcome)
    * [Google Sheets Integration](#Google)
    * [Slash Commands](#Commands)
 * [Error Handling](#Error)

<a name="Introduction"></a>
## Introduction
BlossomzBot is a bot created for Discord, a social platform for messaging and making calls. In particular, BlossomzBot was created entirely by myself for a discord server (Blossomz) that I am a part of, which is a community within the online multiplayer game, Lost Ark. 

This discord bot was created to be used by the admins of the Blossomz discord server, to make the process of carrying out various server and ingame administrative matters much easier and automated.

## Technologies Used
<a name="Technologies"></a>
<div style="display:flex">
<img src="/readme/Python.png" alt="Python" title="Python">
<img src="/readme/Interactions.py.png" alt="Interactions.py" title="Interactions.py">
<img src="/readme/Discord Dev.png" alt="Discord Dev" title="Discord Dev">
<img src="/readme/AWS EC2.png" alt="AWS EC2" title="AWS EC2">
<img src="/readme/AWS RDS.png" alt="AWS RDS" title="AWS RDS">
</div>

<div style="display:flex">
<img src="/readme/MySQL.png" alt="MySQL" title="MySQL">
<img src="/readme/Google Sheets.png" alt="Google Sheets" title="Google Sheets">
<img src="/readme/Apps Script.png" alt="Apps Script" title="Apps Script">
<img src="/readme/SheetDB.png" alt="SheetDB" title="SheetDB">
<img src="/readme/GitHub Actions.png" alt="GitHub Actions" title="GitHub Actions">
</div>

#### Architecture Diagram

<img src="/documentation/README/Architecture Diagram.png" alt="Architecture Diagram" title="Architecture Diagram">

The app was built using Python and the Interactions.py library. It is connected to a MySQL database. 

Any changes made to the main branch in Git will automatically trigger the deploy script in Github Actions to deploy the app into an AWS EC2 instance, where the app is hosted. The MySQL instance in the AWS environment is hosted using AWS RDS. 

The app is integrated with Google Sheets by making API calls to API endpoints created in SheetDB, which interacts with Google Sheets, where an automatically triggered script in Apps Script updates the sheet accordingly.

<a name="DevEnvironment"></a>
## Development Environment
There are 2 Git Branches, the main branch contains the code with the most updated version of the app and is the version that is hosted in AWS and used in the Blossomz discord server at all times. The dev branch is used for the purposes of developing new features and expanding the app. 

When developing the app, only the dev branch is used for new commits, the changes are tested locally inside a development discord server that I created myself, as well as a local instance of MySql and local .env files to contain relevant configuration information. An alt account is also used for SheetDB API testing so as to avoid unnecessarily making API calls for the main SheetDB account that is used by the Blossomz discord server, due to the free tier of SheetDB having a monthly limit of API requests that can be made.

Whenever a new feature has been finished and is ready for deployment, I complete a pull request from the dev branch to the main branch. Github Actions is then triggered upon any changes being made to the main branch, running the deploy.yml script which deploys the new code into the AWS EC2 server where the app is hosted. 

<a name="Features"></a>
## Features

<a name="Guests"></a>
#### Managing Guests
Whenever a new guest joins the Blossomz discord server, they are prompted to read through the rules of the discord server and must respond to agree to the terms before they are allowed to see other text and voice channels in the server. Upon accepting the terms which constitutes as successful verification, they will then receive the Guest role. An admin is then required to make a decision on whether to keep their role as Guest which limits their privileges in the discord server, or to upgrade their role to Friend, Best Friend or Member, if they intended on joining the community with a higher level of involvement. 

Before BlossomzBot was created, an admin would have to manually check whether a new guest has accepted the terms and received the guest role before the admin can change their role to something else, this process can take an indefinite amount of time as sometimes new members who join the discord server take their time to read through the rules and verify themselves, or forget to do so and return many hours later to do it. Thus, admins will have to periodically check themselves whether the new guest has verified themselves already before changing their role, with the process of changing their role having to be done manually as well. 

I created a new text-channel inside the Blossomz discord server called #managing-guests which is only accessible by the admins. Once a new person who joins the discord server has verified themselves and received the guest role, this will appear in the #managing-guests channel:

<img src="/documentation/README/New Guest.png" alt="New Guest" title="New Guest">

To ensure that a new person only appears in this channel once and never again, their discord user ID is stored inside the database. The app will check whether the discord ID already exists in the database and if so, it will not make a new prompt inside the #managing-guests channel for the same person again. As long as admins enable notifications for this #managing-guests channel, they will be notified immediately that actions have to be taken to resolve this new guest's role. By clicking any of the options changes their role accordingly. The bot's message will then change to look like so:

<img src="/documentation/README/New Guest Edited.png" alt="New Guest Edited" title="New Guest Edited">

Inside the #blossomz-bot channel which contains the bot's logs, this will be shown: 

<img src="/documentation/README/New Guest Logs.png" alt="New Guest Logs" title="New Guest Logs">

The welcome message and google sheets features will be explained below.

<a name="Welcome"></a>
#### Welcome Message
When a new guest has joined and has their role changed to either Member or Best Friend, it means that they joined with the intention to be actively involved in the Blossomz community. In this case, a welcome message will be automatically sent by the bot to that person's direct messages inbox as a private personal message. This will hopefully make the person feel welcomed into the community, the message looks like so:

<img src="/documentation/README/Welcome Message.png" alt="Welcome Message" title="Welcome Message">

<a name="Google"></a>
#### Google Sheets Integration
As there are many members in the discord server, with some being members ingame in Lost Ark, some being non-members ingame but are active in the community, some being friends of the members, some being mere guests, there are a lot of people to manage. For convenient administration, it is helpful to keep track of the information of every person in the discord server inside a spreadsheet in google sheets that the Blossomz admins can all access. 

However, it will be a lot of manual work to maintain the spreadsheet whenever there is a new member or when existing discord server members are updated in some way. BlossomzBot solves this problem by automating much of these aforementioned problems, by automatically updating the google sheet whenever there is a new member in the discord server, when someone changes their display name or discord username, or has their role changed by an admin. 

The spreadsheet looks like this:

<img src="/documentation/README/Google Sheet.png" alt="Google Sheet" title="Google Sheet">

To make changes to the spreadsheet from the discord app, I make use of the SheetDB API which is a service that allows for easy communication with Google Sheets. However, with the free tier of SheetDB, there is a limited amount of API calls that can be made per month. Some changes made in the discord server would require multiple updates to be made in the sheets, for example changing a person's role would require first searching the spreadsheet for the tab with the role that person previously had, then searching through the sheet to find the row containing that person, delete that row, then searching for the tab for the new role that the person is given, then adding that row again. To fulfil even one use case can require many API calls to update the sheet as required. To get around this problem, I created this Holding Area tab in the sheet:

<img src="/documentation/README/Holding Area.png" alt="Holding Area" title="Holding Area">

Instead of using SheetDB's API to perform updates on the google sheet, whenever a new person is to be added or updated in the sheet, the discord app sends all the relevant information to the Holding Area. If there is no previous role, that means it is a new person and they are to be added. If there is a previous role and new role, that means it is an existing person and their role is to be updated, meaning the row containing their information have to be removed from a tab and then added to a different tab. If the previous role and new role are the same, it means that either their display name or discord username have changed, so their will simply just have to be updated within the same tab and same row. 

To read from the Holding Area tab and perform all the relevant operations to update the google sheet, I make use of Google Apps Script. The script that I wrote in App Script can be found <a href="/documentation/appScript.js">here</a>. The Apps Script is triggered automatically whenever a new entry is added to the Holding Area tab and it will perform the logic as I have described, to assess how to update the sheet accordingly. After the sheets have been updated, App Script sends a success message back to BlossomzBot, they are being connected via a weboook. The bot then logs the success message inside the #blossomz-bot channel. This is how the resulting logs look like whenever someone's role, display name or discord username has been updated:

<img src="/documentation/README/Role Change.png" alt="Role Change" title="Role Change">
<img src="/documentation/README/Name Change.png" alt="Name Change" title="Name Change">

The following diagram summarises the flow of this entire process:
<img src="/documentation/README/Flow Diagram.png" alt="Flow Diagram" title="Flow Diagram">

<a name="Commands"></a>
#### Slash Commands
Only the admins are allowed to use these commands. These are the slash commands created that are currently in service within the Blossomz discord server:

<img src="/documentation/README/Commands.png" alt="Commands" title="Commands">

(1) Configure

The configure command allows for enabling and disabling various BlossomzBot features, in the event that any of them are defective or causing problems, they can be disabled individually while the rest of the app can still continue running and working. This is what you see upon using the command: 

<img src="/documentation/README/Configure.png" alt="Configure" title="Configure">

These are the options for the dropdown: 

<img src="/documentation/README/Configure Options.png" alt="Configure Options" title="Configure Options">

(2) Kick Nicely

This allows admins to kick a member from the discord server, with the bot sending them a private personal message to explain the reason why they were kicked and also assuring them that they would be welcomed back if they wish to join back again. The message looks like this: 

<img src="/documentation/README/Kick Message.png" alt="Kick Message" title="Kick Message">

(3) Send Welcome Message

Allows admins to manually make BlossomzBot send a welcome message to a user by inputting a User ID. This command can be used in the event that a welcome message needs to be sent but was for some reason not able to be sent via the normal automated means.

(4) Insert All Member IDs (Archived, can be found <a href="/documentation/archived_commands.txt">here</a>)

Runs a script that loops through all the Member ID of everyone in the discord server and inserts them into the database if the Member ID does not already exist. This command was used at the very start when BlossomzBot was initially deployed, as the database was empty and not yet seeded with all the Member IDs of the existing members in the discord server. After this was done once, the command was archived as it is no longer needed.

(5) Write All to Spreadsheet (Archived, can be found <a href="/documentation/archived_commands.txt">here</a>)

Runs a script that loops through everyone in the discord server and inserts their relevant information into the google sheet. This command was used at the very start when BlossomzBot was initially deployed, as the google sheet was empty and not yet seeded with all the data of the existing members in the discord server. After this was done once, the command was archived as it is no longer needed.

<a name="Error"></a>
#### Error Handling
Errors detected in all try / except blocks are logged as a message by the bot into the blossomz-bot channel in the discord server. These error messages are specific to which function was being executed to allow for easier troubleshooting, with all error messages being defined inside <a href="/models/Messages.py">here</a>. If errors are caught from try / except blocks inside inner functions, the error is raised back up to the outer functions where the outer try / except blocks will make the bot log the error in the discord server. 
