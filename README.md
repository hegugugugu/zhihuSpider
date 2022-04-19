## 实现功能：

1. 爬取知乎问题“什么时候你真的很心疼一只猫？(https://www.zhihu.com/question/267209533)”下的1398个回答（截至2022年4月18日）
2. 存储到Excel中，包括：用户id、创建时间、用户昵称、点赞数、评论数和内容，方便后续对回答进行文本分析（分词、词频统计、抽取关键词等等）

## 结果截图：

![image-20220419224010272](C:\Users\maotu\AppData\Roaming\Typora\typora-user-images\image-20220419224010272.png)

## 爬虫思路：

### 直接爬取失败：

<img src="C:\Users\maotu\AppData\Roaming\Typora\typora-user-images\image-20220419171117703.png" alt="image-20220419171117703" style="zoom:33%;" />

使用抓包分析，搜索回答重的关键字，这个answers？include=...就是返回给我们的数据。可以在previewer中看到data的格式是json

<img src="C:\Users\maotu\AppData\Roaming\Typora\typora-user-images\image-20220419173138278.png" alt="image-20220419173138278" style="zoom: 50%;" />

知乎的回答不是按照页面显示的，下滑会有新的回答被加载出来，是AJAX技术，在每个新增加的answer的url中，改变的只有offset和limit，offset可以看作是页数，limit默认为5

<img src="C:\Users\maotu\AppData\Roaming\Typora\typora-user-images\image-20220419173808368.png" alt="image-20220419173808368" style="zoom: 33%;" />

直接进行爬取会返回错误，知乎反爬，返回1003

<img src="C:\Users\maotu\AppData\Roaming\Typora\typora-user-images\image-20220419171305103.png" alt="image-20220419171305103" style="zoom:50%;" />

<img src="C:\Users\maotu\AppData\Roaming\Typora\typora-user-images\image-20220419171338073.png" alt="image-20220419171338073" style="zoom:50%;" />

### js逆向分析：

知乎2020年之后就不能不登陆就直接爬取了，需要通过一些方法绕过知乎的反爬机制。

#### 方法一（已失效）：使用selenuim托管

使用selenium自动化测试爬取知乎的时候出现了：错误代码10001：请求异常请升级客户端后重新尝试，这个错误的产生是由于知乎可以检测selenium自动化测试的脚本，因此可以阻止selenium的继续访问。这也算是比较高级的反爬取措施。

解决方案见：https://www.cnblogs.com/future-dream/p/11109124.html

此方法2022年4月已失效

#### 方法二（需要配置Node.js，确保module里有jsdom）：js逆向分析

通过postman测试，请求头中只需要带上user-agent、cookie、x-zse-93、x-zse-96

仔细对比不同answer的Request Header，发现唯一改变的只有x-zse-96是变化的，所以只要能够自动生成x-zse-96就可以补全请求头进行爬虫了。

<img src="C:\Users\maotu\AppData\Roaming\Typora\typora-user-images\image-20220419180419831.png" alt="image-20220419180419831" style="zoom: 50%;" /><img src="C:\Users\maotu\AppData\Roaming\Typora\typora-user-images\image-20220419180513813.png" alt="image-20220419180513813" style="zoom:50%;" />

全局搜索关键字x-zse-96，把涉及到的变量都打上断点，可以看到x-zse-96是2.0_和y拼接而成的。y变量是等于O.signature的。

<img src="C:\Users\maotu\AppData\Roaming\Typora\typora-user-images\image-20220419205203210.png" alt="image-20220419205203210" style="zoom:50%;" />

上溯发现signature的生成函数，signture调用了u()()方法传入了f()(s)，f方法中传入了s值，在这里也打上断点，调试后发现s是明文数据，在终端进行测试，s = '101_3_2.0+/api/v4/answers/378731849/concerned_upvoters?limit=5&offset=0+"AIDRS7aZ0BSPTiY2Dq2wQvGM2EYysNwEw-c=|1650376322"'

生成方式是： s = [r, a, i, H(c) && c, o].filter(Boolean).join("+");

其中，r=101_3_2.0是固定版本号

a=/api/v4/answers/378731849/concerned_upvoters?limit=5&offset=0是根据问题和params来的

i=AIDRS7aZ0BSPTiY2Dq2wQvGM2EYysNwEw-c=|1650376322是cookie的d_c0值

猜测f()(s),是进行MD5加密的操作，验证确实是这样。

<img src="C:\Users\maotu\AppData\Roaming\Typora\typora-user-images\image-20220419221953921.png" alt="image-20220419221953921" style="zoom:50%;" />

对于u()，调用__g._encrypt(encodeURIComponent(e)),这是一个加密算法，把它上面一部分js代码粘出来，补充上jsdom的环境，完整代码见g_encrypt.js

<img src="C:\Users\maotu\AppData\Roaming\Typora\typora-user-images\image-20220419222518508.png" alt="image-20220419222518508" style="zoom:50%;" />

<img src="C:\Users\maotu\AppData\Roaming\Typora\typora-user-images\image-20220419223708035.png" alt="image-20220419223708035" style="zoom:50%;" />

##### 关于jsdom的安装：

```
npm i jsdom -g
```

Node.js版本是14.15.4