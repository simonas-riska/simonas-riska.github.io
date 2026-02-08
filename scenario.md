---
title: Incident Scenario
---

# Incident Scenario

## Scenario Summary
**Initial access via a malicious document launching encoded PowerShell, followed by host reconnaissance and persistence via scheduled task to maintain access.**

## Scope
- Single Windows 10/11 endpoint
- Single user context
- No lateral movement assumed

## Rationale
This scenario was selected because it reflects a high-frequency enterprise incident pattern:
- Living-off-the-land PowerShell usage
- Minimal tooling and native persistence
- Strong Windows telemetry visibility

The focus is on analyst investigation and decision-making rather than exploitation.
