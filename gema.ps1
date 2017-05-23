 param (
    [Parameter(Mandatory=$true)][string]$task,
    [Parameter(Mandatory=$true)][string]$environment,
    [Parameter(Mandatory=$true)][string]$pipeline
 )

$App_Url="https://gocd-env-management.paas.in-1.dc1.buy4.io"

#[System.Net.ServicePointManager]::ServerCertificateValidationCallback = {$true}
#[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
#[System.Net.ServicePointManager]::CertificatePolicy = New-Object TrustAllCertsPolicy
#[System.Net.ServicePointManager]::ServerCertificateValidationCallback = {$true}
#[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

add-type @"
    using System.Net;
    using System.Security.Cryptography.X509Certificates;
    
    public class IDontCarePolicy : ICertificatePolicy {
        public IDontCarePolicy() {}
        public bool CheckValidationResult(
            ServicePoint sPoint, X509Certificate cert,
            WebRequest wRequest, int certProb) {
            return true;
        }
    }
"@
[System.Net.ServicePointManager]::CertificatePolicy = new-object IDontCarePolicy 

$connection_string = "$App_Url/$($task)?env=$environment&pipeline=$pipeline"
"$connection_string"
Invoke-WebRequest -Uri "$App_Url/$($task)?env=$environment&pipeline=$pipeline"
