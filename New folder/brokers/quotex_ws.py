"""
QUANTUM X PRO - Quotex Adapter (XCharts API)
Updated to use xcharts.live API - No Cloudflare blocking!
"""
from brokers.quotex_xcharts import QuotexXChartsAdapter

# Export the working adapter
QuotexWSAdapter = QuotexXChartsAdapter

__all__ = ['QuotexWSAdapter']
