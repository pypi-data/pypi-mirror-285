## echostream-managed-app

EchoStream managed app is a part of your EchoStream tenant. It maintains [echostream managed nodes](https://docs.echo.stream/v1/docs/managed-node) throughout their lifecycle. It runs as daemon service on your or your partner's compute environment. 

It is packaged as a part of your seed.iso (boot image), it can be downloaded from EchoStream application UI or through an api call. The boot image hardens the VM and configures all necessary things to let the managed app run.

> Note: version >=0.3.0 requires Python 3.12

### What echostream-managed-app does?
- It starts up app change receiver node and starts receiving messages from app change router.
- Pull Docker images from private EchoStream ecr or public-ecr.
- Startup/kill managed-node docker containers as they are added/removed in/through the UI/API.
- Restart managed-nodes if there is any part of node config got updated or edges between the nodes are modified.
- It runs containers on isolated docker network.
- Upstream the app/node logs to cloudwatch.

### Configuration
Requirements and other configuration for testing the managed app in local env.
#### Env vars
Below are the required env vars. These can be found in `user-data` file in your app's boot image (seed.iso)
- APP
- APPSYNC_ENDPOINT
- AWS_DEFAULT_REGION
- CLIENT_ID
- LOG_GROUP_NAME
- PASSWORD
- TENANT
- USER_NAME
- USER_POOL_ID

#### other requirements
- The necessary pip packages for this app are in `requirements.dev.txt`.
- Docker engine must be installed.
- This app looks for aws credentials in environment variables or at `~/.aws/credentials`. 
These aws credentials should have access to login/pull images from ecr and write access to cloudwatch logs.

```
"ecr-public:DescribeImages",
"ecr-public:GetAuthorizationToken"
"ecr:BatchCheckLayerAvailability"
"ecr:BatchGetImage",
"ecr:DescribeImages",
"ecr:DescribeRepositories",
"ecr:GetAuthorizationToken",
"ecr:GetDownloadUrlForLayer",
"ecr:GetRepositoryPolicy",
"ecr:ListImages",
"logs:CreateLogStream"
"logs:PutLogEvents",
"sts:GetServiceBearerToken",
```

### Usage
- After environment variables are sourced and Docker engine is running, the app can be started by python interpreter `python echostream_managed_app/__init__.py`. 
- The app starts to receive messages from app change receiver and starts managing the nodes on the docker.
- The logs are written to `/var/log/echostream/echostream-managed-app.log`

#### Note:
- AWS credentials can be passed into environment using aws-vault.
- If access is denied to write to the log file, either run as sudo or change the log destination which is accessible.
- For more verbose logs, set the logging level to `DEBUG`

More details here: [Managed-app](https://docs.echo.stream/docs/managed-app)