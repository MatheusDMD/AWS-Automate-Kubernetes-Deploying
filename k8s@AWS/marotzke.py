import argparse, subprocess, pprint
from json import dumps, load

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARN = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    OKAY = '[{0}OK{1}]'.format('\033[92m','\033[0m')
    FAILED = '[{0}FAIL{1}]'.format('\033[91m','\033[0m')
    WARNING = '[{0}WARNING{1}]'.format('\033[93m','\033[0m')
    
possible_machines=[
    't2.nano',
    't2.micro',
    't2.small',
    't2.medium',
    't2.large',
    't2.xlarge',
    't2.2xlarge',
    'm4.large',
    'm4.xlarge',
    'm4.2xlarge',
    'm3.medium',
    'm3.large',
    'm3.xlarge',
    'm3.2xlarge'
    ]
possible_regions=[
    'us-east-2',
    'us-east-1',
    'us-west-1',
    'us-west-2',
    ]
possible_regions_deploy=[
    'us-west-2a',
    ]

def write_loadbalancer_file(args):
    with open( 'loadbalancer.json', 'w' ) as f:
        var = {
                "kind": "Service",
                "apiVersion": "v1",
                "metadata": {
                "name": "{0}-loadbalancer".format(args.name)
                },
                "spec": {
                "ports": [{
                        "name":"http",
                        "port": 80,
                        "targetPort": int(args.target_port)
                }],
                "selector": {
                        "app": "{0}".format(args.name)
                },
                "type": "LoadBalancer"
                }
                } 
        f.write(dumps(var,indent=4))
    success_log = "Loadbalancer configuration File  {0}".format(bcolors.OKAY)
    print(success_log)

def write_deploy_file(args):
    with open( 'deployment.yaml', 'w' ) as f:
        var = """
apiVersion: extensions/v1beta1
kind: Deployment
metadata:
  name: {0}
  labels:
    app: {0}
spec:
  replicas: {2}
  template:
    metadata:
      labels:
        app: {0}
    spec:
      containers:
      - name: {0}
        image: {1}
        ports:
        - containerPort: 80

        """.format(args.name, args.image, args.replicas)
        f.write( var )
    success_log = "Deployment configuration File    {0}".format(bcolors.OKAY)
    print(success_log)

