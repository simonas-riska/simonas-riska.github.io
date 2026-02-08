---
title: Lab Architecture
---

# Lab Architecture

## Endpoint Provisioning

A clean Windows 11 Enterprise virtual machine was deployed to act as the monitored endpoint for the incident response lab.

- Windows 11 Enterprise (Evaluation)
- 64-bit edition
- Single endpoint, standalone (non-domain joined)
- Intended to simulate a typical corporate workstation

The virtual machine was created from an official Microsoft ISO and installed without additional third-party software to preserve a clean baseline.

At this stage, the endpoint contained:
- No third-party security tools
- No additional user activity
- Default Windows configuration only

This baseline was preserved to ensure all observed activity during the incident could be attributed to the simulated scenario.

![Windows 11 Enterprise VM created from official ISO](images/win11-vm-iso.png)

*Figure 1: Windows 11 Enterprise ISO selected during virtual machine creation.*

![Clean Windows 11 desktop after installation](images/win11-desktop.png)

*Figure 2: Clean Windows 11 Enterprise endpoint baseline prior to telemetry and agent installation.*

## User Accounts

### Standard Local User Account

A standard local user account was created to simulate a typical corporate end-user context for the incident scenario.

- Username: employee1
- Account type: Standard user
- Local group membership: Users

The account was intentionally not granted administrative privileges to reflect a common enterprise workstation configuration and to support realistic privilege boundaries and execution context during investigation.

![Standard user account creation](images/user-account-create.png)

*Figure 3: Creation of a standard local user account for the lab endpoint.*

![User group membership](images/user-account-groups.png)

*Figure 4: Verification that the user is a member of the local Users group only.*

### Local Administrator Account

A separate local administrator account was created to represent privileged access on the endpoint.

- Username: admin1
- Account type: Local administrator
- Local group membership: Administrators

This account was created to support realistic privilege separation during investigation, including analysis of execution context, potential privilege escalation attempts, and differentiation between standard and administrative activity.

![Administrator account creation](images/admin-account-create.png)

*Figure 5: Creation of a dedicated local administrator account for the lab endpoint.*

![Administrator group assignment](images/admin-account-groups.png)

*Figure 6: Verification that the account is a member of the local Administrators group.*

## Windows Event Logging

Default Windows Event Logging was confirmed to be enabled on the endpoint, including the following log channels:

- Security
- System
- Application

These logs provide core visibility into authentication events, system changes, service activity, and application-level errors, and form the baseline telemetry for subsequent investigation and correlation with enhanced logging sources.

![Command-line logging policy enabled](images/gpo-command-line-enabled.png)

*Figure 7: Command-line inclusion enabled for process creation audit events.*

![Audit Process Creation policy](images/audit-process-creation.png)

*Figure 8: Local Security Policy showing Audit Process Creation enabled.*

![Group Policy update](images/gpupdate-force.png)

*Figure 9: Policy refresh to apply updated audit settings.*

![whoami execution](images/whoami-execution.png)

*Figure 10: Manual execution used to generate a test process creation event.*

![Event 4688 with command-line captured](images/event4688-commandline.png)

*Figure 11: Security Event ID 4688 showing command-line arguments and user context.*

## Process Command-Line Logging

Process command-line logging was enabled to enhance visibility into process execution details during investigation.

The following configuration was applied:
- Audit Process Creation enabled (Success)
- Command-line arguments included in process creation events

This configuration ensures that Security Event ID 4688 includes full command-line arguments, allowing reconstruction of execution intent during incident analysis.

## PowerShell Logging Configuration

Enhanced PowerShell logging was enabled on the endpoint to provide deep visibility into PowerShell-based execution during the simulated incident scenario.

The configuration was designed to ensure that:
- PowerShell script contents are captured, including dynamically generated and decoded commands
- Module-level activity is logged to support investigation of living-off-the-land techniques
- PowerShell events can be correlated with process creation, user context, and persistence mechanisms

Both **Script Block Logging** and **Module Logging** were enabled via Local Group Policy.

![PowerShell policy path](images/gpo-powershell-policy-path.png)

*Figure 12: Local Group Policy Editor path for PowerShell logging configuration.*

![Script Block Logging enabled](images/ps-scriptblock-logging-policy-enabled.png)

*Figure 13: PowerShell Script Block Logging enabled via Local Group Policy.*

![Module Logging enabled](images/ps-module-logging-policy-enabled.png)

*Figure 14: PowerShell Module Logging policy enabled.*

![Module Logging wildcard configuration](images/ps-module-logging-enabled-wildcard.png)

*Figure 15: PowerShell Module Logging configured with wildcard (`*`) to capture all module activity.*

![Group Policy update applied](images/cmd-gpupdate-force-executed.png)

*Figure 16: Group Policy update executed to apply PowerShell logging settings.*

![PowerShell test command execution](images/ps-test-command-executed.png)

*Figure 17: Manual PowerShell command execution used to generate logging events.*

![PowerShell Script Block event details](images/eventviewer-powershell-scriptblock-event-details.png)

*Figure 18: PowerShell Operational log showing Script Block event details with captured command content.*

## Sysmon Telemetry (Enhanced Endpoint Logging)

To extend endpoint telemetry beyond default Windows logging, Sysmon (System Monitor) was installed on the Windows VM. Sysmon provides additional high-value security events (e.g., process creation with richer metadata) that support incident investigation and timeline reconstruction.

