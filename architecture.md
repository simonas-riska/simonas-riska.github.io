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

## Appendix: Endpoint Deployment Evidence

<details>
<summary>Windows 11 Enterprise deployment screenshots</summary>

![Windows 11 Enterprise VM created from official ISO](images/win11-vm-iso.png)

*Figure: Windows 11 Enterprise ISO selected during virtual machine creation.*

![Clean Windows 11 desktop after installation](images/win11-desktop.png)

*Figure: Clean Windows 11 Enterprise endpoint baseline prior to telemetry and agent installation.*

</details>

## Baseline State

At this stage, the endpoint contained:
- No third-party security tools
- No additional user activity
- Default Windows configuration only

This baseline was preserved to ensure all observed activity during the incident could be attributed to the simulated scenario.
