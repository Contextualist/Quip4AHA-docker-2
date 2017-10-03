## Automatic Quip Job Script for AHA Broadcast
The scripts call [Quip](https://quip.com) API though [its official Python library](https://github.com/quip/quip-api) to perform certain automatic tasks on the broadcast doc.

### Include:
| Script | URL | Cron(UTC+08:00) | Description |
| ------ | --- | --------------- | ----------- |
| [AssignHost.py](\AssignHost.py) | /a | | Divide the doc into parts and assign them to the host evenly. |
| [NewDoc.py](\NewDoc.py) | /newdoc | every Friday 16:10 | Create the doc for the broadcast next week. |
| [UpdateWeather.py](\UpdateWeather.py) | /updateweather | every Sunday 07:27;<br/>every Wednesday 07:27 | Update "weather for today" in the doc. |

### Run with Docker
```
docker run -d \
-p 80:80 \
-e "token={Quip_API_token}" \
-v /path/to/configs:/etc/q4a \
contextualist/quip4aha
```

### History
* 2016.04 The [original project](https://github.com/Contextualist/Quip4AHA) was deployed on [GAE](https://cloud.google.com)
* 2016.07 A strange bug of GAE disabled my updates. Transplanted the project to [DaoCloud](https://daocloud.io). Host on quip4aha.daoapp.io. 
* 2017.09 Tired of DaoCloud's restrain, hosted on AHA's VPS.
