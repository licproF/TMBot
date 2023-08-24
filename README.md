# TMBot

*代码几乎由 ChatGPT 完成。*

```
docker run -it --restart always --name=TMBot \
-e TZ=Asia/Shanghai \
-e API_ID=<telegram api_id> \
-e API_HASH=<telegram api_hash> \
-e prefix="#" \
-e proxy=http://your_http_proxy:port \
--network=host \
-v /:/hostfs:ro \
-v <path>:/TMBot/data \
noreph/tmbot
```

- `api_id`、`api_hash`：申请地址 https://my.telegram.org ，参考 https://core.telegram.org/api/obtaining_api_id 。
- `prefix`：命令前缀，可选。
- `proxy`：代理，可选 http、https 和 socks5，可选。
- `--network=host`：获取宿主机网卡流量统计，可选。
- `-v /:/hostfs:ro`：获取硬盘分区信息，因可读取宿主机所有信息，慎用。
- `path` 自定义路径，映射插件、登录信息目录。
- 以上命令记得去掉 `<>`。

默认三个命令 `restart`、`ping`、`sysinfo`
