# Duty Bot
A bot to track Mesa Court's Duty Schedule.

Every day at 3:45pm, it loads the Mesa Court Duty schedule from Roompact and posts it in Slack.  
<img src="assets/screenshots/duty-team.png" height=300px>

### Dependencies
Slack : `pip3 install slackclient`  
Schedule : `pip3 install schedule`

### Building an deployment package
To create a deployable zip file, run the following script in the project's root directory: `./build_deployment.sh`
