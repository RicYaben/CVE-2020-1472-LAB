# ZeroLogon testing script

A lab setup to test a vulnerability for the ZeroLogon exploit (CVE-2020-1472).
It contains a Python script that uses the Impacket library to test the vulnerability, and a Virtual Machine (VM) with Windows Server 2019 configured as a Domain Controller (DC).

The script attempts to perform the Netlogon authentication bypass.
It will immediately terminate when successfully performing the bypass, and not perform any Netlogon operations.
When the DC is patched, the detection script will give up after sending a number of pairs of RPC calls and conclude the target is not vulnerable (with a false negative chance of 0.04%).

<details open>
    <summary><b>Requirements</b></summary>

- VMWare workstation/fusion
- Vagrant
- Python (^v3.7)

**Optional**

- Docker
  
</details>

Simply type `vagrant up` to load a vulnerable build of Windows Server 2019 as a VM.
Then, configure the VM as a Domain Controller following [this tutorial](https://www.virtualgyanis.com/post/step-by-step-how-to-install-and-configure-domain-controller-on-windows-server-2019).
Lastly, launch the attack on the DC (`zerologon_tester.py`).
It is recommended to use the Dockerised version of this attack or in a `virtual environment`.

- **`Docker` option.** Run:
  
    ```bash
    # NOTE: On Windows, you may need to enable the `Hyper-V` Wiwndows feature.
    # NOTE2: On Windows, you may need to switch to `Linux Containers`.
    $ docker build -f Dockerfile . -t zerologon
    # This command run the zerologon test on the DC with domain VAGRANT in the address 192.168.33.10
    $ docker run zerologon VAGRANT 192.168.33.10
    ```

- **`VirtualEnv` option.** Run:

    ```bash
    $ python3 -m virtualenv zerologon
    $ zerologon/Scripts/Activate.ps1
    # NOTE: This may give you some issues with your firewall!!
    $ pip install git+https://github.com/SecureAuthCorp/impacket
    $ pip install -r requirements.txt
    $ python zerologon_tester.py VAGRANT 192.168.33.10
    ```

---
The output of this attack should look something like this:

![zerologon](assets/attack.png)

This script is only meant to test the viability of the attack, it does not exploit the server in any other way.
The script does not perform any changes to the DC.
If you are curious about how to implement a PoC attack, check [this](https://medium.com/mii-cybersec/zerologon-easy-way-to-take-over-active-directory-exploitation-c4b38c63a915) writeup or a similar one.

---

The script targets can be used to target a DC or backup DC. It likely also works against a read-only DC, but this has not been tested. The DC name should be its NetBIOS computer name. If this name is not correct, the script will likely fail with a `STATUS_INVALID_COMPUTER_NAME` error. A whitepaper on this vulnerability will be published [here](https://www.secura.com/blog/zero-logon).


> **NOTE**:
> If something goes sideways and you receive a `STATUS_INVALID_COMPUTER_NAME` error, run `nbtstat -A 192.168.33.10`, this will give you some insight on what is going on in that address. Otherwise, you can always test wether the machine is reachable from your host by pinging it (`ping 192.168.33.10`).
>
> **NOTE2**:
> If the attack fails, it may be that the machine has been updated with security patches. Check the updates and remove anything that looks like `Security Patches` from 2020 onwards.
