#!/usr/bin/env bash

echo "Git clone zhmcclient ..."
git clone http://github.rtp.raleigh.ibm.com/openstack-zkvm/python-zhmcclient.git

echo "Install development tools ..."
cd python-zhmcclient
make develop

echo "Build zhmcclient ..."
make build

echo "Install zhmcclient ..."
make install
