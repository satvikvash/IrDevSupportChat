import resend
import time

resend.api_key = "re_J9fpAhYG_KRufi7HBZYadLpfhPgnBSbQ1"

FROM_EMAIL = "onboarding@resend.dev"
TO_EMAIL = "irdevsupport@4zpjqq.onmicrosoft.com"

threads = [
    {
        "subject": "Client Alerting Notifications Not Delivered",
        "body": """\
Hi team,

We're not receiving real-time alert emails for stock movement triggers set in the Notification module.

Details:
- Client: EquityGroup Inc.
- Module: Notifications
- Affected alert types: Stock movement, earnings updates
- Last received email: June 5, 10:15 AM EST

This is causing missed event notifications. Please advise.

Emily Hughes  
VP, Investor Coverage"""
    },
    {
        "subject": "RE: Client Alerting Notifications Not Delivered",
        "body": """\
Emily,

Issue resolved:

- Root cause: Misconfigured Akamai edge cache blocking webhook-to-email bridge
- Fix: Updated cache rules and whitelisted IP for our email trigger API
- Verified: Delivery resumed to all alert subscribers
- Action: Enabled webhook logs in Notification module

Thanks,  
DevOps Team"""
    },
    {
        "subject": "Earnings Upload Failing for CSV Imports",
        "body": """\
Hi Support,

Attempting to upload earnings data in bulk using the CSV import feature, but getting 500 Internal Server Error.

- Client: Sunrise Capital
- Module: Estimates Import
- File: earnings_q2_2025.csv
- Tried browsers: Chrome, Firefox
- Happens on step: "Map Fields"

Please help resolve ASAP.

Manoj Verma  
Director, Financial Data Ops"""
    },
    {
        "subject": "RE: Earnings Upload Failing for CSV Imports",
        "body": """\
Manoj,

Resolved:

- Bug in field mapping step due to recent CSV parser update
- Issue affected all files missing optional “Notes” column
- Patched upload backend to handle null field scenarios
- Your file has now been successfully imported

Regards,  
Support Team"""
    },
    {
        "subject": "Transcript Sync Delayed Across Global Feeds",
        "body": """\
Team,

We’re seeing delays in transcripts showing up for non-US companies.

- Client: EastBridge Holdings (APAC focus)
- Module: Transcripts
- Delay: 6–8 hours from event time
- Affected: TSMC, Reliance, Softbank
- Expected: 30-minute lag

Please investigate ingestion delay.

Tomoya Ito  
Senior Analyst"""
    },
    {
        "subject": "RE: Transcript Sync Delayed Across Global Feeds",
        "body": """\
Tomoya,

Thanks for reporting.

- Root Cause: Cron job failure in ir-transcripts-apac-parser
- Scheduled ingestion skipped 2 cycles on June 9
- Fix: Restarted ETL scheduler, patched memory leak
- Added: Auto-restart and alerting on ingestion skips

Backlog cleared. Transcripts flowing as expected.

Best,  
IR Data Pipeline Team"""
    },
    {
        "subject": "Research Summary Widget Crashing Dashboard",
        "body": """\
Hello Support,

Our internal IR dashboard fails to load when the Research Summary widget is added.

- Client: BlueHorizon Investments
- Module: Custom Dashboard Builder
- Widget: Research Summary
- Error: "Module not defined – ir-research-widget.js"

Other widgets load fine.

Sandra Dell  
Business Analyst"""
    },
    {
        "subject": "RE: Research Summary Widget Crashing Dashboard",
        "body": """\
Sandra,

Thanks for flagging this.

- Missing JS bundle reference due to CDN update
- Research Summary widget not deployed on latest CDN manifest
- Deployed fix, validated widget rendering in staging and prod

Dashboard should now work smoothly.

Infra Team"""
    },
    {
        "subject": "Security Audit - Role-Based Access Not Honored",
        "body": """\
Hi Support,

During a routine audit, we found some users had access to restricted estimate reports.

- Client: Integrity Capital
- Module: RBAC & Permissions
- Observed: Junior analysts accessing sensitive earnings projections
- Access via: URL deep-link, not visible via UI

This could be a compliance issue.

Ananya Das  
Compliance Lead"""
    },
    {
        "subject": "RE: Security Audit - Role-Based Access Not Honored",
        "body": """\
Ananya,

Urgent issue addressed.

- Flaw: Missing RBAC middleware on direct report URL handler
- Patch: Applied permission check for all report endpoints
- Audit log created for all sensitive access events

Please rerun your audit to confirm resolution.

Security Engineering"""
    },
    {
        "subject": "SSO Auto-Provisioning Not Working for New Users",
        "body": """\
Support,

New hires are not being auto-provisioned in IRHelper despite successful Okta login.

- Client: Nova Investors
- SSO: Okta
- Users affected: 5 (onboarding batch)
- Error: “User not found” after login

Manual creation works fine.

Jeff Cole  
IT Admin"""
    },
    {
        "subject": "RE: SSO Auto-Provisioning Not Working for New Users",
        "body": """\
Jeff,

Provisioning issue resolved.

- Problem: SCIM sync was disabled post API key rotation
- Fix: Re-enabled SCIM sync with Okta directory
- Added sync webhook retry logic

New users should now auto-provision upon SSO login.

Support Team"""
    },
    {
        "subject": "Estimates Dashboard Totals Not Matching Detail View",
        "body": """\
Support Team,

The totals on the overview page of the Estimates dashboard are not matching the drilled-down company views.

- Client: Apex Equity Partners
- Module: Estimates
- Total: $11.2B
- Sum of details: $10.7B

Please validate if caching is out-of-sync.

Boris Ivanov  
Investment Analyst"""
    },
    {
        "subject": "RE: Estimates Dashboard Totals Not Matching Detail View",
        "body": """\
Boris,

Confirmed cache mismatch.

- Root Cause: Akamai cache not invalidated on Q2 override update
- Fix: Purged regional caches manually
- Implemented: Auto-invalidation hook on override API

Totals now match detailed values. Thanks for flagging!

IRHelper Caching Ops"""
    }
]

# Send all emails in sequence
for thread in threads:
    response = resend.Emails.send({
        "from": FROM_EMAIL,
        "to": TO_EMAIL,
        "subject": thread["subject"],
        "text": thread["body"]
    })
    print(f"Sent: {thread['subject']} → Status: {response.get('status', 'check logs')}")
    time.sleep(1)  # Optional: slight delay to avoid rate limits