A community-maintained Sysmon configuration (sysmon-modular by Olaf Hartong) was used as a baseline to enable useful detections while keeping noise manageable. After installation, Sysmon service status was verified and telemetry generation was validated by performing a controlled user action (opening Notepad) and confirming the corresponding Sysmon event in Event Viewer.

![Sysmon download page (Microsoft Sysinternals)](images/sysmon-download-page.png)

*Figure 19: Official Sysmon documentation/download source used for acquisition.*

![Extracted Sysmon binaries](images/sysmon-binaries-extracted.png)

*Figure 20: Sysmon package extracted to a dedicated directory on the endpoint.*

![sysmon-modular configuration repository](images/sysmon-modular-github-repository.png)

*Figure 21: sysmon-modular repository used as the baseline Sysmon configuration source.*

![Sysmon configuration copied to Sysmon directory](images/sysmon-config-copied-to-sysmon-dir.png)

*Figure 22: Sysmon configuration file placed in the Sysmon installation directory.*

![Sysmon installation command executed](images/sysmon-install-command-executed.png)

*Figure 23: Sysmon installed with configuration applied from an elevated command prompt.*

![Sysmon service running](images/sysmon-service-running.png)

*Figure 24: Sysmon64 service verified as running after installation.*

![Telemetry validation: Notepad opened](images/sysmon-test-notepad-opened.png)

*Figure 25: Controlled user action (opening Notepad) used to generate a Sysmon Process Create event.*

![Sysmon Process Create event for Notepad](images/eventviewer-sysmon-processcreate-notepad.png)

*Figure 26: Event Viewer showing Sysmon Process Create (Event ID 1) confirming telemetry collection.*

## Security Monitoring Platform (Wazuh SIEM / EDR)

To centralize endpoint telemetry and support alert-driven incident response workflows, a dedicated security monitoring platform was deployed using **Wazuh**.

Wazuh was selected to provide:
- Centralized log ingestion and correlation
- Endpoint security monitoring (EDR-like visibility)
- Alerting and severity classification
- MITRE ATT&CK mapping to support structured analysis
- A realistic SOC-style investigation interface

The platform was deployed on a separate Linux system to simulate a typical enterprise separation between monitored endpoints and security monitoring infrastructure.

---

## Wazuh Server Deployment

### Operating System

A dedicated **Ubuntu Server 24.04 LTS** virtual machine was deployed to host the Wazuh components.

- Ubuntu Server 24.04 (LTS)
- Minimal installation
- Dedicated VM acting as a security monitoring node
- Network connectivity to the monitored Windows endpoint

The system was intentionally kept minimal to reduce noise and maintain focus on security monitoring functionality rather than general-purpose server services.

---

### Wazuh Installation

Wazuh version **4.14.2** was installed using the official Wazuh installation assistant, which deploys and configures all required components in a single-node architecture.

Installed components included:
- **Wazuh Manager** – log analysis, rules, decoders, and alert generation
- **Wazuh Indexer** – event indexing and search backend
- **Wazuh Dashboard** – web-based SOC interface for investigation and analysis
- **Filebeat** – log shipping between components

The installation process automatically generated and configured TLS certificates to secure communication between Wazuh components.

![Wazuh installation process output](images/wazuh-installation-output.png)

*Figure 27: Wazuh installation assistant executing and deploying core components.*

Upon completion, all Wazuh services were verified to be running successfully.

![Wazuh dashboard service status](images/wazuh-dashboard-service-status.png)

*Figure 28: Wazuh Dashboard service verified as active and running.*

---

### Network Exposure and Dashboard Access

The Wazuh Dashboard listens on HTTPS port **443** on the Ubuntu server.  
To allow access from the analyst workstation, port forwarding was configured on the virtualization platform.

- Host port: 8443  
- Guest port: 443  
- Protocol: TCP  

This configuration allowed secure access to the Wazuh Dashboard from the analyst system without exposing the VM directly to the external network.

![Port forwarding configuration](images/wazuh-port-forwarding.png)

*Figure 29: NAT port forwarding configured to expose the Wazuh Dashboard.*

---

### Wazuh Dashboard Validation

After installation and network configuration, access to the Wazuh Dashboard was successfully established via a web browser.

![Wazuh login page](images/wazuh-login-page.png)

*Figure 30: Wazuh Dashboard login page accessed via forwarded HTTPS port.*

Following authentication, the main dashboard interface loaded successfully, confirming that all core Wazuh components were operational.

![Wazuh dashboard overview](images/wazuh-dashboard-overview.png)

*Figure 31: Wazuh Dashboard overview showing platform readiness prior to agent enrollment.*

At this stage:
- No agents were registered
- No endpoint telemetry had been ingested
- The platform was in a clean, pre-incident state

This clean SIEM baseline was intentionally preserved to ensure that all subsequent alerts and findings could be clearly attributed to the simulated incident activity.

---

## Agent Enrollment Preparation

With the Wazuh platform operational, the environment was prepared for endpoint agent enrollment.

The next phase of the lab focuses on:
- Deploying the Wazuh agent on the Windows endpoint
- Verifying ingestion of Windows Event Logs and Sysmon telemetry
- Confirming alert generation and MITRE ATT&CK mapping
- Establishing an alert-driven starting point for the incident investigation

At this point, the lab transitions from **telemetry preparation** to **active security monitoring**, enabling realistic SOC-style detection and response workflows.






