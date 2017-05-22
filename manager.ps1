 param (
    [Parameter(Mandatory=$true)][string]$action,
    [Parameter(Mandatory=$true)][string]$environment,
    [Parameter(Mandatory=$true)][string]$pipeline
 )

$App_Url="https://gocd-env-management.paas.in-1.dc1.buy4.io"

curl -Uri "$App_Url/$action?$env=environment&pipeline=$pipeline"
