# Nessus
[https://intranet.hbtn.io/projects/3179](https://intranet.hbtn.io/projects/3179)


## Lab Environment – VM Access Links

**Howering your mouse over the VM name on the project page will reveal a clickable link allowing to download the VM.**

Download the **Ubuntu Server** and **Metasploitable 2** VMs from the project page and import them into your virtualization software (e.g., VirtualBox \ File \ Import Appliance).

Ubuntu Server is configured with a NAT interface; Metasploitable 2 comes without network interface - we have to add a Host-Only Adapter with Promiscuous Mode set to Allow VMs (select imported VM, go to Settings \ Network \ Adapter).

We are going to use our own Kali, which is already configured with a NAT interface and if not present then add a Host-Only Adapter with Promiscuous Mode set to Allow VMs.  The Host-Only Adapter is required for the Nessus scanner to communicate with the Metasploitable 2 VM.

### Ubuntu Server:

- **Login:** user
- **Password:** user

### Kali Linux  \<- recommended to use own Kali since we installed Nessus on it

- **Login:** kali
- **Password:** kali

### Metasploitable 2:

- **Login:** msfadmin
- **Password:** msfadmin


## Task 0 - Web Application Scan on DVWA

**Lab Information**

| Field           | Value |
|-------          |-------|
| Scanner         | Nessus Essentials on Kali Linux (192.168.56.10) |
| Target          | DVWA on Ubuntu Server (192.168.56.20) |
| Target URL      | http://192.168.56.20/dvwa |
| Nessus Template | Web Application Tests |




