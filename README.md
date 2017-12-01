# AWS Docker Image Deployer

## Pre-requirements

- `brew install kubectl`
- `brew install kops`
- `brew install jq`
- `install awscli`

## CLUSTER

create AWS BUCKET
[include location constraint](docs.aws.amazon.com/general/latest/gr/rande.html)
(`--create-bucket-configuration LocationConstraint=us-east-2`)

`aws s3api create-bucket --bucket cluster.matheusmarotzke.com --create-bucket-configuration LocationConstraint=us-east-2`

returned :
{
    "Location": "http://cluster.matheusmarotzke.com.s3.amazonaws.com/"
}

`aws s3api put-bucket-versioning --bucket cluster.matheusmarotzke.com --versioning-configuration Status=Enabled`

`export KOPS_STATE_STORE=s3://cluster.matheusmarotzke.com`

`ID=$(uuidgen) && aws route53 create-hosted-zone --name cluster.matheusmarotzke.com --caller-reference $ID | jq .DelegationSet.NameServers`
returned:
[
  "ns-123.awsdns-15.com",
  "ns-590.awsdns-09.net",
  "ns-1743.awsdns-25.co.uk",
  "ns-1109.awsdns-10.org"
]

`kops create cluster --name cluster.matheusmarotzke.com --zones us-west-2a --master-size t2.micro --node-size t2.micro --state s3://cluster.matheusmarotzke.com --yes`

auto-changes the environment to your new cluster

(2-3 min)


## DEPLOYING DOCKER FILE
`kubectl create -f deployment.yaml`

deployment.yaml
"""
apiVersion: extensions/v1beta1
kind: Deployment
metadata:
  name: matheusmarotzke-webapp
  labels:
    app: matheusmarotzke-webapp
spec:
  replicas: 1
  template:
    metadata:
      labels:
        app: matheusmarotzke-webapp
    spec:
      containers:
      - name: matheusmarotzke-webapp
        image: matheusdmd/python-simple:v1
        ports:
        - containerPort: 80
"""

`kubectl create -f loadbalancer.json`
"""
{
    "kind": "Service",
    "apiVersion": "v1",
    "metadata": {
      "name": "matheusmarotzke-webapp-loadbalancer"
    },
    "spec": {
      "ports": [{
        "name":"http",
        "port": 80,
        "targetPort": 80
      }],
      "selector": {
        "app": "matheusmarotzke-webapp"
      },
      "type": "LoadBalancer"
    }
  }
  """
2 min

`kubectl get service`

`kubectl describe service matheusmarotzke-webapp-loadbalancer`

## DELETING THE WHOLE THING

`kops delete cluster --name=cluster.matheusmarotzke.com --state=s3://cluster.matheusmarotzke.com`
