Vagrant.configure("2") do |config|
    config.vm.box = "StefanScherer/windows_2019"
    config.vm.box_version = "2019.11.15"
    config.vm.provider :vmware_desktop do |vmware|
        vmware.gui = true
    end
    config.vm.network "private_network", ip: "192.168.33.10"
    config.vm.synced_folder '.', '/vagrant', disabled: true
end