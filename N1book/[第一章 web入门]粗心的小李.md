2022.11.29

开启靶机，一个干净index.html，上面告诉我们存在git泄露，尝试访问/.git文件夹，结果不行，但是可以访问里面的文件。

但是书上并没有提到太多的方法，只是简单的提到了使用工具。

我想尝试手动而不使用工具，于是围绕git泄露去搜索资料，还真找到了：https://www.freebuf.com/articles/web/267597.html

根据我对这篇文章的个人理解，简单来讲就是想办法找相关的hash值，通过路径: /.git/objects/hash值前两位/完整的hash值减前两位

来获取对应commit记录的内容。

应用到这道题上，首先我对git文件夹并不熟悉，所以我在本地上git init了一下，方便本地操作，在靶机上访问/.git/HEAD，里面给出了一个路径refs/heads/master，里面有一串hash值： 

    213b7e386e9b0b406d91fae58bf8be11a58c3f88

构造路径：

    /.git/objects/21/3b7e386e9b0b406d91fae58bf8be11a58c3f88

文件下载打开一看，虽然一堆乱码，但是很明显并没有我们想要的。

我在本地的git几乎把所有可能存在hash值的文件翻了个遍，最终将目光锁定在了/.git/index文件。

我先把靶机上的index文件下载，然后覆盖我本地的/.git/index，然后在通过git ls-files --stage命令查看，结果如下：

    sugob@WIN-C93D9KOFCJ5 MINGW64 ~/Downloads (master)
    $ git ls-files --stage
    100644 1e0db5d96b5cc9785055c14bbec0e7ad14f48151 0       index.html

发现中间有一串1e0db5d96b5cc9785055c14bbec0e7ad14f48151，根据刚刚的方法构造路径，下载到了文件，直接打开就能看到一大堆内容虽然是乱码，脚本将其解码一下,一大堆内容中发现耀眼的flag:

    n1book{git_looks_s0_easyfun}
