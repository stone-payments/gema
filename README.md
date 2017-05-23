# GEMA - GoCD Environment Manager Application
App to manage environments of pipelines in gocd from the command line.

# Quickstart
This app uses a curl command tool to interact with the GEMA, which internally interacts with the GoCD API in order to manage the environment's pipelines.

Please download the appropriate version for your system. Windows users should download 'gema.ps1' and linux users should download 'gema.sh'.
(If you're a linux user, don't forget to chmod +x gema.sh)

The app implements just 3 simple commands to manage the GoCD's pipelines environments:

- list
- add
- remove

In order to check if a pipeline 'PIPELINE' is in the environment 'ENV', type this in your command prompt:
```
 	# ./gema.sh list ENV PIPELINE
```

In order to add a pipeline 'PIPELINE' to the environment 'ENV', type this in your command prompt:
```
 	# ./gema.sh add ENV PIPELINE
```

In order to remove a pipeline 'PIPELINE' from the environment 'ENV', type this in your command prompt:
```
 	# ./gema.sh remove ENV PIPELINE
```

# Installation
In order to run this app, first you will need to define these environment URLs:

GOCD_URL
	- The complete URL of the GoCD server, including the port. Ex: "https://gocd.io:8154"

GEMA_USER:
	- The username who is going to interact with the GoCD API. This user must have permission to manage the GoCD environments.

GEMA_PASS:
	- The password of the GoCD user.

RESTRICTED_ENVS:
	- A list of restricted environments separeted by ",". These are environents where the user cannot add or remove pipelines to, for exemple, Production.

When these environment URLs have been defined, just start the app with:
```
	# python gema.py
```
This will start the app, opening the port 8888 for the users to connect to, acording to the #quickstart.

# Questions?
If you have any questions or suggestions, please feel free to email us at qaas at stone.com.br.
