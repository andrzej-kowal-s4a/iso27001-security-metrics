# iso27001-security-metrics

# JIRA reference
https://smart4aviation.atlassian.net/browse/SECURITY-280


# Metrics which are tracked:
Each of the metrics is tracked in a separate JIRA filter and are send to mailbox each week on Thursday.


## SECURITY-280-Incidents-Major-plus
project = security and issuetype = "Security Incident" and priority >= Major and status != Closed
https://smart4aviation.atlassian.net/issues/?filter=32878

## SECURITY-280-Incidents
project = security and issuetype = "Security Incident" and status != Closed
https://smart4aviation.atlassian.net/issues/?filter=32879

## SECURITY-280-Security-Issues
project not in (SERVICE) AND ( labels in ("security", "incident", "breach") OR summary ~ "breach" OR summary ~ "incident" OR description ~ "breach" OR description ~ "incident" OR description ~ "breach" ) and status != CLOSED ORDER BY priority DESC
https://smart4aviation.atlassian.net/issues/?filter=32880
