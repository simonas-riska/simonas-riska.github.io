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

Screenshots are included below as supporting evidence of the endpoint deployment and baseline state.

At this stage, the endpoint contained:
- No third-party security tools
- No additional user activity
- Default Windows configuration only

This baseline was preserved to ensure all observed activity during the incident could be attributed to the simulated scenario.

## User Accounts

### Standard Local User Account

A standard local user account was created to simulate a typical corporate end-user context for the incident scenario.

- Username: employee1
- Account type: Standard user
- Local group membership: Users

The account was intentionally not granted administrative privileges to reflect a common enterprise workstation configuration and to support realistic privilege boundaries and execution context during investigation.

### Local Administrator Account

A separate local administrator account was created to represent privileged access on the endpoint.

- Username: admin1
- Account type: Local administrator
- Local group membership: Administrators

This account was created to support realistic privilege separation during investigation, including analysis of execution context, potential privilege escalation attempts, and differentiation between standard and administrative activity.

## Windows Event Logging

Default Windows Event Logging was confirmed to be enabled on the endpoint, including the following log channels:

- Security
- System
- Application

These logs provide core visibility into authentication events, system changes, service activity, and application-level errors, and form the baseline telemetry for subsequent investigation and correlation with enhanced logging sources.

## Process Command-Line Logging

Process command-line logging was enabled to enhance visibility into process execution details during investigation.

The following configuration was applied:
- Audit Process Creation enabled (Success)
- Command-line arguments included in process creation events

This configuration ensures that Security Event ID 4688 includes full command-line arguments, allowing reconstruction of execution intent during incident analysis.

## Appendix: Endpoint Deployment Evidence

<details>
<summary>Windows 11 Enterprise deployment screenshots</summary>

![Windows 11 Enterprise VM created from official ISO](images/win11-vm-iso.png)

*Figure 1: Windows 11 Enterprise ISO selected during virtual machine creation.*

![Clean Windows 11 desktop after installation](images/win11-desktop.png)

*Figure 2: Clean Windows 11 Enterprise endpoint baseline prior to telemetry and agent installation.*

</details>

<details>
<summary>Standard user account creation screenshots</summary>

![Standard user account creation](images/user-account-create.png)

*Figure 3: Creation of a standard local user account for the lab endpoint.*

![User group membership](images/user-account-groups.png)

*Figure 4: Verification that the user is a member of the local Users group only.*

</details>

<details>
<summary>Local administrator account creation screenshots</summary>

![Administrator account creation](images/admin-account-create.png)

*Figure 5: Creation of a dedicated local administrator account for the lab endpoint.*

![Administrator group assignment](images/admin-account-groups.png)

*Figure 6: Verification that the account is a member of the local Administrators group.*
</details>

<details>
<summary>Process command-line logging configuration and verification</summary>

![Command-line logging policy enabled](images/gpo-command-line-enabled.png)

*Figure 7: Command-line inclusion enabled for process creation audit events.*

![Event 4688 with command-line captured](images/event4688-commandline.png)

*Figure 8: Security Event ID 4688 showing command-line arguments and user context.*

<details>
<summary>Extended configuration steps (learning reference)</summary>

![Audit Process Creation policy](images/audit-process-creation.png)

*Local Security Policy showing Audit Process Creation enabled.*

![Group Policy update](images/gpupdate-force.png)

*Policy refresh to apply updated audit settings.*

![whoami execution](images/whoami-execution.png)

*Manual execution used to generate a test process creation event.*

</details>

</details>



