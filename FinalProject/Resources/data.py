import akshare as ak

futures_zh_daily_sina_df = ak.futures_zh_daily_sina(symbol="HC0")
print(futures_zh_daily_sina_df)
futures_zh_daily_sina_df.to_csv("hc.csv", index=False)