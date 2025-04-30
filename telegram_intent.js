// telegram_intent.js

// 获取请求的URL
var url = $request.url;

// 构造Intent URI
var intentUrl = "intent://" + url.replace(/^https?:\/\//, "") + "#Intent;scheme=https;package=org.telegram.messenger;end";

// 返回重定向响应
$done({
  status: "HTTP/1.1 302 Found",
  headers: {
    "Location": intentUrl
  },
  body: ""
});