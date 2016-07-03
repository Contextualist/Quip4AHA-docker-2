## Automatic Quip Job Script for AHA Broadcast
The scripts call [Quip](https://quip.com) API though [its official Python library](https://github.com/quip/quip-api) to perform certain automatic tasks on the broadcast doc.

The [original project](https://github.com/Contextualist/Quip4AHA) was deployed on [GAE](https://cloud.google.com), who broke my heart with a strange bug that disabled my updates. Anyway, I transplanted the project to [DaoCloud](https://daocloud.io). Host on quip4aha.daoapp.io . 

### Include:
| Script | Call | Cron(UTC+08:00) | Description |
| ------ | ---- | --------------- | ----------- |
| [AssignHost.py](\AssignHost.py) | /a?host=<'+'.join(hosts)> | | Divide the doc into parts and assign them to the host evenly. |
| [NewDoc.py](\NewDoc.py) | /newdoc | every Friday 16:10 | Create the doc for the broadcast next week. |
| [UpdateWeather.py](\UpdateWeather.py) | /updateweather | every Sunday 07:27;<br/>every Wednesday 07:27 | Update "weather for today" in the doc. |
