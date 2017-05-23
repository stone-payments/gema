 param (
    [Parameter(Mandatory=$true)][string]$task,
    [Parameter(Mandatory=$true)][string]$environment,
    [Parameter(Mandatory=$true)][string]$pipeline
 )

$App_Url="https://gocd-env-management.paas.in-1.dc1.buy4.io"

[System.Net.ServicePointManager]::SecurityProtocol = @("Tls12","Tls11","Tls","Ssl3")
(Invoke-WebRequest -Uri "$App_Url/$($task)?env=$environment&pipeline=$pipeline").Content
