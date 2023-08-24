# TMBot

基于 [telethon](https://github.com/LonamiWebs/Telethon) 的 userbot 程序，代码百分百由 ChatGPT 完成。

部署：
```
docker run -it \
    --restart always \
    --name TMBot \
    --net host \
    -v /path/to/TMBdata:/TMBdata \
    -e api_id=1234567 \
    -e api_hash=1a2b3c...8x9y0z \
    noreph/tmbot
```
插件目录：`TMBdata/plugins`。  
配置文件目录：`TMBdata/config`。  
账号登录数据：`TMBdata/session`。  
api_id、api_hash 请前往 my.telegram.org 申请。  

⚠️⚠️⚠️ 温馨提示：谨慎使用，不对使用后出现任何结果负责，包括但不限于封号、被群组管理员禁言、踢出等等。
