# Kubernetes @ AWS Automate Deployement

## SOLUTION DIAGRAM

![alt text](https://github.com/MatheusDMD/AWS-Automate-Kubernetes-Deploying/blob/master/images/solution_diagram.jpg "Diagram")

## PRE-REQUIREMENTS

- `brew install kubectl`
- `brew install kops`
- `brew install jq`
- `install awscli` (and configure key-set)

## CLUSTER
[CLI code](https://github.com/MatheusDMD/AWS-Automate-Kubernetes-Deploying/blob/master/k8s%40AWS/marotzke.py)

### Creates a bucket on S3

create AWS BUCKET
[include location constraint](docs.aws.amazon.com/general/latest/gr/rande.html)

- `aws s3api create-bucket --bucket <your_domain> --create-bucket-configuration LocationConstraint=us-east-2`

```
returned :
{
    "Location": "http://<your_domain>.s3.amazonaws.com/"
}
```

### Creates a Hosted-Zone on Route53
So that Kops can have a fixed address to your apllication.

- `aws s3api put-bucket-versioning --bucket <your_domain> --versioning-configuration Status=Enabled`

- `export KOPS_STATE_STORE=s3://<your_domain>`

- `ID=$(uuidgen) && aws route53 create-hosted-zone --name <your_domain> --caller-reference $ID | jq .DelegationSet.NameServers`

Using the domain name for the bucket name is only a form of better keeping track of names, but it's not a requirement.

### Set your domain Name Space
Use these name servers to change the configuration of your domain.
```
returned:
[
  "ns-122.awsdns-09.com",
  "ns-591.awsdns-13.net",
  "ns-1233.awsdns-35.co.uk",
  "ns-1129.awsdns-11.org"
]
```

![alt text](https://github.com/MatheusDMD/AWS-Automate-Kubernetes-Deploying/blob/master/images/tutorial.jpeg "how to set it up on Google Domains")

This is the UI to set it up on Google Domains.

### Creating the cluster

- `kops create cluster --name <your_domain> --zones us-west-2a --master-size t2.micro --node-size t2.micro --state s3://<your_domain> --yes`

Creates the instances of master and nodes for your cluster in the specified region and size.

Automatically changes the environment of `kubectl` to your new cluster.

[2-3 min]


## DEPLOYING DOCKER FILE

- `kubectl create -f deployment.yaml`

Creates the application and deploys an image with the specific number of pods/replicas from your docker-hub repo. (It also works with different services like Amazon ECS).

deployment.yaml:

```
apiVersion: extensions/v1beta1
kind: Deployment
metadata:
  name: <your_webapp_name>
  labels:
    app: <your_webapp_name>
spec:
  replicas: 1
  template:
    metadata:
      labels:
        app: <your_webapp_name>
    spec:
      containers:
      - name: <your_webapp_name>
        image: <your_image_from_docker_hub>
        ports:
        - containerPort: 80
```

- `kubectl create -f loadbalancer.json`

loadbalancer.json:

```
{
    "kind": "Service",
    "apiVersion": "v1",
    "metadata": {
      "name": "<your_webapp_name>-loadbalancer"
    },
    "spec": {
      "ports": [{
        "name":"http",
        "port": 80,
        "targetPort": <application_port>
      }],
      "selector": {
        "app": "<your_webapp_name>"
      },
      "type": "LoadBalancer"
    }
  }
```
[2 min]

`kubectl get service`

`kubectl describe service <your_webapp_name>-loadbalancer`

Get the link from `LoadBalancer Ingress:` that will allow you to access your application. 

## DELETING THE WHOLE THING

`kops delete cluster --name=<your_domain> --state=s3://<your_domain>`

Your Route53 and the S3 service will still be running.


## NEXT STEPS

- Implement Auto-scaling
- Add more possible configurations
- Add 'update' image features
- Implement a generic cli REST api

