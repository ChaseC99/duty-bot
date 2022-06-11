# Duty Bot
A bot to track Mesa Court's Duty Schedule.

Every day at 3:45pm, it loads the Mesa Court Duty schedule from Roompact and posts it in Slack.  
<img src="assets/screenshots/duty-team.png" height=300px>

### Dependencies
Slack : `pip3 install slackclient`  
Schedule : `pip3 install schedule`

### Building an deployment package
To create a deployable zip file, run the following script in the project's root directory: `./build_deployment.sh`

## Setting up Duty Bot in a new Slack

### Creating a new Duty Bot App
1. Navigate to https://api.slack.com/apps
2. Click "Create New App"
3. Select "From an app manifest"
4. Pick the workspace you want to install Duty Bot to.
5. Copy and paste the content from [manifest.yml](manifest.yml) into the "Enter app manifest below" textbox
6. Click create!
7. Finally, click "Install to Workspace" and allow all permissions.

Once the app is installed, you need to update the OAuth token in the `config.py` file.  
To get the OAuth token, click on the "Add features and functionality" dropdown, then click the "Permissions" link.  
Copy the `Bot User OAuth Token` and paste it `config.py`.

### Customizing your Duty Bot
1. Navigate to https://api.slack.com/apps
2. Select "Duty Bot"
3. Scroll down to "Display Information" at the bottom 
4. Add the [Duty Bot Logo](assets/duty-bot.png) as the App Icon
