 param (
    [Parameter(Mandatory=$true)][string]$task,
    [Parameter(Mandatory=$true)][string]$environment,
    [Parameter(Mandatory=$true)][string]$pipeline
 )

$App_Url="https://gema.stone.com.br"

[System.Net.ServicePointManager]::SecurityProtocol = @("Tls12","Tls11","Tls","Ssl3")
(Invoke-WebRequest -Uri "$App_Url/$($task)?env=$environment&pipeline=$pipeline" -UseBasicParsing).Content 
