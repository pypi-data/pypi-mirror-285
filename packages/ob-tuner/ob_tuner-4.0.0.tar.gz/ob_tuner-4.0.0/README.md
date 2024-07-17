# ob-tuner

![CI Status](https://github.com/svange/ob-tuner/actions/workflows/pipeline-prod.yaml/badge.svg?branch=main)
![CI Status](https://github.com/Woxom-Solutions/ob-tuner/actions/workflows/pipeline-prod.yaml/badge.svg?branch=dev)

![PyPI - Version](https://img.shields.io/pypi/v/ob-tuner)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg?style=flat-square)](https://conventionalcommits.org)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?style=flat-square&logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Made with GH Actions](https://img.shields.io/badge/CI-GitHub_Actions-blue?logo=github-actions&logoColor=white)](https://github.com/features/actions "Go to GitHub Actions homepage")
[![semantic-release](https://img.shields.io/badge/%20%20%F0%9F%93%A6%F0%9F%9A%80-semantic--release-e10079.svg)](https://github.com/semantic-release/semantic-release)

## Introduction

ob-tuner is a user-friendly, interactive GUI interface for creating, testing, and managing AI agents for OpenBrain. It provides a Gradio-based interface for users to create and fine-tune agent configurations and test various setups. The ob-tuner UI aims to simplify the process of working with AI agents by providing a comprehensive toolset for developers and researchers.

Your AI Agents will use tools, such as access to your CRM's API, to funnel leads into your campaigns. This UI gives you a place to tweak parameters of your agents (temperature, mode, tools, etc.), store the keys for any tools that require authentication, and test the agents in real-time.

![img_3.png](img_3.png)



## Features

- **Interactive GUI**: Easily create, modify, and test agent configurations using a web-based interface powered by Gradio.
- **Real-time Testing**: Test your agent configurations in real-time and see immediate feedback on changes.
- **Configuration Management**: Save, load, and manage different agent configurations using DynamoDB.


## Using ob-tuner

### Agent Configuration

In the ob-tuner interface, you can create and modify agent configurations. These configurations can be saved to your DynamoDB tables in AWS, allowing you to reference them in any AWS workflow using the boto3 library.

### Testing and Tuning

Use the interactive interface to test different configurations and fine-tune agent parameters. The interface provides real-time feedback, making it easy to see the effects of your changes immediately.

## Procedures

### Before Deploying

1. **Ensure AWSServiceRoleForElasticBeanstalk Exists**: 
   - Verify that the `AWSServiceRoleForElasticBeanstalk` exists in your roles. If it does not exist, create it using the AWS Management Console. The UI will guide you to create the role correctly without needing to fill in the name, trust relationship, or policy document.

2. **Register with Cognito**: 
   - Register with Amazon Cognito and obtain a `client_id` and `client_secret` for the OAuth2 client. You will need to provide your `callback_url` during this process.

3. **Create a Route53 Record for Your Base Domain**: 
   - Create a Route 53 record for your base domain. This requires a root A record in the root domain. For example, set `openbra.in` with an `A` record pointing to your EBS endpoint.

4. **Create a Custom Domain in Cognito**: 
   - Set up a custom domain in your Cognito user pool. Ensure the Route 53 record above is created first before proceeding with this step.

5. **Create an ACM Certificate**: 
   - Create a certificate in AWS Certificate Manager (ACM) for the custom domain.

6. **Create an SSH Key Pair**: 
   - Generate an SSH key pair and store the private key in a secure location. Use the key pair name in the `ec2_key_name` parameter.

7. **Add EBS Admin Access**:
   - Ensure that Elastic Beanstalk has the necessary administrative access.

   ![img_1.png](img_1.png)
   ![img_2.png](img_2.png)

### After Deploying

1. **Create a Route 53 Record Set**: 
   - Create a Route 53 record set pointing your callback URL domain to the Elastic Beanstalk URL.

   ![img.png](img.png)

### Note

- **Avoid Immediate Redeployment**: 
  - Do not redeploy the application for at least 5 minutes after a successful deployment to avoid failed runs. This requires additional logic in the deployment pipeline to handle such cases automatically.
  - 

 :construction: **The following procedures are not guaranteed to work, it's where the project is going though.** :construction:

## Quick Start

### Installation

Install ob-tuner and its dependencies using pip:

```bash
pip install ob-tuner
```

### Setting Up Your Environment

To set up your environment, create a `.env` file:

```bash
cp .env.example .env
```

Edit the `.env` file with your own values.

### Running ob-tuner

To launch the ob-tuner interface:

```bash
ob-tuner
```


## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to the project.

## License

ob-tuner is open-source software licensed under the AGPLv3. For commercial use, contact us.















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