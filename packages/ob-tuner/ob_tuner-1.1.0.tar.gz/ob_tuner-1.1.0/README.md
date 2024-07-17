# OB Tuner

An AI agent tuning tool for OpenBra.in agents.

## Procedures

### Before deploying

1. Ensure AWSServiceRoleForElasticBeanstalk exists in your roles, if not, create it. Use the UI and it weil be created correctly without havingto fill in the name or trust relationship or policy document.

1. Before deploying, register with Cognito and get a `client_id` and `client_secret` for the OAuth2 client. You will need to provide your `callback_url`.

1. Before deploying, create a Route53 record for your base domain. This requires a root A record in the root domain. For example `openbra.in` `A` `EBS endpoint`.


1. Before deploying, create a custom domain in your cognito user pool. This requires the record above to be created first.

1. Before deploying you must creaet a certificate in ACM for the custom domain.

1. Before deploying, create ssh keypair and store the private key in a secure location. Use the key pair name in the `ec2_key_name` parameter.

1. Befoer deploying, add EBS admin access 
![img_1.png](img_1.png)![img_2.png](img_2.png)


### After deploying
1. After deploying, create a Route 53 record set pointing your callback URL domain to the EBS URL.
![img.png](img.png)


NOTE:
Do not redeploy app for at least 5 minutes (if last one was succesful) to avoid failed runs... requires more logic in the pipeline to automate this case