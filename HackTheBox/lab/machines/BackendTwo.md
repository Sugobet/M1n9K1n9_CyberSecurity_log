# BackendTwo

BackendTwo在脆弱的web api上通过任意文件读取、热重载的uvicorn从而访问目标，之后再通过猜单词小游戏获得root

---

## 外部信息收集

### 端口扫描

循例nmap

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/8400cae6-41b9-4f78-df3a-1a5412b74e15.png)

### Web枚举

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/99773991-404e-fc3c-ec1a-f4be1bbbbaa0.png)

feroxbuster扫目录

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/64575a8e-d993-87f0-eeda-c0be0ef53d92.png)

/api/v1列举了两个节点

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/c733bfd3-8b7f-ac03-b800-61cf95a5c7da.png)

/api/v1/user/1

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/20788e61-3e33-4093-18a1-31f55c0d6cb4.png)

扫user可以继续发现login和singup

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/2e9d4cce-fde0-4a0f-8f01-3298c650024e.png)

注册个账户

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/c56b945e-7078-defc-824f-87304dd0da11.png)

登录

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/e0dcb621-ad72-9b9f-ea3e-1fe7bcaf1fd0.png)

burp添加请求头

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/093d0038-f081-75d9-3732-23a7a4ee6a5f.png)

访问/docs

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/9e489cec-f4f1-e0ff-bd44-8238d1062c00.png)

edit中可以添加字段以修改它，修改is_superuser

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/53bb3273-b26e-398f-2cf2-efb24fb18258.png)

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/658844ad-1cf8-3f73-04d3-6b5414350589.png)

改完后需要重新登录一下

## Foothold

读/proc/self/status

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/bafa2b22-46cf-166d-a523-4729e593efa9.png)

再读父进程的cmdline

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/1fb8f6e9-7b6d-6058-9b96-d73492991ce2.png)

/proc/self/environ

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/a2fd3774-4059-bb2d-c9dd-7cb81576cddb.png)

从环境变量可以得知运行在/home/htb目录，并且是app/main.py

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/0f1f5dfb-5df9-0dce-46ae-cd0248e88771.png)

由于uvicorn设置了--reload热重载，所以可以直接写shellcode

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/bcc8160f-e50f-27b7-2cda-90c7130038f6.png)

但是这里需要jwt设置了debug

从main跟到core/config.py, jwt secret是api key

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/3cc4984a-4f49-7c2e-6579-ba2ad1b55048.png)

将jwt解码，然后添加debug字段，使用api key作为secret创建新的jwt

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/84dd70e0-e328-4c5d-16c6-fb7335e722c2.png)

在main.py写shellcode

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/594876f6-9579-11f6-e92c-4489a2bc7788.png)

然鹅这个shell很快将会断开，main会被重置，但我们可以通过这个短暂的shell写ssh key

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/cef41ef7-f496-ba2e-071f-f1b98f4114a5.png)

登录ssh

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/b5cf1f2f-7760-c9f8-ec5e-243cdf339f3c.png)

## 本地权限提升

auth.log有个密码，它是htb的

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/fd9e463c-2e0f-b849-c416-b0453c9860ad.png)

sudo -l

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/26561421-3a7e-4979-c700-2b034fd5bc7e.png)

/opt有个字典

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/ec09d7c4-05c6-ee45-5f98-baebcf36a7c2.png)

当我输入shell的时候前两位是正确的

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/0df81295-d6bd-46a3-9e72-5f7d6610729f.png)

从字典中过滤

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/c64a4c35-3d73-c28e-1c30-1ec36477448f.png)

我发现它是随机并非硬编码的，每次sudo -l都会是不同的正确word

当我们输入正确的word后我们将能得到它

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/cab2e7f5-dcf2-5d59-386d-4a002e3a311a.png)

