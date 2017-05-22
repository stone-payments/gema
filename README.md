# gocd-env-management
App to manage environments of pipelines in gocd from the command line.

# Quickstart
This app is intended to be used with curl, where you will type a curl in your command prompt and the app will interact with the GoCD API in order to manage the environment's pipelines.

This app implements just 3 simple commands to manage the GoCD's pipelines environments:

- list
- add
- remove

In order to check if a pipeline 'PIPELINE' is in the environment 'ENV', type this in your command prompt:
```
 	# curl "APP_URL/list?env=ENV&pipeline=PIPELINE"
```

In order to addd a pipeline 'PIPELINE' to the environment 'ENV', type this in your command prompt:
```
	# curl "APP_URL/add?env=ENV&pipeline=PIPELINE"
```

In order to remove a pipeline 'PIPELINE' from the environment 'ENV', type this in your command prompt:
```
	# curl "APP_URL/remove?env=ENV&pipeline=PIPELINE"
```

# Installation
In order to run this app, first you will need to define these environment URLs:

GOCD_URL
	- The complete URL of the GoCD server, including the port. Ex: "https://gocd.io:8154"

GEM_USER:
	- The username who is going to interact with the GoCD API. This user must have permission to manage the GoCD environments.

GEM_PASS:
	- The password of the GoCD user.

RESTRICTED_ENVS:
	- A list of restricted environments separeted by ",". These are environents where the user cannot add or remove pipelines to, for exemple, Production.

When these environment URLs have been defined, just start the app with:
```
	# python gocd_integration.py
```
This will start the app, opening the port 8888 for the users to connect to, acording to the #quickstart.

# Questions?
If you have any questions or suggestions, please feel free to email us at qaas at stone.com.br.
