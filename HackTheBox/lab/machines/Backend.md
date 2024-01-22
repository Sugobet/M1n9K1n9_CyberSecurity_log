# Backend


---

## 外部信息搜集

### 端口扫描

循例nmap

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/7b77dd68-6b77-9862-2ea9-3daf366d12db.png)

### Web枚举

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/e2a7a72c-86cc-ccf3-b791-cfea37fbc80a.png)

feroxbuster

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/9077dfda-88fe-3ad4-02b7-609c85102cf5.png)

这个结构与这个靶机第二个版本基本一致

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/2715ccb1-2619-f598-978a-455faf21d254.png)

/user

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/30902d0a-1d72-cbf3-602d-3fd0689e22d5.png)

创建个账号

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/28812525-55ca-e3bb-d032-21feef42b460.png)

登录

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/e9db4a3d-2947-ae7e-6373-deb926d7a6f7.png)

burp添加请求头

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/b806cf04-7172-fdd0-98a8-227bc545b398.png)

/docs

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/79b1631e-04b4-aea6-9dba-2a25e80b9c65.png)

看到有个可以修改密码的api，先查询admin的guid

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/11f4cdfe-467c-a29c-0140-9e9a3f91b134.png)

尝试修改admin的密码

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/8a1e694b-cc16-96a7-1304-6def140de386.png)

登录admin

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/8894df6a-1971-4083-a6ce-2893f674c5f5.png)

## Foothold

exec需要debug，现在我们只能任意文件读取

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/766f0513-583e-0fb3-97e0-575d05696512.png)

读/proc/self/status

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/396f66aa-5258-2373-5f80-ba16421a0deb.png)

读父进程cmdline

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/094c1da9-24f6-2435-b3b3-a43257fb9b6b.png)

可以得知/home/htb/uhc/app/main.py

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/5c2a0ea9-6cd6-4bac-8095-7b278fd6f977.png)

从main.py跟到app/core/config.py，拿到jwt的secret

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/131d285b-83f7-97fa-a387-07769fd8b3c9.png)

解码jwt后添加debug字段，再用secret转jwt

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/fb4131ff-3839-0274-449f-a5381c1a65bf.png)

burp更换header后再次exec

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/e212862b-d9c2-0820-ed9c-0f9904161180.png)

常规python reverse shell base64

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/bd564ba5-4f09-9972-d8ad-8795e94b9223.png)

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/a2543b06-3dfa-7178-121f-6f42f9fe2b9a.png)

## 本地权限提升

auth.log

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/8ad259de-d637-0400-1f5b-925c5f4c7af5.png)

发现一个密码

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/a09829d3-7aac-2a1e-38cd-2d7fec04f892.png)

它不是htb的密码，直接就是root的

![file](https://blog.apt250.zip/wp-content/uploads/2024/01/2857fa27-5311-90b3-82aa-5a12d3c05c97.png)