def execute_command(var, success_log=None, fail_log=None, extra_print=None, diplay_output=True,special_case=False):
    process = subprocess.Popen(var, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process.wait()
    output, error = process.communicate()
    if special_case:
        if success_log:
            print(success_log)
    if error.decode("utf-8") == '':
        if success_log:
            print(success_log)
        if extra_print:
            print(extra_print)
        if diplay_output:
            print(output.decode("utf-8"))
    else:
        if not special_case:
            if fail_log:
                print(fail_log)
            if diplay_output:
                print(error.decode("utf-8"))

def hosted(args):
    print()
    var = "aws route53 create-hosted-zone --name {0} --caller-reference $(uuidgen) | jq .DelegationSet.NameServers".format(args.domain)
    success_log = "Configuring Hosted Zone          {0}".format(bcolors.OKAY)
    fail_log    = "Configuring Hosted Zone          {0}".format(bcolors.FAILED)
    extra_print = "Use this addresses to your domain Name Servers:"
    execute_command(var, success_log, fail_log, extra_print)

def create_bucket(args):
    var = "aws s3api create-bucket --bucket {0} --create-bucket-configuration LocationConstraint={1}".format(args.domain, args.zones)
    success_log = "Creating Bucket                  {0}".format(bcolors.OKAY)
    fail_log    = "Creating Bucket                  {0}".format(bcolors.WARNING)
    execute_command(var,success_log, fail_log)

def bucket_config_versioning(args):
    var = "aws s3api put-bucket-versioning --bucket {0} --versioning-configuration Status=Enabled".format(args.domain)
    success_log = "Setup Bucket Versioning          {0}".format(bcolors.OKAY)
    fail_log    = "Setup Bucket Versioning          {0}".format(bcolors.FAILED)
    execute_command(var,success_log, fail_log)

def kops_environment_variable_setup(args):
    var = "export KOPS_STATE_STORE=s3://{0}".format(args.domain)
    execute_command(var)

def deploy_using_kops(args):
    var = "kops create cluster --name {0} --zones us-west-2a --master-size {1} --node-size {2} --state s3://{0} --yes".format(args.domain, args.master_size, args.node_size)
    success_log = "Create Instances with Kops       {0}".format(bcolors.OKAY)
    fail_log    = "Create Instances with Kops       {0}".format(bcolors.FAILED)
    execute_command(var,success_log, fail_log, diplay_output=False, special_case=True)

def image_deployment(args):
    var = "kubectl create -f deployment.yaml"
    success_log = "Image Deployment                 {0}".format(bcolors.OKAY)
    fail_log    = "Image Deployment                 {0}".format(bcolors.FAILED)
    execute_command(var,success_log, fail_log, diplay_output=True)    

def loadbalancer_deployment(args):
    var = "kubectl create -f loadbalancer.json"
    success_log = "Loadbalancer Deployment          {0}".format(bcolors.OKAY)
    fail_log    = "Loadbalancer Deployment          {0}".format(bcolors.FAILED)
    execute_command(var,success_log, fail_log, diplay_output=True)    

def create(args):
    print()
    create_bucket(args)       
    bucket_config_versioning(args)
    kops_environment_variable_setup(args)
    deploy_using_kops(args)
    print("Cluster Creation                 {0}\n".format(bcolors.OKAY))
    print("Run 'deploy' command when cluster is up.\n It may take [3-4] min to be up.\n")
#     else:
#         print("Cluster Creation                 {0}\n".format(bcolors.FAILED))

def deploy(args):
    print()
    write_deploy_file(args)
    image_deployment(args)
    write_loadbalancer_file(args)
    loadbalancer_deployment(args)
    print("Deployment                       {0}\n".format(bcolors.OKAY))
    print("Done. Access it though the URL or with via REST. It may take [2-3] min to be up.\n")

def delete(args):
    print()
    decision = input("Are you sure you want to delete your cluster? [y/N] ")
    print()
    if decision.lower() == 'y' or decision.lower() == 'yes':
        var = "kops delete cluster --name={0} --state=s3://{0} --yes".format(args.domain)
        success_log = "Cluster Deleted                  {0}\n".format(bcolors.OKAY)
        fail_log    = "Cluster Deleted                  {0}\n".format(bcolors.FAILED)
        execute_command(var, success_log, fail_log)
        print("Cluster Deleted                  {0}\n".format(bcolors.OKAY))
        print("Instances are now terminating. It may take [2-3] min to be up.\n")
    else:
        print("Deletion Aborted.\n")

def bye(args):
    print(args)
    print("Configuring Bucket       {0}".format(bcolors.WARNING))
    print("Configuring Bucket       {0}".format(bcolors.FAILED))

FUNCTION_MAP = {'create': create, 'config': hosted, 'deploy': deploy ,'delete': delete }

parser = argparse.ArgumentParser(description='Marotzke Deployement Services')

parser.add_argument('command',choices=FUNCTION_MAP.keys())

parser.add_argument('--name', default='matheusmarotzke-webapp', 
        help='application name (default: %(default)s)')

parser.add_argument('--zones',choices=possible_regions, default='us-east-2', 
        help='the zones to run instances (default: %(default)s)')

parser.add_argument('--master-size',choices=possible_machines, default='t2.micro', 
        help='the size of master machine (default: %(default)s)')

parser.add_argument('--node-size',choices=possible_machines, default='t2.micro', 
        help='the size of node machine (default: %(default)s)')

parser.add_argument('--domain', default='cluster.matheusmarotzke.com', 
        help='application domain for cluster (default: %(default)s)')

parser.add_argument('--image', default='matheusdmd/python-simple:v2', 
        help='image to be deployed (default: %(default)s)')

parser.add_argument('--target-port', default='80', 
        help='target port for your deployed application (default: %(default)s)')

parser.add_argument('--replicas', default='2', 
        help='number of pod replicas for the cluster(default: %(default)s)')

args = parser.parse_args()
func = FUNCTION_MAP[args.command]
func(args)  