PROTECTED_VMS_QUERY = """
query {
  vSphereVmNewConnection {
    nodes {
      name
      effectiveSlaDomain {
        name
      }
    }
  }
}
"""

LATEST_RECOVERY_POINT_QUERY = """
query {
  vSphereVmNewConnection {
    nodes {
      name
      effectiveSlaDomain {
        name
      }
      newestSnapshot {
        id
        date
      }
    }
  }
}
"""

REPLICATION_FAILURES_QUERY = """
query {
  activitySeriesConnection(
    filters: {
      lastActivityType: [REPLICATION]
      lastActivityStatus: [FAILURE]
    }
  ) {
    count
    nodes {
      objectName
      objectType
      lastActivityType
      lastActivityStatus
      lastUpdated
      severity
      lastActivityMessage
    }
  }
}
"""

PROTECTION_FAILURES_QUERY = """
query {
  activitySeriesConnection(
    filters: {
      lastActivityStatus: [FAILURE]
    }
  ) {
    count
    nodes {
      objectName
      objectType
      lastActivityType
      lastActivityStatus
      lastUpdated
      severity
      lastActivityMessage
    }
  }
}
"""

SLA_VIOLATIONS_QUERY = """
query {
  snappableConnection(
    filter: {
      complianceStatus: OutOfCompliance
    }
  ) {
    count
    nodes {
      name
      objectType
      slaDomain {
        name
      }
      missedSnapshots
    }
  }
}
"""