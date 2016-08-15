# z Systems Hardware Management Console Web Services API Ansible Module 

Ansible module for [HMC Web Services API](http://www-01.ibm.com/support/docview.wss?uid=isg29b97f40675618ba085257a6a00777bea), written in Python.


## Checkout Repository
    
    git clone git@github.rtp.raleigh.ibm.com:openstack-zkvm/zhmc-ansible.git

## Installation 
### With Virtualbox and Vagrant

    vagrant up
    vagrant ssh
    cd /vagrant

### On existing Operating System

* Install [Ansible](http://docs.ansible.com/ansible/intro_installation.html)
* Install [Requests Package](http://docs.python-requests.org/en/master/user/install/)
    
## Edit config file ansible/vars.yml

Edit the configuration file vars.yml in the ansible folder and update the values for 
* hmc_address
* ws_api_userid
* ws_api_password
* cpc_name
* lpar_name
* load_address (in case you have a ECKD disk)

## Run playbooks

    cd ansible
    ansible-playbook example_play.yml
