import mstarpy

fund = mstarpy.Funds(term="F00000PZH2", country="in")
print(fund.name)
df_equity_holdings = fund.holdings(holdingType="equity")
print(df_equity_holdings[["securityName", "weighting", "susEsgRiskScore"]].head())

