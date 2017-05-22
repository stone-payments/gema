# gocd-env-management
App to manage environments of pipelines in gocd from the command line.

# Quickstart
This app is intended to be used with curl, where you will type a curl in your command prompt and the app will interact with the GoCD api in order to manage the environment's pipelines.

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

