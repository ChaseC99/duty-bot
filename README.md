# Duty Bot
A bot to track Mesa Court's Duty Schedule.  

### Features
- Post the Mesa Court Duty Schedule everyday at 4pm on Slack
<html>
<img src="https://raw.githubusercontent.com/ChaseC99/duty-bot/master/assets/screenshots/duty-team.png" height=300px>
</html>

- Track changes to the Mesa Court Duty Schedule
<html>
<img src="https://github.com/ChaseC99/duty-bot/blob/master/assets/screenshots/event-updated.png?raw=true" height=200px>
<img src="https://github.com/ChaseC99/duty-bot/blob/master/assets/screenshots/event-created-deleted.png?raw=true" height=200px>
</html>

### Dependencies
Slack : `pip3 install slackclient`  
Schedule : `pip3 install schedule`

### Building an deployment package
To create a deployable zip file, run the following script in the project's root directory: `./build_deployment.sh`
