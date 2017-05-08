# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"


Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "ubuntu/trusty64"
  if Vagrant::Util::Platform.windows? then
    config.vm.synced_folder ".", "/vagrant", type: "rsync", rsync__exclude: ".git/"
    config.vm.provision "ansible_local" do |ansible|
      ansible.playbook = "provision.yml"
    end
  else
    config.vm.provision "ansible", playbook: "provision.yml"
  end
end
