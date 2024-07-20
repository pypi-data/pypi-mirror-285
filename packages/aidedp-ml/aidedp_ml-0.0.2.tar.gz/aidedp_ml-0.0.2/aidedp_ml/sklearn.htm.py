<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
        <title>机器学习sklearn 模型导出 sklearn导入数据_mob64ca13fc5fb6的技术博客_51CTO博客</title>
    <meta name="keywords" content="机器学习sklearn 模型导出 sklearn导入数据,机器学习博客,51CTO博客">
<meta name="description" content="机器学习sklearn 模型导出 sklearn导入数据，传统的机器学习任务从开始到建模的一般流程是：获取数据-&amp;gt;数据预处理-&amp;gt;训练建模-&amp;gt;模型评估-&amp;gt;预测，分类。本文我们将依据传统机器学习的流程，看看在每一步流程中都有哪些常用的函数以及它们的用法是怎么样的。希望你看完这篇文章可以最为快速的开始你的学习任务。1.获取数据1.1导入sklearn数据集sklearn中包含了大量的优质的数据集，在你学习机器">    <meta name="applicable-device" content="pc">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1" />
    <meta name="msvalidate.01" content="91C5324FE68C0A46FA65F3FEC225EA65" />
    <meta name="referrer" content="no-referrer-when-downgrade">
    
<meta http-equiv="x-dns-prefetch-control" content="on">
<link rel="preconnect" href="https://cdn.51cto.com/">
<link rel="dns-prefetch" href="https://cdn.51cto.com/">
<link rel="preconnect" href="https://static2.51cto.com/edu/">
<link rel="dns-prefetch" href="https://static2.51cto.com/edu/">
<link rel="preconnect" href="https://s2.51cto.com">
<link rel="dns-prefetch" href="https://s2.51cto.com">
<link rel="preload" as="image" href="https://s2.51cto.com/images/100/base/empty.png?x-oss-process=image/format,webp/ignore-error,1">
    <link rel="canonical" href="https://blog.51cto.com/u_16213600/10820896">
    <link type="favicon" rel="shortcut icon" href="/favicon.ico" />
        <script type="application/ld+json">{"@context":"https://ziyuan.baidu.com/contexts/cambrian.jsonld","@id":"https://blog.51cto.com/u_16213600/10820896","appid":"1576672126670053","title":"机器学习sklearn 模型导出 sklearn导入数据_mob64ca13fc5fb6的技术博客_51CTO博客","images":["https://s2.51cto.com/images/blog/202405/15015125_6643a49d0bfbd64134.png","https://s2.51cto.com/images/blog/202405/15015125_6643a49d1ef572503.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_30,g_se,x_10,y_10,shadow_20,type_ZmFuZ3poZW5naGVpdGk=","https://s2.51cto.com/images/blog/202405/15015125_6643a49d335358109.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_30,g_se,x_10,y_10,shadow_20,type_ZmFuZ3poZW5naGVpdGk="],"description":"　　传统的机器学习任务从开始到建模的一般流程是：获取数据 -&gt; 数据预处理 -&gt; 训练建模 -&gt; 模型评估 -&gt; 预测，分类。本文我们将依据传统机器学习的流程，看看在每一步流程中都有哪些常用的函数以及它们的用法是怎么","pubDate":"2024-05-16T10:05:52","upDate":"2024-05-16T10:05:52"}</script>
                                <style data-name="css-inline-enable-style-block" type="text/css">
.blue{color:#3e71f6}.Page{margin:0 auto;width:1200px}.Page.Max{min-width:1000px;width:90%}.Page.M764{width:764px}.white-open{background:#fff;display:none;height:100%;left:0;opacity:0;position:fixed;top:0;width:100%;z-index:10}.blue-btn{background:#3e71f6;border:1px solid #3e71f6}.blue-btn:hover{background:#3477e6;border:1px solid #3477e6}.Header{background:#fff;box-shadow:0 3px 10px hsla(0,0%,40%,.03);display:flex;height:70px;justify-content:center;min-width:1200px;position:relative;z-index:21}.fgline{background:#333;display:inline-block;height:11px;margin:29px 4px 0;transform:rotate(22.5deg);width:1px}.Content{padding-top:20px;z-index:10}.Content,.Footer{position:relative}.Footer{background:#eaeaeb;color:#999;font-size:12px;margin-top:20px;overflow:hidden;padding:40px 0}.Footer dl{font-size:14px;margin-right:40px}.Footer dl dt{color:#333;font-size:16px;margin-bottom:10px}.Footer dl td{height:28px;padding-right:28px}.Footer dl td a{color:#666}.Footer dl td a:hover{color:#3e71f6}.Footer dl img{margin-right:20px}.Footer .copy a{color:#999}.Footer .copy a:hover{color:#333}.pagination{font-size:12px;margin:30px auto;text-align:center}.pagination li{display:inline-block;line-height:1;overflow:hidden}.pagination li.disabled,.pagination li.disabled:hover{color:#333;cursor:default;font-size:14px;padding:0 5px}.pagination li:last-child.last.disabled{color:#999;font-size:12px}.pagination li a,.pagination li.active b{color:#999;display:block;line-height:1;padding:0 5px;text-align:center;width:24px}.pagination li.active b{color:#333}.pagination li a:hover,.pagination li.active a{color:#333;font-size:14px}.pagination li.first a,.pagination li.first_page a,.pagination li.last a,.pagination li.last_page a,.pagination li.next a,.pagination li.prev a{text-align:center;width:50px}.pagination li.next:hover a,.pagination li.prev:hover a{font-size:12px}.pagination li:last-child.last.noLink{background:0;border-color:transparent;margin:0}.noList{margin:100px auto;text-align:center}.noList p{color:#999;font-size:14px;line-height:3}.is-vip-bg,.is-vip-bg-2,.is-vip-bg-3,.is-vip-bg-4,.is-vip-bg-5,.is-vip-bg-6,.is-vip-bg-7{height:100%;position:relative}.is-vip-bg-6 i{right:5px}.vip-icon{bottom:0;cursor:pointer;display:inline-block;position:absolute;right:-5px}.vip-icon-1{background:url("https://s2.51cto.com/images/100/blog/old/vip.png") no-repeat left 0;bottom:6px;height:32px;right:8px;width:32px}.webp .vip-icon-1{background-image:url("https://s2.51cto.com/images/100/blog/old/vip.png?x-oss-process=image/format,webp")}.vip-icon-2{background:url("https://s2.51cto.com/images/100/blog/old/vip.png") no-repeat left -64px;height:22px;width:22px}.webp .vip-icon-2{background-image:url("https://s2.51cto.com/images/100/blog/old/vip.png?x-oss-process=image/format,webp")}.vip-icon-3{background:url("https://s2.51cto.com/images/100/blog/old/vip.png") no-repeat left -108px;height:20px;width:20px}.webp .vip-icon-3{background-image:url("https://s2.51cto.com/images/100/blog/old/vip.png?x-oss-process=image/format,webp")}.vip-icon-4{background:url("https://s2.51cto.com/images/100/blog/old/vip.png") no-repeat left -152px;height:18px;width:18px}.webp .vip-icon-4{background-image:url("https://s2.51cto.com/images/100/blog/old/vip.png?x-oss-process=image/format,webp")}.vip-icon-5{background:url("https://s2.51cto.com/images/100/blog/old/vip.png") no-repeat left -152px;bottom:11px;height:18px;left:20px;position:absolute;width:18px}.webp .vip-icon-5{background-image:url("https://s2.51cto.com/images/100/blog/old/vip.png?x-oss-process=image/format,webp")}.vip-icon-1.on{background:url("https://s2.51cto.com/images/100/blog/old/vip.png") no-repeat right 0}.webp .vip-icon-1.on{background-image:url("https://s2.51cto.com/images/100/blog/old/vip.png?x-oss-process=image/format,webp")}.vip-icon-2.on{background:url("https://s2.51cto.com/images/100/blog/old/vip.png") no-repeat right -64px}.webp .vip-icon-2.on{background-image:url("https://s2.51cto.com/images/100/blog/old/vip.png?x-oss-process=image/format,webp")}.vip-icon-3.on{background:url("https://s2.51cto.com/images/100/blog/old/vip.png") no-repeat right -108px}.webp .vip-icon-3.on{background-image:url("https://s2.51cto.com/images/100/blog/old/vip.png?x-oss-process=image/format,webp")}.vip-icon-4.on{background:url("https://s2.51cto.com/images/100/blog/old/vip.png") no-repeat right -152px}.webp .vip-icon-4.on{background-image:url("https://s2.51cto.com/images/100/blog/old/vip.png?x-oss-process=image/format,webp")}.vip-icon-5.on{background:url("https://s2.51cto.com/images/100/blog/old/vip.png") no-repeat right -152px}.webp .vip-icon-5.on{background-image:url("https://s2.51cto.com/images/100/blog/old/vip.png?x-oss-process=image/format,webp")}.is-vip-bg-6{position:relative}.is-vip-bg-7 .vip-icon-4{background:url("https://s2.51cto.com/images/100/blog/old/vip.png") no-repeat 0 100%;bottom:0;height:28px;position:absolute;right:0;width:28px}.webp .is-vip-bg-7 .vip-icon-4{background-image:url("https://s2.51cto.com/images/100/blog/old/vip.png?x-oss-process=image/format,webp")}.is-vip-bg-7 .vip-icon-4.on{background:url("https://s2.51cto.com/images/100/blog/old/vip.png") no-repeat 100% 100%}.webp .is-vip-bg-7 .vip-icon-4.on{background-image:url("https://s2.51cto.com/images/100/blog/old/vip.png?x-oss-process=image/format,webp")}.is-vip-bg-3 i{bottom:0;right:12px}.is-vip-bg-4 i{bottom:0;right:0}.center-bg .vip-icon{bottom:6px;right:0}.comment-creat .is-vip-bg-6 i{bottom:-2px;right:-2px}.special-column .column-1 .column-box .center a.h2{font-size:18px}.special-column .column-1 .column-box .center h5 span{font-size:14px}.Footer{background:#fff;box-shadow:0 -1px 20px 10px hsla(0,3%,94%,.32);padding-top:35px}.Footer .Logo{box-sizing:border-box;display:block;height:60px;padding-top:16px;width:214px}.Footer .copy{color:#bbb;text-align:left}.Footer .copy a{color:#666;font-size:14px}.Footer .copy a:hover{color:#3e71f6}.Footer tr:first-child{border:0}.Footer table td{border:0;font-size:14px}.Footer a.zhiCustomBtn,.aboutList a.zhiCustomBtn{display:block}.Footer dt{font-weight:700}.Footer dl td{padding-bottom:5px}dl.foot_ab td{padding-right:43px}dl.foot_link{margin-right:20px}.urlTransfer{box-sizing:border-box;min-height:700px;padding-top:130px}.urlTransfer .logo{background:url("https://s2.51cto.com/images/100/blog/old/logo3.png") no-repeat 50%;background-size:217px 37px;height:37px;margin:0 auto;width:217px}.webp .urlTransfer .logo{background-image:url("https://s2.51cto.com/images/100/blog/old/logo3.png?x-oss-process=image/format,webp")}.urlTransfer .inner{background:#fff;box-sizing:border-box;margin:20px auto 0;padding:26px 39px;width:445px}.urlTransfer .inner .tit{background:#f7f7f7;color:#222;font-size:16px;height:45px;line-height:45px;width:240px}.urlTransfer .inner .tit i{color:#d3313a;float:left;font-size:25px;margin:0}.urlTransfer .inner .tips{color:#222;font-size:16px;margin-top:15px}.urlTransfer .inner .btn{background:#d3313a;border-radius:2px;color:#fff;cursor:pointer;display:block;height:36px;line-height:36px;margin-top:20px;text-align:center;width:100px}.urlTransfer .inner .btn:hover{background:#c22d36;color:#fff}.urlTransfer .inner .url{-webkit-line-clamp:2;line-clamp:2;-webkit-box-orient:vertical;color:#999;display:-webkit-box;font-size:16px;margin-top:10px;overflow:hidden;text-overflow:ellipsis;word-break:break-all}.urlTransfer .inner .url span{cursor:pointer}.urlTransfer .inner .url span:hover{color:#666}.common_scales_light{animation-duration:1s;-webkit-animation-duration:1s;animation-iteration-count:infinite;-webkit-animation-iteration-count:infinite;animation-name:scales_light;-webkit-animation-name:scales_light}@keyframes scales_light{0%{transform:scale(100%)}50%{transform:scale(96%)}to{transform:scale(100%)}}@-webkit-keyframes scales_light{0%{-webkit-transform:scale(100%)}50%{-webkit-transform:scale(96%)}to{-webkit-transform:scale(100%)}}.home-top-old .top-box .item-lf{padding-right:27px!important}.blog-search{font-size:14px!important}.right-fixadv{bottom:60%;position:fixed;right:20px;width:100px;z-index:999}.right-fixadv .ins{position:relative}.right-fixadv .ins span{background:url("https://s2.51cto.com/images/100/blog/sprites/sprites_ac0aa035.png") no-repeat -61px -277px;content:"";cursor:pointer;display:block;height:32px;position:absolute;right:-10px;top:-30px;transform:scale(.5);width:32px;z-index:99}.webp .right-fixadv .ins span{background-image:url("https://s2.51cto.com/images/100/blog/sprites/sprites_ac0aa035.png?x-oss-process=image/format,webp")}.right-fixadv img{width:100%}@media screen and (max-width:1199px){.Footer dl,.Footer dl.foot_link{margin-right:0}}.ac-box{display:block}.ac-box,.ac-box img{width:100%}input::-ms-clear{display:none;height:0;width:0}button,input,input[type=button]{outline:0}.header-content{display:flex;height:70px;justify-content:space-between;margin:1px auto}.header-content .header-left{display:flex;position:relative;width:50%}.header-content .header-left .Logo{box-sizing:border-box;padding-top:25px;width:100px}.header-content .header-left .Logo a{display:block;height:100%;overflow:hidden;position:relative}.header-content .header-left .Logo a img{z-index:2}.header-content .header-left .Logo h1,.header-content .header-left .Logo h2{position:absolute;text-indent:-9999em;z-index:-1}.header-content .header-left .Navigates{display:flex;font-size:16px;line-height:70px;list-style:none}.header-content .header-left .Navigates li{margin-left:38px;position:relative}.header-content .header-left .Navigates li:first-child{margin-left:43px}.header-content .header-left .Navigates li a{color:#333}.header-content .header-left .Navigates li:hover a{color:#3e71f6}.header-content .header-left .Navigates li .hot-img{height:auto;position:absolute;right:-23px;top:14px;width:24px}.header-content .header-left .Navigates .first a{display:block;height:70px;position:relative;width:100px}.header-content .header-left .Navigates .first a img{bottom:0;left:0;margin:auto;position:absolute;right:0;top:0;width:100px}.header-content .header-left .Navigates .first a img.otherimg{width:130px}.header-content .header-left .Navigates .cur a{color:#3e71f6}.header-content .header-right{display:flex;line-height:70px;list-style:none}.header-content .header-right li{margin-left:28px}.header-content .header-right .search{background:#f7f7f7;border-radius:3px;height:28px;line-height:28px;margin-top:21px;position:relative}.header-content .header-right .search .form-search{display:flex;justify-content:space-between;width:244px}.header-content .header-right .search .form-search input{background:0;border:none;flex:1;height:28px;line-height:28px;padding-left:10px}.header-content .header-right .search .form-search .blogsou{background:0;color:#999;display:inline-block;height:14px;line-height:14px;margin:7px 13px;padding:0;width:14px;z-index:99}.header-content .header-right .search .form-search .bloga-shanchutupian{color:#999;cursor:pointer;display:none}.header-content .header-right .search .form-search input:valid+.bloga-shanchutupian{display:block}.header-content .header-right .search .focusSelect_his{background:#fff;border-radius:10px;box-shadow:0 -2px 15px 0 rgba(0,0,0,.06);display:none;left:0;padding-bottom:10px;position:absolute;text-align:left;top:35px;width:100%;z-index:2}.header-content .header-right .search .focusSelect_his .hishead{border-bottom:1px solid #f6f7f8;color:#9399a6;display:block;font-size:14px;line-height:1.1;margin:20px 20px 10px;padding-bottom:10px;position:relative}.header-content .header-right .search .focusSelect_his .hishead .clearhis{color:#9399a6;cursor:pointer;float:right;font-size:14px}.header-content .header-right .search .focusSelect_his .his-item{align-items:center;color:#121212;cursor:pointer;display:flex;font-size:14px;justify-content:space-between;margin-bottom:17px;min-width:0;padding:0 20px}.header-content .header-right .search .focusSelect_his .his-item span{-webkit-line-clamp:2;-webkit-box-orient:vertical;display:-webkit-box;flex:1;line-height:25px;overflow:hidden;text-overflow:ellipsis}.header-content .header-right .search .focusSelect_his .his-item .close-his-item{color:#9399a6;display:none;font-size:12px}.header-content .header-right .search .focusSelect_his .his-item:hover .close-his-item{display:block;height:25px}.header-content .header-right .search .focusSelect_key{display:none;width:100%}.header-content .header-right .write{position:relative}.header-content .header-right .write a{color:#3e71f6}.header-content .header-right .write a .iconblog{margin-right:2px}.header-content .header-right .write .new_bloger{background-color:#ee502f;border-radius:50px;color:#fff;font-size:18px;font-weight:500;line-height:20px;padding:4px 14px;position:absolute;right:-56px;text-align:center;top:6px;transform:scale(.5);white-space:nowrap}.header-content .header-right .creative{position:relative}.header-content .header-right .creative a{color:#3e71f6}.header-content .header-right .creative .task{background:url("https://s2.51cto.com/blog/activity3.png") no-repeat top;background-size:225px 34px;bottom:-10px;display:inline-block;height:34px;left:-138px;position:absolute;width:225px}.webp .header-content .header-right .creative .task{background-image:url("https://s2.51cto.com/blog/activity3.png?x-oss-process=image/format,webp")}.header-content .header-right .message,.header-content .header-right .message .message-link{position:relative}.header-content .header-right .message .message-link i{background:#e31436;border-radius:10px;color:#fff;display:inline-block;font-size:12px;font-style:normal;left:23px;line-height:1;padding:1px 4px;position:absolute;top:-6px}.header-content .header-right .message div{background:#fff;border-radius:10px;box-shadow:0 -2px 15px 0 rgba(0,0,0,.06);display:none;left:-30px;position:absolute;top:26px;width:87px;z-index:99}.header-content .header-right .message div .ins{padding:24px 18px 24px 27px}.header-content .header-right .message div .ins a{color:#121212;display:block;font-size:14px;font-weight:400;line-height:20px;margin-bottom:17px}.header-content .header-right .message div .ins a i{background:#e31436;border-radius:10px;color:#fff;display:inline-block;font-size:12px;font-style:normal;left:23px;line-height:1;margin-left:2px;padding:1px 4px}.header-content .header-right .message div .ins a:hover{color:#3e71f6}.header-content .header-right .message div .ins a:last-child{margin-bottom:0}.header-content .header-right .message:hover div{display:block}.header-content .header-right .user{position:relative;width:24px}.header-content .header-right .user .is-vip-bg-1{display:inline-block}.header-content .header-right .user .is-vip-bg-1 img{border-radius:12px;height:24px;margin-top:23px;width:24px}.header-content .header-right .user .vip-icon{left:15px;position:absolute;top:27px}.header-content .header-right .user .user-alert{border-radius:10px;box-shadow:0 3px 10px hsla(0,0%,40%,.07);display:none;left:-280px;overflow:hidden;position:absolute;top:54px;z-index:99}.header-content .header-right .user .user-alert .ins{background:#fff;border-radius:10px;box-sizing:border-box;width:300px}.header-content .header-right .user .user-alert .ins .vip-icon{left:55px;top:50px}.header-content .header-right .user .user-alert .ins .user-base{align-items:center;background:linear-gradient(180deg,rgba(226,239,255,.5),hsla(0,0%,100%,0));color:#121212;display:block;display:flex;filter:blur(0);font-size:15px;font-weight:500;padding:10px 20px 0}.header-content .header-right .user .user-alert .ins .user-base img{border-radius:100%;height:50px;margin-right:10px;width:50px}.header-content .header-right .user .user-alert .ins .user-message{margin-top:11px;padding:0 20px}.header-content .header-right .user .user-alert .ins .user-message .user-medal{border-bottom:1px solid #f5f5f5;display:flex;flex-wrap:wrap}.header-content .header-right .user .user-alert .ins .user-message .user-medal img{height:27px;margin-right:13px;padding-bottom:14px;width:24px}.header-content .header-right .user .user-alert .ins .user-message .user-modal{border-bottom:1px solid #f5f5f5;display:flex}.header-content .header-right .user .user-alert .ins .user-message .user-modal .stat-item{color:#9f9f9f;flex:1;font-size:14px;font-weight:400;line-height:26px;margin-left:3px;padding:14px 0;text-align:left}.header-content .header-right .user .user-alert .ins .user-message .user-modal .stat-item:first-child{margin-left:0}.header-content .header-right .user .user-alert .ins .user-message .user-modal .stat-item .stat-num{color:#000;font-family:DINAlternate-Bold,DINAlternate;font-size:18px;font-weight:700;line-height:21px}.header-content .header-right .user .user-alert .ins .user-menu{border-bottom:1px solid #f5f5f5;display:flex;flex-wrap:wrap;padding:19px 20px 0}.header-content .header-right .user .user-alert .ins .user-menu a{box-sizing:border-box;color:#525d6c;display:block;font-size:14px;font-weight:400;line-height:20px;margin-bottom:20px;position:relative;width:50%}.header-content .header-right .user .user-alert .ins .user-menu a .iconblog{margin-right:8px}.header-content .header-right .user .user-alert .ins .user-menu a:nth-child(2n){padding-left:5px}.header-content .header-right .user .user-alert .ins .user-menu a .dot{background:#e31436;border-radius:5px;display:inline-block;height:5px;position:absolute;width:5px}.header-content .header-right .user .user-alert .ins .login-out{color:#525d6c;display:block;font-size:14px;font-weight:400;line-height:45px;text-align:center}.header-content .header-right .user:hover .user-alert{display:block}@media screen and (max-width:1580px){.header-content{width:1200px}}@media screen and (min-width:1581px)and (max-width:1767px){.header-content{width:1390px}}@media screen and (min-width:1768px){.header-content{width:1580px}}.Header-old .header-content{width:1200px}.home-top{background:#303030;font-size:12px;font-weight:400;height:30px;line-height:30px;position:relative;width:100%}.home-top,.home-top a,.home-top a:hover{color:#fff}.home-top .w1200{margin:0 auto;width:1200px}.home-top .left_nav{align-items:center;display:flex}.home-top .top_right{display:flex}.home-top .top_right .item-rt{margin-left:30px}.home-top .top_right .item-rt .i{font-size:12px}.home-top .top_right .item-rt.collection{cursor:pointer}.home-top .top_box{align-content:center;display:flex;height:30px;justify-content:space-between}.home-top .top_box .item-lf{padding-right:30px;position:relative}.home-top .top_box .item-lf.hot{align-items:center;display:flex}.home-top .top_box .item-lf.hot .hot-div{font-size:12px;height:14px;position:absolute;right:2px;top:-1px;width:26px}.home-top .top_box .item-lf.hot .hot-div img{height:14px;width:26px}.home-top .top_box .subweb{display:inline-block;height:30px}.home-top .top_box .subweb:hover{cursor:pointer;font-weight:600}.home-top .top_box .subweb.subweb-tag{position:relative}.home-top .top_box .subweb.subweb-tag .tagicon{display:block;height:13px;position:absolute;right:-28px;top:-3px;width:26px}.home-top .top_box .subweb.subweb-tag .tagicon img{width:100%}.home-top .nav-more-container{background:#303030;height:0;position:absolute;top:30px;transition:height .3s;width:100%;z-index:1000}.home-top .nav-more-container.height1{height:30px}.home-top .nav-more-container.height2,.home-top .nav-more-container.height3{height:120px}.home-top .nav-more-container .nav-contant-box{height:0;position:relative;transition:height .3s}.home-top .nav-more-container .nav-contant-box.height1{height:30px}.home-top .nav-more-container .nav-contant-box.height2,.home-top .nav-more-container .nav-contant-box.height3{height:120px}.home-top .nav-more-container .nav-contant{box-sizing:border-box;font-size:0;height:0;overflow:hidden;position:absolute;transition:height .3s;width:100%}.home-top .nav-more-container .nav-contant.height1{height:30px}.home-top .nav-more-container .nav-contant.height2,.home-top .nav-more-container .nav-contant.height3{height:120px}.home-top .nav-more-container .nav-contant a{color:#fff;font-size:12px;line-height:25px;margin-right:50px}.home-top .nav-more-container .nav-contant a:hover{color:#f40d04}.home-top .nav-more-container .nav-contant .ewmbox{display:inline-block;text-align:center;width:130px}.home-top .nav-more-container .nav-contant .ewmbox .imgbox{background:#fff;border:4px solid #fff;border-radius:4px;height:66px;margin:15px auto 0;overflow:hidden;width:66px}.home-top .nav-more-container .nav-contant .ewmbox img{background:#fff;border-radius:4px;height:66px;width:66px}.home-top .nav-more-container .nav-contant .ewmbox .txt{color:#c8c8c8;font-size:12px;padding-top:5px}.home-top .nav-more-container .nav-contant.wechatImageList{text-align:center}.home-top .nav-more-container .nav-contant.wechatImageList .ewmbox{width:130px}.home-top .nav-more-container .nav-contant.appImageList{text-align:center}.home-top .nav-more-container .nav-contant.appImageList .ewmbox{width:160px}.home-top .nav-more-container .nav-contant.nav-contant9{text-align:right}.home-top .nav-more-container .nav-contant.nav-contant9 .loginout{cursor:pointer;font-size:12px}.home-top .search-top i{font-size:14px}@media screen and (min-width:1768px){.home-top .w1200{width:1580px}}.publish-box{bottom:20px;display:block;height:103px;position:fixed;right:50px;width:331px;z-index:999999}.publish-box img{width:100%}.publish-box .publish-close{bottom:90px;cursor:pointer;display:inline-block;height:30px;position:fixed;right:52px;width:30px}.hover-ball{background-size:55px 43px!important;border:none!important;border-radius:0!important;right:19px!important;z-index:9999!important}.hover-ball.origin-background{background-size:140%!important}#lingjing-agent-container{z-index:99999!important}#lingjing-agent-container .markdown-container pre.chat-code-pre .hljs{white-space:normal!important}#lingjing-agent-container .chat-input-box-clean{cursor:pointer!important}@font-face{font-family:iconblog;src:url("https://static2.51cto.com/edu/blog/blog-static/iconFont/iconfont.woff2?t=1704267097589") format("woff2"),url("https://static2.51cto.com/edu/blog/blog-static/iconFont/iconfont.woff?t=1704267097589") format("woff"),url("https://static2.51cto.com/edu/blog/blog-static/iconFont/iconfont.ttf?t=1704267097589") format("truetype")}.iconblog{-webkit-font-smoothing:antialiased;-moz-osx-font-smoothing:grayscale;font-family:iconblog!important;font-size:16px;font-style:normal}.blogllc:before{content:"\e6c6"}.blogsousuo1:before{content:"\e6c5"}.blogyijianfk:before{content:"\e6c4"}.blogyonghu:before{content:"\e6c3"}.blogyinhao:before{content:"\e6bf"}.blogpaixu:before{content:"\e6c0"}.blogxuanzhong:before{content:"\e6c1"}.blogxuanxiang:before{content:"\e6c2"}.blogfanhuidb:before{content:"\e6a3"}.blogfenxiang2:before{content:"\e6a4"}.blogchuangzuozx:before{content:"\e6a5"}.blogijilu:before{content:"\e6a6"}.blogshoucang-4:before{content:"\e6a7"}.blogqianbao:before{content:"\e6a8"}.blogzhuanlan:before{content:"\e6a9"}.blogquan:before{content:"\e6bd"}.blogwode:before{content:"\e6be"}.bloggengduo1:before{content:"\e695"}.blogsousuo:before{content:"\e698"}.blogxiewz:before{content:"\e69b"}.bloghuati1:before{content:"\e69c"}.bloggaiban:before{content:"\e693"}.bloga-2023:before{content:"\e694"}.blogjichuxinxi:before{content:"\e704"}.blogimport:before{content:"\e700"}.blogqiandao:before{content:"\e6ff"}.blogyidaka:before{content:"\e6fe"}.blogqiandaoqueren:before{content:"\e6fc"}.blogshenfenrenzhengbeifen:before{content:"\e6f8"}.bloggonggaobeifen:before{content:"\e6f7"}.blogunfold:before{content:"\e6f4"}.bloghuati:before{content:"\e6f3"}.blogrongyurenzheng:before{content:"\e6f1"}.blogpaixujiang:before{content:"\e6ee"}.blogpaixusheng:before{content:"\e6ed"}.blogxunzhangguanli:before{content:"\e6ec"}.bloghelp:before{content:"\e6eb"}.blogxiewenzhang:before{content:"\e6ea"}.blogzuixinblogzuixin:before{content:"\e63f"}.blogzuire:before{content:"\e63e"}.blogxiangshangpaixu:before{content:"\e6e6"}.blogzhujiao2:before{content:"\e6e0"}.blogzhujiang2:before{content:"\e6df"}.blogxuesheng2:before{content:"\e6de"}.blogyitijiao2:before{content:"\e6dd"}.blogrili2:before{content:"\e6dc"}.blogpaixu2:before{content:"\e6db"}.blogjiezhishijian2:before{content:"\e6da"}.blogdanxuanxuanzhong:before{content:"\e6d9"}.blogdanxuanweixuanzhong:before{content:"\e6d8"}.blogzuoye2:before{content:"\e6d5"}.blogshijian2:before{content:"\e6d4"}.blogjiaoshi2:before{content:"\e6d3"}.blogmulu:before{content:"\e63d"}.bloga-bianzu9:before{content:"\e63b"}.bloga-bianzu8:before{content:"\e63c"}.bloga-bianzu10:before{content:"\e638"}.bloga-bianzu12:before{content:"\e639"}.bloga-bianzu6:before{content:"\e63a"}.bloga-bianzu11:before{content:"\e637"}.bloga-bianzu7:before{content:"\e636"}.bloga-shanchutupian:before{content:"\e6cd"}.blogtianjiabeifen:before{content:"\e6cc"}.blogtishibeifen:before{content:"\e6cb"}.blogtishi2beifen:before{content:"\e6ca"}.blogjubaobeifen:before{content:"\e6c7"}.blogfuwuqibeifen:before{content:"\e6bc"}.blogqiyexinxihuabeifen:before{content:"\e6bb"}.blogyouxikaifabeifen:before{content:"\e6ba"}.blogrengongzhinengbeifen:before{content:"\e6b9"}.blogruanjianyanfabeifen:before{content:"\e6b8"}.blogkaoshirenzhengbeifen:before{content:"\e6b7"}.bloghongmengbeifen:before{content:"\e6b6"}.blogofficebangongbeifen:before{content:"\e6b5"}.blogqianrushibeifen:before{content:"\e6b4"}.blogyidongkaifabeifen:before{content:"\e6b3"}.blogbianchengyuyanbeifen:before{content:"\e6b2"}.blogqianduankaifabeifen:before{content:"\e6b1"}.blogyunjisuanbeifen:before{content:"\e6b0"}.blogshujukubeifen:before{content:"\e6af"}.blogxitongyunweibeifen:before{content:"\e6ae"}.blogwangluoanquanbeifen:before{content:"\e6ad"}.blogJavabeifen:before{content:"\e6ac"}.blogpythonbeifen:before{content:"\e6ab"}.blogdashujubeifen:before{content:"\e6aa"}.bloga-15beifen41:before{content:"\e6a2"}.bloga-15beifen4:before{content:"\e6a1"}.bloga-15beifen5:before{content:"\e6a0"}.bloga-15beifen2:before{content:"\e69f"}.bloga-15beifen3:before{content:"\e69e"}.bloga-15beifen:before{content:"\e69d"}.blogchenggongtishi:before{content:"\e69a"}.blogxiepinglun:before{content:"\e699"}.blogwodeqianbaobeifen:before{content:"\e697"}.blogdianzanxuanzhong:before{content:"\e696"}.bloga-icbokewenda:before{content:"\e692"}.bloga-icyijianfankui:before{content:"\e691"}.bloga-icfenxiangbeifen:before{content:"\e690"}.bloga-icwodedingyuezhuanlan:before{content:"\e68f"}.bloga-icdingyuezhuanlan:before{content:"\e68e"}.bloga-icshouye:before{content:"\e68d"}.bloga-icyonghu:before{content:"\e68c"}.blogshanchu1:before{content:"\e68a"}.blogyuedu:before{content:"\e689"}.blogpinglun3:before{content:"\e687"}.blogfenxiang1:before{content:"\e686"}.bloggengduo:before{content:"\e67f"}.blogshanchu18:before{content:"\e67e"}.blogquxiao18:before{content:"\e67d"}.bloglink:before{content:"\e67c"}.blogshanchu:before{content:"\e67b"}.blogdianzan:before{content:"\e679"}.blogremensousuo:before{content:"\e676"}.bloglishijilu:before{content:"\e675"}.bloga-blogdianzanxe622:before{content:"\e622"}.blogchuangzuoshezhibeifen:before{content:"\e631"}.blogchuangzuoliebiao:before{content:"\e632"}.blogchuangzuoshouye:before{content:"\e633"}.blogchuangzuoqushi:before{content:"\e634"}.blogchuangzuotianjia:before{content:"\e635"}.blogchuangzuogongju:before{content:"\e623"}.blogchuangzuolanhufan:before{content:"\e624"}.blogchuangzuoguanli:before{content:"\e625"}.blogchuangzuohuodong:before{content:"\e626"}.blogchuangzuorli:before{content:"\e628"}.blogchuangzuochuangzuo:before{content:"\e629"}.blogchuangzuoshezhi:before{content:"\e62b"}.blogchuangzuoshuju:before{content:"\e62f"}.blogchuangzuoxiazai:before{content:"\e630"}.blogfenxiang:before{content:"\e61b"}.blogNextpage:before{content:"\e62e"}.blogPreviouspage:before{content:"\e62d"}.blogxuanzhongbeifen1:before{content:"\e62c"}.blogweixuanzhongbeifen:before{content:"\e62a"}.blogright:before{content:"\e627"}.blogshouqi:before{content:"\e620"}.blogyuedu1:before{content:"\e621"}.blogsixin1:before{content:"\e61f"}.blogshoucang:before{content:"\e61e"}.blogpinglun1:before{content:"\e61d"}.blogzhankai:before{content:"\e61c"}.blogbianji1:before{content:"\e61a"}.blogguanzhu:before{content:"\e619"}.blogbianji:before{content:"\e617"}.blogshanchu2:before{content:"\e618"}.blogfenxiangqq:before{content:"\e614"}.blogfenxiangweixin:before{content:"\e615"}.blogfenxiangweibo:before{content:"\e616"}.blogqqqun:before{content:"\e611"}.blogboke:before{content:"\e612"}.blogguan:before{content:"\e613"}.blogpinglun:before{content:"\e605"}.blogpinglun2:before{content:"\e606"}.blogshang:before{content:"\e607"}.blogsixin:before{content:"\e608"}.blogshou:before{content:"\e609"}.blogzan2:before{content:"\e60a"}.blogfen:before{content:"\e60b"}.blogshan:before{content:"\e60c"}.blogzhi:before{content:"\e60d"}.blogsou:before{content:"\e60e"}.blogzan:before{content:"\e60f"}.blogduo:before{content:"\e610"}.blogxie:before{content:"\e604"}::-webkit-scrollbar{-webkit-appearance:none;height:10px;width:10px}::-webkit-scrollbar-thumb{background-color:rgba(0,0,0,.3);border:2px solid #fff;border-radius:4px}::-webkit-scrollbar-thumb:hover{background-color:rgba(0,0,0,.5)}::-webkit-scrollbar-thumb:window-inactive{background-color:rgba(0,0,0,.2)}.msg-index-box{background:#fff;border-radius:10px;left:50%;margin-left:-300px;padding:25px 10px;position:fixed;top:30%;width:606px;z-index:9999}.msg-index-box .top-bg{background:url("https://s2.51cto.com/images/100/blog/index/followbg.png") no-repeat top;height:129px;left:0;position:absolute;top:0;width:626px}.webp .msg-index-box .top-bg{background-image:url("https://s2.51cto.com/images/100/blog/index/followbg.png?x-oss-process=image/format,webp")}.msg-index-box .follow-close{background:url("https://s2.51cto.com/images/100/blog/index/sprites_indexfp0908.png") -61px -206px;cursor:pointer;height:18px;position:absolute;right:14px;top:14px;width:19px;z-index:1}.webp .msg-index-box .follow-close{background-image:url("https://s2.51cto.com/images/100/blog/index/sprites_indexfp0908.png?x-oss-process=image/format,webp")}.msg-index-box .con-box{left:0;position:absolute;top:0;width:100%}.msg-index-box .icon-bg{left:97px;position:absolute;top:48px}.msg-index-box .icon-1{background:url("https://s2.51cto.com/images/100/blog/index/sprites_indexfp0908.png") -8px -206px;height:31px;width:37px}.webp .msg-index-box .icon-1{background-image:url("https://s2.51cto.com/images/100/blog/index/sprites_indexfp0908.png?x-oss-process=image/format,webp")}.msg-index-box .icon-2{background:url("https://s2.51cto.com/images/100/blog/index/sprites_indexfp0908.png") -92px -199px;height:38px;width:38px}.webp .msg-index-box .icon-2{background-image:url("https://s2.51cto.com/images/100/blog/index/sprites_indexfp0908.png?x-oss-process=image/format,webp")}.msg-index-box h2{color:#4285f4;font-size:26px;line-height:1;margin-bottom:20px;margin-top:26px;text-align:center}.msg-index-box .con{color:#333;font-size:14px;line-height:24px;text-align:center}.msg-index-box .con a{color:#4285f4}.msg-index-box .code-bg{background:url("https://s2.51cto.com/images/100/blog/index/followcode.png") no-repeat;height:148px;margin:20px auto 0;width:148px}.webp .msg-index-box .code-bg{background-image:url("https://s2.51cto.com/images/100/blog/index/followcode.png?x-oss-process=image/format,webp")}.msg-index-box .code-bg img{width:100%}.msg-index-box .tipBox{line-height:20px;margin:0 auto;text-align:left;width:350px}.msg-index-box .tipBox .btn{color:#3e71f6;cursor:pointer}.msg-index-box .tipBox .txt{display:inline-block;line-height:12px;max-width:120px}.msg-index-box .btn-box{margin-top:20px;text-align:center}.msg-index-box .btn-box p{border-radius:6px;cursor:pointer;display:inline-block;font-size:14px;height:28px;line-height:28px;padding:0 16px}.msg-index-box .btn-1{border:1px solid #fff;color:#666;margin-right:46px}.msg-index-box .btn-2{border:1px solid #4285f4;color:#4285f4}.Header{top:30px}.hljs-center{text-align:center}.hljs-right{text-align:right}#result{overflow:auto}.detail-content-left s{text-decoration:line-through}.cto-mermaid{text-align:center}.cto-mermaid svg{max-width:100%}#result img{height:auto}.report-dialog-root{display:none}.am-engine img{vertical-align:middle}.mb24{margin-bottom:24px}.mb30{margin-bottom:30px}body{background:#f7f8f9}.Header{position:fixed;width:100%}.home-top{position:fixed;top:0;z-index:999}.detail-content-new{background:#f7f8f9;padding:114px 0 30px}.detail-content-new .jia1,.detail-content-new .jia2{color:#3e71f6}.detail-content-new .fixtitle{background:#fff;box-shadow:0 3px 10px #efefef;display:none;height:61px;left:0;line-height:61px;position:fixed;top:0;width:100%;z-index:999}.detail-content-new .fixtitle h3{box-sizing:border-box;color:#333;font-size:24px;overflow:hidden;padding:0 35px;text-overflow:ellipsis;white-space:nowrap;width:883px}.detail-content-new .fixtitle .messbox .checkFollow{background:#3e71f6;border:none;border-radius:0;border-radius:2px;box-sizing:border-box;color:#666;color:#fff;cursor:pointer;float:right;font-size:14px;height:32px;line-height:32px;margin:13px 0 0 15px;text-align:center;width:90px}.detail-content-new .fixtitle .messbox .checkFollow.in{background:0;border:1px solid #789bf9;color:#3e71f6;padding-left:0}.detail-content-new .fixtitle .messbox .checkFollow.on{background:#3e71f6;font-family:iconblog;padding-left:19px;text-align:left}.detail-content-new .fixtitle .messbox .checkFollow.on:before{content:"";font-size:20px;vertical-align:bottom}.detail-content-new .fixtitle .messbox .checkFollow.on:hover{background:#3d62f5}.detail-content-new .fixtitle .messbox .checkFollow.off{background:#ddd;padding-left:0}.detail-content-new .fixtitle .messbox .name{color:#17233f;float:right;margin-left:10px;max-width:110px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.detail-content-new .fixtitle .messbox strong{float:right;height:34px;margin-top:13px;position:relative;width:34px}.detail-content-new .fixtitle .messbox .avatar img{border-radius:34px;height:34px;width:34px}.detail-content-new .Page .common-section{background:#fff;border-radius:2px}.detail-content-new .Page .detail-content-left{float:left;width:874px}.detail-content-new .Page .detail-content-left.set-right{float:right}.detail-content-new .Page .detail-content-left .common-spacing{padding:15px 35px}.detail-content-new .Page .detail-content-left .content-taotao-h{display:none}.detail-content-new .Page .detail-content-left .article-detail{padding-bottom:27px}.detail-content-new .Page .detail-content-left .article-detail>.title{word-wrap:break-word;font-size:37px;line-height:40px;margin-bottom:5px;padding:5px 0 10px;word-break:break-all}.detail-content-new .Page .detail-content-left .article-detail>.title h1{color:#333;display:inline;font-size:28px}.detail-content-new .Page .detail-content-left .article-detail>.title span{border-radius:4px;color:#fff;display:inline-block;font-size:14px;line-height:24px;margin-right:1px;position:relative;text-align:center;top:-4px;width:36px}.detail-content-new .Page .detail-content-left .article-detail>.title span:first-child{margin-left:20px}.detail-content-new .Page .detail-content-left .article-detail>.title span.tuijian{background:#f3c352}.detail-content-new .Page .detail-content-left .article-detail>.title span.original{background:#99cea4}.detail-content-new .Page .detail-content-left .article-detail>.title span.reprint{background:#84c4fa}.detail-content-new .Page .detail-content-left .article-detail>.title span.translation{background:#fea4a4}.detail-content-new .Page .detail-content-left .article-detail>.title span.type_selected{background:#84a0fa}.detail-content-new .Page .detail-content-left .article-detail>.title .examine{background:#f4f5f6;color:#b7bdc9;display:inline-block;font-size:14px;font-weight:400;height:22px;line-height:22px;text-align:center;width:49px}.detail-content-new .Page .detail-content-left .article-detail .messbox{background:#f9f9fa;border-radius:2px;color:#6b7486;padding:15px 15px 5px}.detail-content-new .Page .detail-content-left .article-detail .messbox p.mess-line1{line-height:1}.detail-content-new .Page .detail-content-left .article-detail .messbox p.mess-line1 a{color:#6b7486}.detail-content-new .Page .detail-content-left .article-detail .messbox p.mess-line1 a:hover{color:#3e71f6}.detail-content-new .Page .detail-content-left .article-detail .messbox p.mess-line1 .fl{padding-right:12px}.detail-content-new .Page .detail-content-left .article-detail .messbox p.mess-line1 #copyright-btn{cursor:pointer;font-size:12px;-moz-user-select:none;-webkit-user-select:none;-ms-user-select:none;-khtml-user-select:none;user-select:none}.detail-content-new .Page .detail-content-left .article-detail .messbox p.mess-line1 #copyright-btn:hover{color:#3e71f6}.detail-content-new .Page .detail-content-left .article-detail .messbox p.mess-tag{margin-top:15px}.detail-content-new .Page .detail-content-left .article-detail .messbox p.mess-tag strong{float:left;font-weight:400;margin-right:22px}.detail-content-new .Page .detail-content-left .article-detail .messbox p.mess-tag strong em{font-style:normal;line-height:24px;margin-right:11px}.detail-content-new .Page .detail-content-left .article-detail .messbox p.mess-tag strong a,.detail-content-new .Page .detail-content-left .article-detail .messbox p.mess-tag strong span{background:#efeff1;color:#5c6578;display:inline-block;font-size:12px;height:24px;line-height:24px;margin-bottom:10px;margin-right:13px;padding:0 8px}.detail-content-new .Page .detail-content-left .article-detail .messbox p.mess-tag strong a:last-child,.detail-content-new .Page .detail-content-left .article-detail .messbox p.mess-tag strong span:last-child{margin-right:0}.detail-content-new .Page .detail-content-left .article-detail .messbox p.mess-tag strong a.subject,.detail-content-new .Page .detail-content-left .article-detail .messbox p.mess-tag strong span.subject{background:#e6ebfa;color:#3e71f6}.detail-content-new .Page .detail-content-left .article-detail .messbox p.mess-tag strong a.subject i,.detail-content-new .Page .detail-content-left .article-detail .messbox p.mess-tag strong span.subject i{float:left;font-size:12px;margin:0 4px 0 0}.detail-content-new .Page .detail-content-left .article-detail .messbox p.mess-tag strong a:hover{color:#3e71f6}.detail-content-new .Page .detail-content-left .article-detail .messbox p.mess-tag strong b{color:#6b7486;font-size:14px;font-weight:400}.detail-content-new .Page .detail-content-left .article-detail .copytext{color:#9399a6;display:none;font-size:12px;margin-top:10px;word-break:break-all}.detail-content-new .Page .detail-content-left .article-detail .copytext a{color:#9399a6}.detail-content-new .Page .detail-content-left .article-detail .copytext2{color:#9399a6;font-size:12px;margin-top:10px;word-break:break-all}.detail-content-new .Page .detail-content-left .article-detail .recommend-video{display:none;justify-content:space-between;margin:20px auto}.detail-content-new .Page .detail-content-left .article-detail .recommend-video.recommend-video-1{justify-content:center}.detail-content-new .Page .detail-content-left .article-detail .recommend-video .video{width:49%}.detail-content-new .Page .detail-content-left .article-detail .recommend-video .video a{background:#f8f8fb;border-radius:2px;box-sizing:border-box;display:flex;height:130px;padding:14px}.detail-content-new .Page .detail-content-left .article-detail .recommend-video .video a .pic{border-radius:2px;overflow:hidden;position:relative;width:184px}.detail-content-new .Page .detail-content-left .article-detail .recommend-video .video a .pic:after{background:rgba(0,0,0,.3) url("https://s2.51cto.com/blog/sprites/videoicon.png") no-repeat 50%;content:"";height:104px;left:0;position:absolute;top:0;width:184px}.webp .detail-content-new .Page .detail-content-left .article-detail .recommend-video .video a .pic:after{background-image:url("https://s2.51cto.com/blog/sprites/videoicon.png?x-oss-process=image/format,webp")}.detail-content-new .Page .detail-content-left .article-detail .recommend-video .video a .pic img{height:104px;width:184px}.detail-content-new .Page .detail-content-left .article-detail .recommend-video .video a .detail{display:flex;flex-direction:column;justify-content:center;line-height:1.7;padding-left:14px;width:calc(100% - 200px)}.detail-content-new .Page .detail-content-left .article-detail .recommend-video .video a .detail .title{color:#17233f;font-size:16px;max-height:58px;overflow:hidden}.detail-content-new .Page .detail-content-left .article-detail .recommend-video .video a .detail .dec{color:#8c92a2;font-size:14px;max-height:45px;overflow:hidden}.detail-content-new .Page .detail-content-left .article-detail .article-content-wrap{border-bottom:1px solid #f3f3f3;color:#17233f;font-size:16px;margin-bottom:30px;padding-bottom:30px;word-break:break-all}.detail-content-new .Page .detail-content-left .article-detail .article-content-wrap img{cursor:zoom-in;max-width:100%}.detail-content-new .Page .detail-content-left .article-detail .article-content-wrap .artical-content-bak{max-width:100%;padding:0 0 20px!important}.detail-content-new .Page .detail-content-left .article-detail .article-content-wrap .all-question{color:#3e71f6;cursor:pointer}.detail-content-new .Page .detail-content-left .article-detail .label-list{margin-top:20px;padding-left:90px;position:relative}.detail-content-new .Page .detail-content-left .article-detail .label-list .tag-text{color:#9399a6;display:inline;font-size:13px;line-height:35px;margin-right:15px;word-break:break-all}.detail-content-new .Page .detail-content-left .article-detail .label-list .tag-text:hover{color:#7d828c}.detail-content-new .Page .detail-content-left .article-detail .label-list .tag-text:nth-child(3n-2){color:#b6c2bb}.detail-content-new .Page .detail-content-left .article-detail .label-list .tag-text:nth-child(3n-2):hover{color:#9ea8a2}.detail-content-new .Page .detail-content-left .article-detail .label-list .tag-text:nth-child(3n-1){color:#e0d6d1}.detail-content-new .Page .detail-content-left .article-detail .label-list .tag-text:nth-child(3n-1):hover{color:#c7beb9}.detail-content-new .Page .detail-content-left .article-detail .label-list span{color:#17233f;font-size:16px;left:0;position:absolute;top:0}.detail-content-new .Page .detail-content-left .article-detail .label-list a{background:#f6f7f8;border-radius:2px;color:#6b7484;display:inline-block;height:30px;line-height:30px;margin:0 12px 15px 0;max-width:80%;overflow:hidden;padding:0 20px;text-overflow:ellipsis;white-space:nowrap}.detail-content-new .Page .detail-content-left .article-detail .label-list a.cur,.detail-content-new .Page .detail-content-left .article-detail .label-list a:hover{background:#3e71f6;color:#fff}.detail-content-new .Page .detail-content-left .article-detail .action-box{text-align:center}.detail-content-new .Page .detail-content-left .article-detail .action-box ul li{display:inline-block;list-style:none;position:relative;width:105px}.detail-content-new .Page .detail-content-left .article-detail .action-box ul li:last-child{margin-bottom:0}.detail-content-new .Page .detail-content-left .article-detail .action-box ul li.share:hover .bdsharebuttonbox{display:block}.detail-content-new .Page .detail-content-left .article-detail .action-box ul li .bdsharebuttonbox{left:8px}.detail-content-new .Page .detail-content-left .article-detail .action-box ul li strong{display:inline-block;font-weight:400;position:relative;text-align:center;width:80px}.detail-content-new .Page .detail-content-left .article-detail .action-box ul li strong.is-praise a i{background:url("https://s2.51cto.com/images/100/blog/old/zan1.png") no-repeat top;background-size:47px 47px;display:inline-block;height:47px;width:47px}.webp .detail-content-new .Page .detail-content-left .article-detail .action-box ul li strong.is-praise a i{background-image:url("https://s2.51cto.com/images/100/blog/old/zan1.png?x-oss-process=image/format,webp")}.detail-content-new .Page .detail-content-left .article-detail .action-box ul li strong.is-praise.on a i{background:url("https://s2.51cto.com/images/100/blog/old/zan2.png") no-repeat top;background-size:47px 47px}.webp .detail-content-new .Page .detail-content-left .article-detail .action-box ul li strong.is-praise.on a i{background-image:url("https://s2.51cto.com/images/100/blog/old/zan2.png?x-oss-process=image/format,webp")}.detail-content-new .Page .detail-content-left .article-detail .action-box ul li strong.is-praise.no-praise a i,.detail-content-new .Page .detail-content-left .article-detail .action-box ul li strong.is-praise.on.no-praise a i{background:url("https://s2.51cto.com/images/100/blog/old/zan.gif") no-repeat top;background-size:47px 47px}.detail-content-new .Page .detail-content-left .article-detail .action-box ul li strong.favorites-opt a i{background:url("https://s2.51cto.com/images/100/blog/old/ping1.png") no-repeat top;background-size:47px 47px;display:inline-block;height:47px;width:47px}.webp .detail-content-new .Page .detail-content-left .article-detail .action-box ul li strong.favorites-opt a i{background-image:url("https://s2.51cto.com/images/100/blog/old/ping1.png?x-oss-process=image/format,webp")}.detail-content-new .Page .detail-content-left .article-detail .action-box ul li strong.favorites-opt.on a i{background:url("https://s2.51cto.com/images/100/blog/old/ping2.png") no-repeat top;background-size:47px 47px}.webp .detail-content-new .Page .detail-content-left .article-detail .action-box ul li strong.favorites-opt.on a i{background-image:url("https://s2.51cto.com/images/100/blog/old/ping2.png?x-oss-process=image/format,webp")}.detail-content-new .Page .detail-content-left .article-detail .action-box ul li strong.favorites-opt.no-favorites a i,.detail-content-new .Page .detail-content-left .article-detail .action-box ul li strong.favorites-opt.on.no-favorites a i{background:url("https://s2.51cto.com/images/100/blog/old/ping.gif") no-repeat top;background-size:47px 47px}.detail-content-new .Page .detail-content-left .article-detail .action-box ul li strong:hover a{box-shadow:0 8px 16px 0 rgba(23,35,63,.12)}.detail-content-new .Page .detail-content-left .article-detail .action-box ul li strong a{background:#fff;border:1px solid #f4f4f4;border-radius:47px;box-shadow:0 8px 16px 0 rgba(23,35,63,.04);display:block;height:47px;line-height:47px;margin:0 auto 5px;width:47px}.detail-content-new .Page .detail-content-left .article-detail .action-box ul li strong a i{color:#818797}.detail-content-new .Page .detail-content-left .article-detail .action-box ul li strong a i.blogshang,.detail-content-new .Page .detail-content-left .article-detail .action-box ul li strong a i.blogzan{font-size:19px}.detail-content-new .Page .detail-content-left .article-detail .action-box ul li strong a i.blogshou{font-size:21px}.detail-content-new .Page .detail-content-left .article-detail .action-box ul li strong a i.blogpinglun{font-size:19px}.detail-content-new .Page .detail-content-left .article-detail .action-box ul li strong a i.blogfen{font-size:23px}.detail-content-new .Page .detail-content-left .article-detail .action-box ul li strong a i.blogzhi{font-size:18px}.detail-content-new .Page .detail-content-left .article-detail .action-box ul li strong span{color:#979da9;line-height:1}.detail-content-new .Page .detail-content-left .article-detail .action-box ul li strong span b{font-weight:400}.detail-content-new .Page .detail-content-left .article-detail .action-box ul li strong.on a i{color:#3e71f6}.detail-content-new .Page .detail-content-left .article-detail .lists{margin-top:40px}.detail-content-new .Page .detail-content-left .article-detail .lists p{color:#818797;max-width:45%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.detail-content-new .Page .detail-content-left .article-detail .lists p a{color:#818797}.detail-content-new .Page .detail-content-left .article-detail .lists p a:hover{color:#17233f}.detail-content-new .Page .detail-content-left .article-detail .lists p:last-child{text-align:right}.detail-content-new .Page .detail-content-left .article-edit{margin-bottom:10px;margin-top:10px}.detail-content-new .Page .detail-content-left .article-edit a{color:#9399a6;display:inline-block;font-size:12px;height:23px;line-height:23px;margin-left:20px}.detail-content-new .Page .detail-content-left .article-edit a:hover{color:#3e71f6}.detail-content-new .Page .detail-content-left .article-edit a i{float:left;font-size:14px;margin-right:5px;opacity:.8}.detail-content-new .Page .detail-content-left .common-sub-title{border-bottom:1px solid #f5f5f5;height:48px;line-height:48px;margin-bottom:3px}.detail-content-new .Page .detail-content-left .common-sub-title h2,.detail-content-new .Page .detail-content-left .common-sub-title strong{color:#333;display:inline-block;font-size:20px}.detail-content-new .Page .detail-content-left .common-sub-title .more{color:#999}.detail-content-new .Page .detail-content-left .comment-textarea{padding-top:20px}.detail-content-new .Page .detail-content-left .comment-textarea .avatar{float:left;height:40px;margin-right:15px;position:relative;width:40px}.detail-content-new .Page .detail-content-left .comment-textarea .avatar img{border-radius:40px;height:40px;width:40px}.detail-content-new .Page .detail-content-left .comment-textarea .textarea-box{float:left;width:749px}.detail-content-new .Page .detail-content-left .comment-textarea .textarea-box .textarea-show{background:#fff;border:1px solid #e5e5e5;border-radius:2px;box-sizing:border-box;color:#818797;cursor:pointer;height:44px;line-height:44px;margin-bottom:20px;position:relative}.detail-content-new .Page .detail-content-left .comment-textarea .textarea-box .textarea-show span{display:inline-block;overflow:hidden;padding-left:15px;text-overflow:ellipsis;white-space:nowrap;width:80%}.detail-content-new .Page .detail-content-left .comment-textarea .textarea-box .textarea-show strong{background:#f5f5f5;border-left:1px solid #e5e5e5;display:inline-block;height:42px;line-height:42px;position:absolute;right:0;text-align:center;top:0;width:78px}.detail-content-new .Page .detail-content-left .comment-textarea .textarea-box .textarea-hide{display:none}.detail-content-new .Page .detail-content-left .comment-textarea .textarea-box .textarea-hide .top{margin-bottom:10px}.detail-content-new .Page .detail-content-left .comment-textarea .textarea-box .textarea-hide .top textarea{background:#fff;border:1px solid #e5e5e5;border-radius:2px;box-sizing:border-box;color:#17233f;height:78px;outline:0;padding:12px 15px;resize:none;width:100%}.detail-content-new .Page .detail-content-left .comment-textarea .textarea-box .textarea-hide .bot .publish-btn{background:#3e71f6;border-radius:2px;color:#fff;cursor:pointer;display:inline-block;height:35px;line-height:35px;text-align:center;width:110px}.detail-content-new .Page .detail-content-left .comment-textarea .textarea-box .textarea-hide .bot span{color:#9399a6;font-size:12px;line-height:35px;margin-right:16px}.detail-content-new .Page .detail-content-left .comment-num{border-bottom:1px solid #f5f5f5;color:#333;font-size:20px;height:56px;line-height:56px}.detail-content-new .Page .detail-content-left .comment-num span{color:#999}.detail-content-new .Page .detail-content-left .comment-num span b{font-weight:400}.detail-content-new .Page .detail-content-left .comment-num .sort{cursor:pointer;font-size:14px;font-weight:400;margin-left:15px}.detail-content-new .Page .detail-content-left .comment-num .sort.on{color:#3e71f6}.detail-content-new .Page .detail-content-left .comment-num .sort .iconblog{float:left;font-size:14px;margin-right:5px}.detail-content-new .Page .detail-content-left .comment-box{padding-bottom:27px}.detail-content-new .Page .detail-content-left .comment-List-box .floor-1{border-bottom:1px solid #f5f5f5;padding-top:25px}.detail-content-new .Page .detail-content-left .comment-List-box .floor-1.floor-n{display:none}.detail-content-new .Page .detail-content-left .comment-List-box .floor-2{padding-left:50px}.detail-content-new .Page .detail-content-left .comment-List-box .comment-List{display:flex;padding-bottom:25px}.detail-content-new .Page .detail-content-left .comment-List-box .comment-List .avatar{float:left;height:40px;margin-right:10px;margin-top:4px;position:relative;width:40px}.detail-content-new .Page .detail-content-left .comment-List-box .comment-List .avatar img{border-radius:40px;height:40px;width:40px}.detail-content-new .Page .detail-content-left .comment-List-box .comment-List .comment-detail{float:left;width:754px}.detail-content-new .Page .detail-content-left .comment-List-box .comment-List .comment-detail h3{color:#17233f;font-size:14px;height:28px;line-height:1;line-height:28px;margin-bottom:4px}.detail-content-new .Page .detail-content-left .comment-List-box .comment-List .comment-detail h3 .tag{background:#ebf1fe;border-radius:2px;color:#3e71f6;display:inline-block;font-size:12px;height:20px;line-height:20px;margin-left:7px;margin-top:4px;padding:0 8px}.detail-content-new .Page .detail-content-left .comment-List-box .comment-List .comment-detail h3 i{font-style:normal;margin:0 12px}.detail-content-new .Page .detail-content-left .comment-List-box .comment-List .comment-detail h3 .time{color:#9399a6;font-size:14px;font-weight:400}.detail-content-new .Page .detail-content-left .comment-List-box .comment-List .comment-detail .reply-content{background:#f9f9fa;border-radius:2px;color:#9399a6;font-size:16px;margin-bottom:12px;margin-top:17px;padding:10px 15px;word-break:break-word}.detail-content-new .Page .detail-content-left .comment-List-box .comment-List .comment-detail .content{color:#17233f;font-size:16px;margin-bottom:12px;word-break:break-word}.detail-content-new .Page .detail-content-left .comment-List-box .comment-List .comment-detail .action{height:23px;line-height:23px}.detail-content-new .Page .detail-content-left .comment-List-box .comment-List .comment-detail .action span{color:#9399a6;cursor:pointer;float:left;margin-right:20px}.detail-content-new .Page .detail-content-left .comment-List-box .comment-List .comment-detail .action span:hover i{color:#818797}.detail-content-new .Page .detail-content-left .comment-List-box .comment-List .comment-detail .action span.on,.detail-content-new .Page .detail-content-left .comment-List-box .comment-List .comment-detail .action span.on i{color:#3e71f6}.detail-content-new .Page .detail-content-left .comment-List-box .comment-List .comment-detail .action span i{color:#c5c8cf;float:left;margin-right:6px}.detail-content-new .Page .detail-content-left .comment-List-box .comment-List .comment-detail .action span b{font-weight:400}.detail-content-new .Page .detail-content-left .comment-List-box .comment-List .comment-detail .textarea-hide{margin-top:25px}.detail-content-new .Page .detail-content-left .comment-List-box .comment-List .comment-detail .textarea-hide .top{margin-bottom:10px}.detail-content-new .Page .detail-content-left .comment-List-box .comment-List .comment-detail .textarea-hide .top textarea{background:#fff;border:1px solid #e5e5e5;border-radius:2px;box-sizing:border-box;color:#17233f;height:78px;outline:0;padding:12px 15px;resize:none;width:100%}.detail-content-new .Page .detail-content-left .comment-List-box .comment-List .comment-detail .textarea-hide .bot .publish-btn{background:#3e71f6;border-radius:2px;color:#fff;cursor:pointer;display:inline-block;font-weight:400;height:32px;line-height:32px;text-align:center;width:110px}.detail-content-new .Page .detail-content-left .comment-List-box .comment-List .comment-detail .textarea-hide .bot span{color:#9399a6;cursor:pointer;line-height:35px;margin-right:16px}.detail-content-new .Page .detail-content-left .comment-List-box .more-toggle{color:#17233f;cursor:pointer;display:inline-block;padding-bottom:25px;padding-right:20px;position:relative}.detail-content-new .Page .detail-content-left .comment-List-box .more-toggle:hover,.detail-content-new .Page .detail-content-left .comment-List-box .more-toggle:hover i{color:#3e71f6}.detail-content-new .Page .detail-content-left .comment-List-box .more-toggle i{color:#9399a6;position:absolute;right:0;top:-2px;transform:rotate(-90deg);-ms-transform:rotate(-90deg);-moz-transform:rotate(-90deg);-webkit-transform:rotate(-90deg);-o-transform:rotate(-90deg)}.detail-content-new .Page .detail-content-left .pagination{font-size:12px;margin:60px auto 0;text-align:center}.detail-content-new .Page .detail-content-left .pagination li{border-radius:2px;color:#666;display:inline-block;font-size:14px;height:30px;line-height:30px;margin:0 6px;overflow:hidden;text-align:center}.detail-content-new .Page .detail-content-left .pagination li.disabled,.detail-content-new .Page .detail-content-left .pagination li.disabled:hover{color:#333;cursor:default;font-size:12px;padding:0}.detail-content-new .Page .detail-content-left .pagination li:last-child.last.disabled{color:#999;font-size:12px}.detail-content-new .Page .detail-content-left .pagination li a{background:#f3f4f5;color:#666;display:block;height:30px;line-height:30px;padding:0;text-align:center;width:30px}.detail-content-new .Page .detail-content-left .pagination li a:hover{background:#edeeef;color:#333;font-size:14px}.detail-content-new .Page .detail-content-left .pagination li.active a{color:#333;font-size:14px}.detail-content-new .Page .detail-content-left .pagination li.active b{background:#4973ee;color:#fff;display:block;font-weight:400;line-height:30px;padding:0;text-align:center;width:30px}.detail-content-new .Page .detail-content-left .pagination li.first a,.detail-content-new .Page .detail-content-left .pagination li.first_page a,.detail-content-new .Page .detail-content-left .pagination li.last a,.detail-content-new .Page .detail-content-left .pagination li.last_page a,.detail-content-new .Page .detail-content-left .pagination li.next a,.detail-content-new .Page .detail-content-left .pagination li.prev a{text-align:center;width:30px}.detail-content-new .Page .detail-content-left .pagination li.next:hover a,.detail-content-new .Page .detail-content-left .pagination li.prev:hover a{font-size:14px}.detail-content-new .Page .detail-content-left .pagination li:last-child.last.noLink{background:0;border-color:transparent;margin:0}.detail-content-new .Page .detail-content-left .pagination li.prev a{background:#f3f4f5;font-family:iconblog;font-size:20px;height:30px;width:30px}.detail-content-new .Page .detail-content-left .pagination li.prev a:before{content:""}.detail-content-new .Page .detail-content-left .pagination li.prev a:hover{background:#edeeef;font-size:20px}.detail-content-new .Page .detail-content-left .pagination li.next a{background:#f3f4f5;font-family:iconblog;font-size:20px;height:30px;width:30px}.detail-content-new .Page .detail-content-left .pagination li.next a:before{content:""}.detail-content-new .Page .detail-content-left .pagination li.next a:hover{background:#edeeef;font-size:20px}.detail-content-new .Page .detail-content-left .pagination li.first,.detail-content-new .Page .detail-content-left .pagination li.last{margin:0 2px}.detail-content-new .Page .detail-content-left .pagination li.first a,.detail-content-new .Page .detail-content-left .pagination li.last a{background:0;width:auto}.detail-content-new .Page .detail-content-left .recommend-about li{border-bottom:1px solid #f5f5f5;list-style:none;padding:17px 0 16px;position:relative}.detail-content-new .Page .detail-content-left .recommend-about li .list-subjuct{background:#e9f1ff;border-radius:16px;bottom:17px;box-sizing:border-box;display:none;height:22px;line-height:22px;max-width:250px;overflow:hidden;padding:0 13px;position:absolute;right:0;text-overflow:ellipsis;white-space:nowrap;z-index:2}.detail-content-new .Page .detail-content-left .recommend-about li .list-subjuct .fontsizeIcon{color:#3e71f6;font-size:14px}.detail-content-new .Page .detail-content-left .recommend-about li .list-subjuct span{color:#3e71f6;font-family:PingFang SC;font-size:12px;font-weight:500}.detail-content-new .Page .detail-content-left .recommend-about li:last-child{border-bottom:none}.detail-content-new .Page .detail-content-left .recommend-about li a,.detail-content-new .Page .detail-content-left .recommend-about li:hover .list-subjuct{display:block}.detail-content-new .Page .detail-content-left .recommend-about li .pic{background:#f7f7f8;float:right;height:45px;line-height:45px;margin-left:15px;margin-top:6px;position:relative;text-align:center;width:74px}.detail-content-new .Page .detail-content-left .recommend-about li .pic img{border-radius:2px;bottom:0;left:0;margin:auto;max-height:45px;max-width:74px;position:absolute;right:0;top:0}.detail-content-new .Page .detail-content-left .recommend-about li .pic span{background:rgba(0,0,0,.4);border-radius:1px;bottom:4px;color:#f5f5f5;font-size:12px;height:16px;line-height:20px;position:absolute;right:4px;text-align:center;width:25px}.detail-content-new .Page .detail-content-left .recommend-about li .tit{color:#17233f;font-size:18px;font-weight:700;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.detail-content-new .Page .detail-content-left .recommend-about li .tit em{color:#cd4b50;font-style:normal}.detail-content-new .Page .detail-content-left .recommend-about li .tit:hover{color:#3e71f6}.detail-content-new .Page .detail-content-left .recommend-about li .tit:hover em{color:#cd4b50}.detail-content-new .Page .detail-content-left .recommend-about li p{color:#585858;margin-top:5px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.detail-content-new .Page .detail-content-left .recommend-about li p em{color:#cd4b50;font-style:normal}.detail-content-new .Page .detail-content-left .recommend-cloumn li{border-bottom:1px solid #f5f5f5;list-style:none;padding:25px 0}.detail-content-new .Page .detail-content-left .recommend-cloumn li:last-child{border-bottom:none}.detail-content-new .Page .detail-content-left .recommend-cloumn li dl dt{float:left;height:116px;margin-right:10px;width:213px}.detail-content-new .Page .detail-content-left .recommend-cloumn li dl dt img{height:116px;width:213px}.detail-content-new .Page .detail-content-left .recommend-cloumn li dl dd{float:left;width:580px}.detail-content-new .Page .detail-content-left .recommend-cloumn li dl dd h3{font-weight:400;line-height:1;margin:5px 0 10px}.detail-content-new .Page .detail-content-left .recommend-cloumn li dl dd h3:hover .cloumn-subscribe{display:block}.detail-content-new .Page .detail-content-left .recommend-cloumn li dl dd h3 .title{display:inline-block;max-width:455px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.detail-content-new .Page .detail-content-left .recommend-cloumn li dl dd h3 .title:hover{color:#3e71f6}.detail-content-new .Page .detail-content-left .recommend-cloumn li dl dd h3 .cloumn-subscribe{color:#3e71f6;display:none;float:right;font-size:12px}.detail-content-new .Page .detail-content-left .recommend-cloumn li dl dd .dec{color:#9399a6;line-height:1;margin-bottom:17px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.detail-content-new .Page .detail-content-left .recommend-cloumn li dl dd .mess{color:#9399a6;line-height:1;margin-bottom:20px}.detail-content-new .Page .detail-content-left .recommend-cloumn li dl dd .mess b{background:#9399a6;display:inline-block;height:14px;margin:0 6px;width:1px}.detail-content-new .Page .detail-content-left .recommend-cloumn li dl dd .price{line-height:1}.detail-content-new .Page .detail-content-left .recommend-cloumn li dl dd .price span{color:#17233f;padding-right:18px}.detail-content-new .Page .detail-content-left .recommend-cloumn li dl dd .price strong{color:#9399a6;font-weight:400}.detail-content-new .Page .detail-content-left .recommend-course{margin:20px 0 15px}.detail-content-new .Page .detail-content-left .recommend-course li{float:left;list-style:none;margin-left:21px;width:185px}.detail-content-new .Page .detail-content-left .recommend-course li:first-child{margin-left:0}.detail-content-new .Page .detail-content-left .recommend-course li:nth-child(5),.detail-content-new .Page .detail-content-left .recommend-course li:nth-child(6){display:none}.detail-content-new .Page .detail-content-left .recommend-course li .pic{height:112px;width:185px}.detail-content-new .Page .detail-content-left .recommend-course li .pic img{border-radius:5px;height:112px;width:185px}.detail-content-new .Page .detail-content-left .recommend-course li .main{padding-top:12px}.detail-content-new .Page .detail-content-left .recommend-course li .main h3{font-weight:400;line-height:1;margin-bottom:10px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.detail-content-new .Page .detail-content-left .recommend-course li .main h3 a{color:#17233f}.detail-content-new .Page .detail-content-left .recommend-course li .main h3 a:hover{color:#3e71f6}.detail-content-new .Page .detail-content-left .recommend-course li .main .num{color:#b4b8c1;line-height:1;margin-bottom:13px}.detail-content-new .Page .detail-content-left .recommend-course li .main .price{color:#17233f;font-size:12px;line-height:1}.detail-content-new .Page .detail-content-right{float:right;width:302px}.detail-content-new .Page .detail-content-right .common-spacing{padding:8px 20px 12px}.detail-content-new .Page .detail-content-right .common-sub-title{border-bottom:1px solid #f5f5f5;height:38px;line-height:38px}.detail-content-new .Page .detail-content-right .common-sub-title h2,.detail-content-new .Page .detail-content-right .common-sub-title strong{color:#333;display:inline-block;font-size:16px;max-width:215px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.detail-content-new .Page .detail-content-right .common-sub-title .more{color:#999}.detail-content-new .Page .detail-content-right .fix-table{box-sizing:border-box;position:fixed;top:100px;width:298px}.detail-content-new .Page .detail-content-right .user-intr{padding:25px 10px}.detail-content-new .Page .detail-content-right .user-intr .top .avatar .avatar-img{height:65px;margin:0 auto;position:relative;width:65px}.detail-content-new .Page .detail-content-right .user-intr .top .avatar .avatar-img img{border-radius:65px;height:65px;width:65px}.detail-content-new .Page .detail-content-right .user-intr .top .username{color:#333;font-size:16px;font-weight:700;line-height:1;padding:13px 0 8px;text-align:center}.detail-content-new .Page .detail-content-right .user-intr .top .username a{color:#333;display:inline-block;font-size:16px;height:22px;line-height:22px}.detail-content-new .Page .detail-content-right .user-intr .top .username a .blog-user{display:inline-block;height:22px;max-width:185px;overflow:hidden;text-overflow:ellipsis;vertical-align:bottom;white-space:nowrap;word-break:break-all}.detail-content-new .Page .detail-content-right .user-intr .top .username .icon{display:inline-block;margin-left:-2px;position:relative;vertical-align:middle}.detail-content-new .Page .detail-content-right .user-intr .top .username .icon ul{display:inline-block}.detail-content-new .Page .detail-content-right .user-intr .top .username .icon ul li{float:left;height:18px;list-style:none;margin-left:5px;width:16px}.detail-content-new .Page .detail-content-right .user-intr .top .username .icon ul li a{background:url("https://s2.51cto.com/images/100/blog/sprites/sprites_identity.png") no-repeat;background-size:16px auto;display:inline-block;height:18px;width:16px}.webp .detail-content-new .Page .detail-content-right .user-intr .top .username .icon ul li a{background-image:url("https://s2.51cto.com/images/100/blog/sprites/sprites_identity.png?x-oss-process=image/format,webp")}.detail-content-new .Page .detail-content-right .user-intr .top .username .icon ul li a.qybz{background-position:0 -80px}.detail-content-new .Page .detail-content-right .user-intr .top .username .icon ul li a.zj{background-position:0 -60px}.detail-content-new .Page .detail-content-right .user-intr .top .username .icon ul li a.bkzx{background-position:0 0}.detail-content-new .Page .detail-content-right .user-intr .top .username .icon ul li a.tjzx{background-position:0 -40px}.detail-content-new .Page .detail-content-right .user-intr .top .username .icon ul li a.js{background-position:0 -20px}.detail-content-new .Page .detail-content-right .user-intr .top .username .icon ul li a.zjbz{background-position:0 -108px;background-size:14px auto}.detail-content-new .Page .detail-content-right .user-intr .top .username .icon ul li a.top_hr{background-position:0 -88px;background-size:14px auto}.detail-content-new .Page .detail-content-right .user-intr .top .username .icon ul li a.mrzx{background-position:-6px -257px;background-size:28px auto}.detail-content-new .Page .detail-content-right .user-intr .bottom{margin-bottom:8px}.detail-content-new .Page .detail-content-right .user-intr .bottom.loading{background:url("https://s2.51cto.com/images/100/blog/old/loading1.gif") no-repeat center 36px}.detail-content-new .Page .detail-content-right .user-intr .bottom .lines{background:#f5f5f5;height:1px;margin:0 10px}.detail-content-new .Page .detail-content-right .user-intr .bottom .num-name{text-align:center}.detail-content-new .Page .detail-content-right .user-intr .bottom .num-name:first-child ul{padding-top:0}.detail-content-new .Page .detail-content-right .user-intr .bottom .num-name:last-child ul{padding-top:11px}.detail-content-new .Page .detail-content-right .user-intr .bottom .num-name ul{display:inline-block;line-height:1;padding:18px 0 6px;width:100%}.detail-content-new .Page .detail-content-right .user-intr .bottom .num-name ul li{float:left;font-size:14px;list-style:none;text-align:center;width:25%}.detail-content-new .Page .detail-content-right .user-intr .bottom .num-name ul li .num{color:#17233f;font-size:18px;padding-bottom:8px}.detail-content-new .Page .detail-content-right .user-intr .bottom .num-name ul li .num a{color:#17233f;font-size:18px}.detail-content-new .Page .detail-content-right .user-intr .bottom .num-name ul li .num a:hover{color:#3e71f6}.detail-content-new .Page .detail-content-right .user-intr .bottom .num-name ul li .num span{font-size:17px}.detail-content-new .Page .detail-content-right .user-intr .bottom .num-name ul li .label-name{color:#9399a6;font-size:12px;line-height:1}.detail-content-new .Page .detail-content-right .user-intr .bottom .num-name ul li .label-name a{color:#9399a6}.detail-content-new .Page .detail-content-right .user-intr .bottom .num-name ul li .label-name a:hover{color:#3e71f6}.detail-content-new .Page .detail-content-right .user-intr .operating{margin-top:8px;padding-left:16px}.detail-content-new .Page .detail-content-right .user-intr .operating.operating2 button{display:block;float:none;margin:0 auto}.detail-content-new .Page .detail-content-right .user-intr .operating button{background-color:#fff;background-image:none!important;border:1px solid #789bf9;border-radius:0;border-radius:2px;cursor:pointer;float:left;height:35px;line-height:35px;padding:0;width:110px}.detail-content-new .Page .detail-content-right .user-intr .operating button:hover{border:1px solid #3d62f5}.detail-content-new .Page .detail-content-right .user-intr .operating button:hover a,.detail-content-new .Page .detail-content-right .user-intr .operating button:hover a i{color:#3d62f5}.detail-content-new .Page .detail-content-right .user-intr .operating button a{color:#3e71f6;display:inline-block;font-size:14px;height:35px;line-height:35px}.detail-content-new .Page .detail-content-right .user-intr .operating button a i{float:left;font-size:18px;margin-right:5px}.detail-content-new .Page .detail-content-right .user-intr .operating .checkFollow{background:#3e71f6;border:none;border-radius:0;border-radius:2px;box-sizing:border-box;color:#666;color:#fff;float:left;font-size:14px;height:35px;line-height:35px;margin:0 25px 0 0;text-align:center;width:110px}.detail-content-new .Page .detail-content-right .user-intr .operating .checkFollow.in,.detail-content-new .Page .detail-content-right .user-intr .operating .checkFollow.mutual{background:0;border:1px solid #789bf9;color:#3e71f6;padding-left:0}.detail-content-new .Page .detail-content-right .user-intr .operating .checkFollow.on{background:#3e71f6;font-family:iconblog;padding-left:30px;text-align:left}.detail-content-new .Page .detail-content-right .user-intr .operating .checkFollow.on:before{content:"";font-size:20px;vertical-align:bottom}.detail-content-new .Page .detail-content-right .user-intr .operating .checkFollow.on:hover{background:#3d62f5}.detail-content-new .Page .detail-content-right .user-intr .operating .checkFollow.off{background:#ddd;padding-left:0}.detail-content-new .Page .detail-content-right .blogger-ranking .rank-list{margin-bottom:10px}.detail-content-new .Page .detail-content-right .blogger-ranking .rank-list a{box-sizing:border-box;color:#6c7486;display:block;height:48px;line-height:48px;padding-left:25px;position:relative;width:100%}.detail-content-new .Page .detail-content-right .blogger-ranking .rank-list a:after{background:url("https://s2.51cto.com/images/100/blog/list/css_sprites_0913.png") no-repeat;content:"";height:90px;position:absolute;right:-5px;top:-20px;transform:scale(.45);width:90px}.webp .detail-content-new .Page .detail-content-right .blogger-ranking .rank-list a:after{background-image:url("https://s2.51cto.com/images/100/blog/list/css_sprites_0913.png?x-oss-process=image/format,webp")}.detail-content-new .Page .detail-content-right .blogger-ranking .rank-list a.new{background:url("https://s2.51cto.com/images/100/blog/list/blist1.png") no-repeat;background-size:100% 100%}.webp .detail-content-new .Page .detail-content-right .blogger-ranking .rank-list a.new{background-image:url("https://s2.51cto.com/images/100/blog/list/blist1.png?x-oss-process=image/format,webp")}.detail-content-new .Page .detail-content-right .blogger-ranking .rank-list a.new:after{background-position:-2px -2px}.detail-content-new .Page .detail-content-right .blogger-ranking .rank-list a.week{background:url("https://s2.51cto.com/images/100/blog/list/blist3.png") no-repeat;background-size:100% 100%}.webp .detail-content-new .Page .detail-content-right .blogger-ranking .rank-list a.week{background-image:url("https://s2.51cto.com/images/100/blog/list/blist3.png?x-oss-process=image/format,webp")}.detail-content-new .Page .detail-content-right .blogger-ranking .rank-list a.week:after{background-position:-96px -2px}.detail-content-new .Page .detail-content-right .blogger-ranking .rank-list a.default{background:url("https://s2.51cto.com/images/100/blog/list/blist2.png") no-repeat;background-size:100% 100%}.webp .detail-content-new .Page .detail-content-right .blogger-ranking .rank-list a.default{background-image:url("https://s2.51cto.com/images/100/blog/list/blist2.png?x-oss-process=image/format,webp")}.detail-content-new .Page .detail-content-right .blogger-ranking .rank-list a.default:after{background-position:-2px -96px}.detail-content-new .Page .detail-content-right .blogger-ranking .rank-list a b{font-weight:700;margin-left:5px}.detail-content-new .Page .detail-content-right .blogger-ranking .rank-list:last-child{margin-bottom:0}.detail-content-new .Page .detail-content-right .identify-list{padding:0 14px 5px}.detail-content-new .Page .detail-content-right .identify-list .item{padding-bottom:5px;text-align:center}.detail-content-new .Page .detail-content-right .identify-list .item span{box-sizing:border-box;display:inline-block;height:25px;line-height:25px;max-width:100%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.detail-content-new .Page .detail-content-right .identify-list .item span i{float:left;height:22px;margin-right:4px;width:20px}.detail-content-new .Page .detail-content-right .identify-list .item.item1 span i{background:url("https://s2.51cto.com/images/100/blog/sprites/sprites_detail_new.png") no-repeat;background-position:-5px -5px;background-size:90px auto}.webp .detail-content-new .Page .detail-content-right .identify-list .item.item1 span i{background-image:url("https://s2.51cto.com/images/100/blog/sprites/sprites_detail_new.png?x-oss-process=image/format,webp")}.detail-content-new .Page .detail-content-right .identify-list .item.item2 span i{background:url("https://s2.51cto.com/images/100/blog/sprites/sprites_detail_new.png") no-repeat;background-position:-35px -5px;background-size:90px auto}.webp .detail-content-new .Page .detail-content-right .identify-list .item.item2 span i{background-image:url("https://s2.51cto.com/images/100/blog/sprites/sprites_detail_new.png?x-oss-process=image/format,webp")}.detail-content-new .Page .detail-content-right .identify-list .item.item3 span i{background:url("https://s2.51cto.com/images/100/blog/sprites/sprites_detail_new.png") no-repeat;background-position:-65px -5px;background-size:90px auto}.webp .detail-content-new .Page .detail-content-right .identify-list .item.item3 span i{background-image:url("https://s2.51cto.com/images/100/blog/sprites/sprites_detail_new.png?x-oss-process=image/format,webp")}.detail-content-new .Page .detail-content-right .identify-list .item.item4 span i{background:url("https://s2.51cto.com/images/100/blog/sprites/sprites_detail_new.png") no-repeat;background-position:-5px -37px;background-size:90px auto}.webp .detail-content-new .Page .detail-content-right .identify-list .item.item4 span i{background-image:url("https://s2.51cto.com/images/100/blog/sprites/sprites_detail_new.png?x-oss-process=image/format,webp")}.detail-content-new .Page .detail-content-right .medal-list{display:flex;flex-wrap:wrap;margin-bottom:6px;padding:0 11px}.detail-content-new .Page .detail-content-right .medal-list .item{cursor:pointer;display:flex;height:42.5px;justify-content:center;margin-bottom:9px;width:52px}.detail-content-new .Page .detail-content-right .medal-list .item img{height:40.5px;width:36px}.detail-content-new .Page .detail-content-right .common-list{padding:7px 0 3px}.detail-content-new .Page .detail-content-right .common-list.common-list-dot li .title a,.detail-content-new .Page .detail-content-right .common-list.common-list-dot li a.title{padding-left:10px}.detail-content-new .Page .detail-content-right .common-list.common-list-dot li .title a:before,.detail-content-new .Page .detail-content-right .common-list.common-list-dot li a.title:before{background:#b9bdc5;border-radius:4px;content:"";display:inline-block;height:4px;left:0;position:absolute;top:10px;width:4px}.detail-content-new .Page .detail-content-right .common-list#classification-list li a:hover span{color:#3e71f6}.detail-content-new .Page .detail-content-right .common-list#classification-list li span:first-child{display:inline-block;max-width:206px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.detail-content-new .Page .detail-content-right .common-list#classification-list li span:last-child{color:#5c6578;float:right}.detail-content-new .Page .detail-content-right .common-list li{list-style:none;padding:5px 0}.detail-content-new .Page .detail-content-right .common-list li:last-child{padding-bottom:0}.detail-content-new .Page .detail-content-right .common-list li a{color:#17233f;display:block;font-size:14px;font-weight:400;overflow:hidden;position:relative;text-overflow:ellipsis;white-space:nowrap}.detail-content-new .Page .detail-content-right .common-list li a:hover{color:#3e71f6}.detail-content-new .Page .detail-content-right .common-list li .dec{color:#9399a6;font-size:12px;overflow:hidden;padding-left:10px;text-overflow:ellipsis;white-space:nowrap}.detail-content-new .Page .detail-content-right .common-list li .dec a{color:#9399a6;font-size:12px}.detail-content-new .Page .detail-content-right .common-list-lines{background:#f5f5f5;height:1px;margin-bottom:15px;margin-top:15px}.detail-content-new .Page .detail-content-right .years{color:#17233f}.detail-content-new .Page .detail-content-right .years a{color:#17233f;display:inline-block}.detail-content-new .Page .detail-content-right .years a:hover{color:#3e71f6}.detail-content-new .Page .detail-content-right .months{margin-top:10px}.detail-content-new .Page .detail-content-right .months a{border:1px solid #f0f0f0;display:block;float:left;height:55px;margin:0 20px 10px 0;text-align:center;width:48px}.detail-content-new .Page .detail-content-right .months a:hover span,.detail-content-new .Page .detail-content-right .months a:hover strong{color:#3e71f6}.detail-content-new .Page .detail-content-right .months a:nth-child(4n){margin-right:0}.detail-content-new .Page .detail-content-right .months a span{color:#9399a6;display:block;margin-bottom:2px;padding:1px 0;position:relative}.detail-content-new .Page .detail-content-right .months a span:after{background:#f5f5f5;bottom:0;content:"";height:1px;left:50%;margin-left:-12px;position:absolute;width:25px}.detail-content-new .Page .detail-content-right .months a strong{display:block;font-weight:400}.detail-content-new .Page .detail-content-right .nowYear{margin-top:15px}.detail-content-new .Page .detail-content-right .otherYear .years a{float:left;padding:3px 0;width:50%}.detail-content-new .Page .detail-content-right .directory{max-height:402px;overflow-x:hidden}.detail-content-new .Page .detail-content-right .directory::-webkit-scrollbar{display:none}.detail-content-new .Page .detail-content-right .directory-list{border-left:2px solid #f8f8f9;margin-bottom:20px;margin-top:12px;padding-left:12px}.detail-content-new .Page .detail-content-right .directory-list li{list-style:none}.detail-content-new .Page .detail-content-right .directory-list li:first-child{margin-bottom:7px}.detail-content-new .Page .detail-content-right .directory-list li span{cursor:pointer;display:block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.detail-content-new .Page .detail-content-right .directory-list li:hover span{color:#3e71f6}.detail-content-new .Page .detail-content-right .directory-list li.lv1{margin-bottom:7px}.detail-content-new .Page .detail-content-right .directory-list li.lv1.on .title span{color:#3e71f6}.detail-content-new .Page .detail-content-right .directory-list li.lv1.on .title:before{background:#3e71f6;content:"";display:inline-block;height:18px;left:-14px;position:absolute;top:3px;width:2px}.detail-content-new .Page .detail-content-right .directory-list li.lv1 .title{font-weight:400;position:relative}.detail-content-new .Page .detail-content-right .directory-list li.lv2,.detail-content-new .Page .detail-content-right .directory-list li.lv3{margin-bottom:5px}.detail-content-new .Page .detail-content-right .directory-list li.lv2.on .title span,.detail-content-new .Page .detail-content-right .directory-list li.lv3.on .title span{color:#3e71f6}.detail-content-new .Page .detail-content-right .directory-list li.lv2 .title,.detail-content-new .Page .detail-content-right .directory-list li.lv3 .title{font-size:12px;font-weight:400;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.detail-content-new .Page .detail-content-right .directory-list li.lv2 .title:before,.detail-content-new .Page .detail-content-right .directory-list li.lv3 .title:before{background:#b9bdc5;border-radius:4px;content:"";float:left;height:4px;margin:8px 6px 0 0;width:4px}.detail-content-new .Page .detail-content-right .directory-list li.lv2.lv3,.detail-content-new .Page .detail-content-right .directory-list li.lv3.lv3{margin-left:12px}.detail-content-new .Page .detail-content-right .label-list .tag-text{color:#9399a6;display:inline;font-size:13px;line-height:35px;margin-right:15px;word-break:break-all}.detail-content-new .Page .detail-content-right .label-list .tag-text:hover{color:#7d828c}.detail-content-new .Page .detail-content-right .label-list .tag-text:nth-child(3n-2){color:#b6c2bb}.detail-content-new .Page .detail-content-right .label-list .tag-text:nth-child(3n-2):hover{color:#9ea8a2}.detail-content-new .Page .detail-content-right .label-list .tag-text:nth-child(3n-1){color:#e0d6d1}.detail-content-new .Page .detail-content-right .label-list .tag-text:nth-child(3n-1):hover{color:#c7beb9}.detail-content-new .Page .detail-content-directory{display:none;position:fixed;width:302px}.detail-content-new .Page .detail-content-directory .common-spacing{padding:8px 20px 12px}.detail-content-new .Page .detail-content-directory .common-sub-title{border-bottom:1px solid #efeff1;height:38px;line-height:38px}.detail-content-new .Page .detail-content-directory .common-sub-title h2,.detail-content-new .Page .detail-content-directory .common-sub-title strong{color:#333;display:inline-block;font-size:16px;max-width:215px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.detail-content-new .Page .detail-content-directory .common-sub-title .iconblog{color:#9399a6;cursor:pointer;float:right;font-size:12px;font-weight:700}.detail-content-new .Page .detail-content-directory .common-sub-title .iconblog:hover{color:#313d54}.detail-content-new .Page .common-content-directory.fix-table{box-sizing:border-box;position:fixed;top:100px;width:298px}.detail-content-new .Page .common-content-directory .directory{max-height:402px;overflow-x:hidden}.detail-content-new .Page .common-content-directory .directory::-webkit-scrollbar{display:none}.detail-content-new .Page .common-content-directory .directory-list{border-left:2px solid #f8f8f9;margin-bottom:20px;margin-top:12px;padding-left:12px}.detail-content-new .Page .common-content-directory .directory-list li{list-style:none}.detail-content-new .Page .common-content-directory .directory-list li:first-child{margin-bottom:7px}.detail-content-new .Page .common-content-directory .directory-list li span{cursor:pointer;display:block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.detail-content-new .Page .common-content-directory .directory-list li:hover span{color:#3e71f6}.detail-content-new .Page .common-content-directory .directory-list li.lv1{margin-bottom:7px}.detail-content-new .Page .common-content-directory .directory-list li.lv1.on .title span{color:#3e71f6}.detail-content-new .Page .common-content-directory .directory-list li.lv1.on .title:before{background:#3e71f6;content:"";display:inline-block;height:18px;left:-14px;position:absolute;top:3px;width:2px}.detail-content-new .Page .common-content-directory .directory-list li.lv1 .title{font-weight:400;position:relative}.detail-content-new .Page .common-content-directory .directory-list li.lv2,.detail-content-new .Page .common-content-directory .directory-list li.lv3,.detail-content-new .Page .common-content-directory .directory-list li.lv4{margin-bottom:5px}.detail-content-new .Page .common-content-directory .directory-list li.lv2.on .title span,.detail-content-new .Page .common-content-directory .directory-list li.lv3.on .title span,.detail-content-new .Page .common-content-directory .directory-list li.lv4.on .title span{color:#3e71f6}.detail-content-new .Page .common-content-directory .directory-list li.lv2 .title,.detail-content-new .Page .common-content-directory .directory-list li.lv3 .title,.detail-content-new .Page .common-content-directory .directory-list li.lv4 .title{font-size:12px;font-weight:400;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.detail-content-new .Page .common-content-directory .directory-list li.lv2 .title:before,.detail-content-new .Page .common-content-directory .directory-list li.lv3 .title:before,.detail-content-new .Page .common-content-directory .directory-list li.lv4 .title:before{background:#b9bdc5;border-radius:4px;content:"";float:left;height:4px;margin:8px 6px 0 0;width:4px}.detail-content-new .Page .common-content-directory .directory-list li.lv2.lv3,.detail-content-new .Page .common-content-directory .directory-list li.lv3.lv3,.detail-content-new .Page .common-content-directory .directory-list li.lv4.lv3{margin-left:12px}.detail-content-new .Page .common-content-directory .directory-list li.lv2.lv4,.detail-content-new .Page .common-content-directory .directory-list li.lv3.lv4,.detail-content-new .Page .common-content-directory .directory-list li.lv4.lv4{margin-left:24px}.action-aside{left:50%;margin:-265px 0 0 -703px;position:fixed;top:50%;z-index:999}.action-aside.action-aside-right{bottom:200px;left:auto;margin:0;right:30px;top:auto}.action-aside ul li{list-style:none;margin-bottom:15px;position:relative}.action-aside ul li:last-child{margin-bottom:0}.action-aside ul li.share:hover .bdsharebuttonbox{display:block}.action-aside ul li.scrollTop{display:none}.action-aside ul li strong{display:inline-block;font-weight:400;position:relative;text-align:center;width:80px}.action-aside ul li strong:hover a{box-shadow:0 8px 16px 0 rgba(23,35,63,.12)}.action-aside ul li strong.is-praise a i{background:url("https://s2.51cto.com/images/100/blog/old/zan1.png") no-repeat top;background-size:47px 47px;display:inline-block;height:47px;width:47px}.webp .action-aside ul li strong.is-praise a i{background-image:url("https://s2.51cto.com/images/100/blog/old/zan1.png?x-oss-process=image/format,webp")}.action-aside ul li strong.is-praise.on a i{background:url("https://s2.51cto.com/images/100/blog/old/zan2.png") no-repeat top;background-size:47px 47px}.webp .action-aside ul li strong.is-praise.on a i{background-image:url("https://s2.51cto.com/images/100/blog/old/zan2.png?x-oss-process=image/format,webp")}.action-aside ul li strong.is-praise.no-praise a i,.action-aside ul li strong.is-praise.on.no-praise a i{background:url("https://s2.51cto.com/images/100/blog/old/zan.gif") no-repeat top;background-size:47px 47px}.action-aside ul li strong.favorites-opt a i{background:url("https://s2.51cto.com/images/100/blog/old/ping1.png") no-repeat top;background-size:47px 47px;display:inline-block;height:47px;width:47px}.webp .action-aside ul li strong.favorites-opt a i{background-image:url("https://s2.51cto.com/images/100/blog/old/ping1.png?x-oss-process=image/format,webp")}.action-aside ul li strong.favorites-opt.on a i{background:url("https://s2.51cto.com/images/100/blog/old/ping2.png") no-repeat top;background-size:47px 47px}.webp .action-aside ul li strong.favorites-opt.on a i{background-image:url("https://s2.51cto.com/images/100/blog/old/ping2.png?x-oss-process=image/format,webp")}.action-aside ul li strong.favorites-opt.no-favorites a i,.action-aside ul li strong.favorites-opt.on.no-favorites a i{background:url("https://s2.51cto.com/images/100/blog/old/ping.gif") no-repeat top;background-size:47px 47px}.action-aside ul li strong.sign{cursor:pointer}.action-aside ul li strong.sign a{position:relative}.action-aside ul li strong.sign a .dot{background:#e90d31;border-radius:50%;content:"";display:inline-block;height:5px;position:absolute;right:13px;top:10px;width:5px}.action-aside ul li strong.sign a i{font-size:24px}.action-aside ul li strong a{background:#fff;border:1px solid #f4f4f4;border-radius:47px;box-shadow:0 8px 16px 0 rgba(23,35,63,.04);display:block;height:47px;line-height:47px;margin:0 auto 5px;width:47px}.action-aside ul li strong a i{color:#8a92a5}.action-aside ul li strong a i.blogshang,.action-aside ul li strong a i.blogzan{font-size:19px}.action-aside ul li strong a i.blogshou{font-size:21px}.action-aside ul li strong a i.blogpinglun{font-size:19px}.action-aside ul li strong a i.blogfen{font-size:23px}.action-aside ul li strong a i.blogzhi{font-size:18px}.action-aside ul li strong a i.bloggengduo{font-size:24px}.action-aside ul li strong span{color:#979da9;line-height:1}.action-aside ul li strong span b{font-weight:400}.action-aside ul li strong.on a i{color:#3e71f6}.action-aside ul li strong .new{background:#e31436;border-radius:10px 10px 10px 2px;color:#fff;display:inline-block;font-size:12px;font-style:normal;line-height:1;padding:2px 5px;position:absolute;right:-7px;top:-4px}.bdsharebuttonbox{display:none;left:75px;padding-top:20px;position:absolute;top:-89px;z-index:99}.bdsharebuttonbox .ins{background:#fff;border-radius:2px;box-shadow:0 8px 16px 0 hsla(0,0%,40%,.1);padding:10px 0 8px;position:absolute;text-align:center;width:90px}.bdsharebuttonbox .ins a{background:0;color:#2e3d56;display:inline-block;float:none;font-size:12px;height:32px;line-height:32px;margin:0 0 2px;padding-left:0;width:55px}.bdsharebuttonbox .ins a:hover,.bdsharebuttonbox .ins a:hover i{color:#3e71f6}.bdsharebuttonbox .ins a i{color:#818797;float:left;margin-right:8px}.bdsharebuttonbox .ins a i.blogfenxiangweibo{font-size:19px}.bdsharebuttonbox .ins a i.blogfenxiangqq{font-size:18px}.bdsharebuttonbox .ins a i.blogfenxiangweixin{font-size:20px}.bdsharebuttonbox .ins img{height:59px;width:59px}.Footer{margin-top:60px!important}.footer{background-color:#f7f8f9;color:#9fa3a7;font-size:12px;padding:36px 0;text-align:center}.set-right{-webkit-animation:right-to-left .3s linear;animation:right-to-left .3s linear;right:0;z-index:9}.reset-right,.set-right{float:none!important;position:absolute;top:0}.reset-right{-webkit-animation:left-to-right .3s linear;animation:left-to-right .3s linear;right:326px}.arrowing{animation-duration:1s;-webkit-animation-duration:1s;animation-iteration-count:infinite;-webkit-animation-iteration-count:infinite;animation-name:arrowing;-webkit-animation-name:arrowing}@keyframes right-to-left{0%{right:326px}to{right:0}}@-webkit-keyframes right-to-left{0%{right:326px}to{right:0}}@keyframes left-to-right{0%{right:0}to{right:326px}}@-webkit-keyframes left-to-right{0%{right:0}to{right:326px}}@keyframes arrowing{0%{transform:scale(1)}50%{transform:scale(.9)}to{transform:scale(1)}}@-webkit-keyframes arrowing{0%{-webkit-transform:scale(1)}50%{-webkit-transform:scale(.9)}to{-webkit-transform:scale(1)}}*{-webkit-font-smoothing:antialiased;font-family:-apple-system,Helvetica Neue,Helvetica,Arial,PingFang SC,Hiragino Sans GB,WenQuanYi Micro Hei,Microsoft Yahei,sans-serif;margin:0;padding:0}a{color:#333;text-decoration:none}textarea{resize:none}button,input,input[type=button]{outline:0}button,input[type=button]{background-color:#00baf2;border:none;color:#fff;cursor:pointer;line-height:30px;padding:0 20px}button:hover,input[type=button]:hover{opacity:.9}img{border:none}body{color:#333;font-size:14px;line-height:1.75;text-align:left}.disabled{background:#999}.del{text-decoration:line-through}.clear{height:0;overflow:hidden;width:0}.clear,.clearfix{clear:both}.clearfix:after{clear:both;content:"";display:block}.Left,.fl{float:left}.Right,.fr{float:right}.tl{text-align:left}.tc{text-align:center}.tr{text-align:right}.fb{font-weight:700}.bluebg{background:#00baf2}.blue{color:#00baf2}.redbg{background:#ff4a56}.red{color:#ff4a56}.red:hover{color:#950b11}.Mask,.mask{background:rgba(0,0,0,.8);display:none;height:100%;left:0;position:fixed;top:0;width:100%;z-index:9999}label{margin-bottom:0!important}.blue-btn{background:#4285f4;border:1px solid #4285f4;color:#fff;cursor:pointer}.disabled-btn{background:#ddd;border:1px solid #ddd;color:#fff}.blue-btn:hover{background:#3c78dc;border:1px solid #3c78dc;color:#fff}.gray-btn{background:#fff;border:1px solid #ccc;color:#333;cursor:pointer}.gray-btn:hover{background:#e6e6e6;color:#000}.editor-side-new{font-size:16px;word-break:break-all}.editor-side-new blockquote{background:#f2f5f9;border-left:.2rem solid #4285f4;color:#819198;margin:1rem 0;padding:.8rem 1.2rem}.editor-side-new blockquote h1:last-child,.editor-side-new blockquote h2:last-child,.editor-side-new blockquote h3:last-child,.editor-side-new blockquote h4:last-child,.editor-side-new blockquote h5:last-child,.editor-side-new blockquote h6:last-child,.editor-side-new blockquote li:last-child,.editor-side-new blockquote ol:last-child,.editor-side-new blockquote p:last-child,.editor-side-new blockquote ul:last-child{margin-bottom:0}.editor-side-new blockquote p{font-size:16px;font-weight:400;line-height:1.7}@media screen and (max-width:1440px){.body_padding{padding-bottom:115px}.action-aside{z-index:999}.action-aside ul li{display:inline-block;margin:0 20px;width:80px}.action-aside ul li .bdsharebuttonbox{display:none;left:73px;padding-top:20px;position:absolute;top:-134px;z-index:99}.action-aside ul li strong{width:80px}.action-aside ul li strong span{font-size:12px}.action-aside ul li strong.is-praise a i{background:url("https://s2.51cto.com/images/100/blog/old/zan1.png") no-repeat 50%;background-size:41px 41px;display:inline-block;height:35px;width:35px}.webp .action-aside ul li strong.is-praise a i{background-image:url("https://s2.51cto.com/images/100/blog/old/zan1.png?x-oss-process=image/format,webp")}.action-aside ul li strong.is-praise.on a i{background:url("https://s2.51cto.com/images/100/blog/old/zan2.png") no-repeat 50%;background-size:41px 41px}.webp .action-aside ul li strong.is-praise.on a i{background-image:url("https://s2.51cto.com/images/100/blog/old/zan2.png?x-oss-process=image/format,webp")}.action-aside ul li strong.is-praise.no-praise a i,.action-aside ul li strong.is-praise.on.no-praise a i{background:url("https://s2.51cto.com/images/100/blog/old/zan.gif") no-repeat 50%;background-size:41px 41px}.action-aside ul li strong.favorites-opt a i{background:url("https://s2.51cto.com/images/100/blog/old/ping1.png") no-repeat 50%;background-size:41px 41px;display:inline-block;height:35px;width:35px}.webp .action-aside ul li strong.favorites-opt a i{background-image:url("https://s2.51cto.com/images/100/blog/old/ping1.png?x-oss-process=image/format,webp")}.action-aside ul li strong.favorites-opt.on a i{background:url("https://s2.51cto.com/images/100/blog/old/ping2.png") no-repeat 50%;background-size:41px 41px}.webp .action-aside ul li strong.favorites-opt.on a i{background-image:url("https://s2.51cto.com/images/100/blog/old/ping2.png?x-oss-process=image/format,webp")}.action-aside ul li strong.favorites-opt.no-favorites a i,.action-aside ul li strong.favorites-opt.on.no-favorites a i{background:url("https://s2.51cto.com/images/100/blog/old/ping.gif") no-repeat 50%;background-size:41px 41px}.action-aside ul li strong a{border-radius:35px;height:35px;line-height:35px;margin-bottom:0;width:35px}.action-aside ul li strong a i{color:#8a92a5}.action-aside ul li strong a i.blogshang,.action-aside ul li strong a i.blogzan{font-size:15px}.action-aside ul li strong a i.blogshou{font-size:17px}.action-aside ul li strong a i.blogpinglun{font-size:15px}.action-aside ul li strong a i.blogfen{font-size:19px}.action-aside ul li strong a i.blogzhi{font-size:13px}.action-aside ul li strong a i.bloggengduo{font-size:18px}.action-aside ul li strong.sign{cursor:pointer}.action-aside ul li strong.sign a{position:relative}.action-aside ul li strong.sign a .dot{background:#e90d31;border-radius:50%;content:"";display:inline-block;height:4px;position:absolute;right:9px;top:8px;width:4px}.action-aside ul li strong.sign a i{font-size:18px}.action-aside ul li strong .new{transform:scale(.85);-webkit-transform:scale(.85);-moz-transform:scale(.85)}.action-aside-left{bottom:0;left:0;margin:0;position:fixed;text-align:center;top:auto;width:100%}.action-aside-left .inner{margin:0 auto;width:1200px}.action-aside-left .inner ul{background:#fff;box-shadow:0 0 14px -2px #efefef;padding:10px 0;width:874px}.action-aside.action-aside-right{z-index:999}}@media screen and (max-width:1199px){.Page{width:1000px}.detail-content-new .fixtitle h3{width:720px}.detail-content-new .Page .detail-content-left{width:674px}.detail-content-new .Page .detail-content-left .main-content{max-width:none}.detail-content-new .Page .detail-content-left .comment-textarea .textarea-box{width:549px}.detail-content-new .Page .detail-content-left .comment-List-box .comment-List .comment-detail{width:554px}.detail-content-new .Page .detail-content-left .recommend-cloumn li dl dd{float:left;width:380px}.detail-content-new .Page .detail-content-left .recommend-course{display:none}.action-aside-left .inner{width:1000px}.action-aside-left .inner ul{width:674px}.action-aside-left .inner ul li{margin:0 14px}}@media screen and (min-width:1200px)and (max-width:1580px){.Page{width:1200px}}@media screen and (min-width:1581px)and (max-width:1767px){.Page{width:1390px}.detail-content-new .Page .detail-content-left,.detail-content-new .fixtitle h3{width:1064px}.detail-content-new .Page .detail-content-left .main-content{max-width:none}.detail-content-new .Page .detail-content-left .comment-textarea .textarea-box{width:939px}.detail-content-new .Page .detail-content-left .comment-List-box .comment-List .comment-detail{width:944px}.detail-content-new .Page .detail-content-left .recommend-cloumn li dl dd{float:left;width:771px}.detail-content-new .Page .detail-content-left .recommend-course li{margin-left:27px;width:177px}.detail-content-new .Page .detail-content-left .recommend-course li:nth-child(5){display:block}.detail-content-new .Page .detail-content-left .recommend-course li .pic,.detail-content-new .Page .detail-content-left .recommend-course li .pic img{height:107px;width:177px}.action-aside{margin:-300px 0 0 -799px}}@media screen and (min-width:1768px){.Page{width:1580px}.detail-content-new .Page .detail-content-left,.detail-content-new .fixtitle h3{width:1254px}.detail-content-new .Page .detail-content-left .main-content{max-width:none}.detail-content-new .Page .detail-content-left .comment-textarea .textarea-box{width:1129px}.detail-content-new .Page .detail-content-left .comment-List-box .comment-List .comment-detail{width:1134px}.detail-content-new .Page .detail-content-left .recommend-cloumn li dl dd{float:left;width:961px}.detail-content-new .Page .detail-content-left .recommend-course li{margin-left:24px;width:177px}.detail-content-new .Page .detail-content-left .recommend-course li:nth-child(5),.detail-content-new .Page .detail-content-left .recommend-course li:nth-child(6){display:block}.detail-content-new .Page .detail-content-left .recommend-course li .pic,.detail-content-new .Page .detail-content-left .recommend-course li .pic img{height:107px;width:177px}.action-aside{margin:-300px 0 0 -892px}}.cto-mermaid svg{cursor:zoom-in}.artical-content-bak a img{cursor:pointer!important}.imgViewDom{background:hsla(0,0%,100%,.8);display:none;height:100%;left:0;overflow:auto;position:fixed;text-align:center;top:0;width:100%;z-index:99999999}.imgViewDom .img-content{height:100%;margin:0 auto;overflow:auto;position:relative;width:100%}.imgViewDom .small-img{cursor:zoom-out;left:50%!important;margin:0 auto;position:absolute!important;text-align:center;top:50%!important;transform:translate(-50%,-50%);-ms-transform:translate(-50%,-50%);-moz-transform:translate(-50%,-50%);-webkit-transform:translate(-50%,-50%);-o-transform:translate(-50%,-50%)}.cto-mermaid.gantt .titleText,.imgViewDom svg .titleText{font-size:24px!important}.cto-mermaid.gantt .section0,.imgViewDom svg .section0{fill:#e2eafe!important}.cto-mermaid.gantt .task0,.cto-mermaid.gantt .task1,.cto-mermaid.gantt .task2,.cto-mermaid.gantt .task3,.imgViewDom svg .task0,.imgViewDom svg .task1,.imgViewDom svg .task2,.imgViewDom svg .task3{fill:#9eb8fa!important;stroke-width:0!important}.cto-mermaid.gantt .grid .tick line,.imgViewDom svg .grid .tick line{stroke:#c1c5cc;opacity:.5}.cto-mermaid.gantt .grid .tick text,.imgViewDom svg .grid .tick text{font-size:14px!important}.cto-mermaid.seq .actor,.imgViewDom svg .actor{stroke-width:0;fill:#f3f5f9!important}.cto-mermaid.seq .messageText,.cto-mermaid.seq .noteText>tspan,.cto-mermaid.seq text.actor>tspan,.imgViewDom svg .messageText,.imgViewDom svg .noteText>tspan,.imgViewDom svg text.actor>tspan{fill:#1a233d!important}.cto-mermaid.seq .messageText,.imgViewDom svg .messageText{stroke:none!important}.cto-mermaid.seq .note,.imgViewDom svg .note{stroke-width:0}#result img{height:auto!important}.modal-bg{background:rgba(0,0,0,.45);bottom:0;display:none;height:100vh;top:0;width:100%}.modal-bg,.modal-bg .modal{left:0;position:fixed;right:0;z-index:99999}.modal-bg .modal{background:#fff;border-radius:10px;margin:0 auto;max-height:450px;min-height:150px;overflow:hidden;padding:45px 46px;top:30%;width:450px}.modal-bg .modal .iconblog{color:#acacac;cursor:pointer;font-size:12px;position:absolute;right:12px;top:12px}.modal-bg .modal .content{-webkit-line-clamp:6;-webkit-box-orient:vertical;color:#999;display:-webkit-box;overflow:hidden;position:relative;text-overflow:ellipsis}.modal-bg .modal .content .modal-title{color:#333}.modal-bg .modal .tip-box{color:#333;margin-bottom:50px;margin-top:20px}.modal-bg .modal .tip-box .zhiCustomBtn{color:#2d66fe}.modal-bg .modal .know-box{text-align:center}.modal-bg .modal .know-box .know-btn{border:1px solid #333;border-radius:4px;cursor:pointer;display:inline-block;height:40px;line-height:40px;text-align:center;width:150px}#Msg_Question .question{padding-bottom:22px}#Msg_Question h6{font-size:20px;margin-bottom:20px}#Msg_Question p{text-align:center}#Msg_Question .msgbtn{text-align:center!important}#Msg_Question .msgbtn button{margin-bottom:20px;margin-right:0!important}.blog-link{margin-top:.7rem}.minmenu ul:before{display:none!important}.hover-ball{bottom:435px!important}.tag-box{display:flex;margin-top:10px}.tag-box .tag-item{background:#f2f2f2;border-radius:4px;color:#6a6a6a;cursor:pointer;font-size:12px;font-weight:400;line-height:18px;margin-right:10px;padding:0 9px}.tag-box .tag-item a{color:#858585}.tag-box .tag-item:hover{background:#f1f5ff;color:#3e71f6}.tag-box .tag-item:hover a{color:#3e71f6}.tag,.type{border-radius:2px;color:#fff;font-size:12px;height:18px;line-height:18px;margin-right:6px;padding:0 3px;text-align:center}.tag.type_top,.type.type_top{background:#f8b57e}.tag.type_recommend,.type.type_recommend{background:#f3c352}.tag.type_original,.type.type_original{background:#99cea4}.tag.type_reprint,.type.type_reprint{background:#84c4fa}.tag.type_translation,.type.type_translation{background:#fea4a4}.tag.type_selected,.type.type_selected{background:#84a0fa}.infomessage{background:linear-gradient(144deg,#fdf6e8,#f9eddd);border-radius:4px;color:#ae7518;display:inline-block;font-size:12px;font-weight:500;line-height:21px;margin-right:10px;padding-left:28px;padding-right:9px;position:relative}.infomessage .blogIcon{display:inline-block;left:5px;position:absolute}.infomessage b{font-weight:400;margin-right:5px}.list-subjuct{align-items:center;background:#f1f5ff;border-radius:10px;box-sizing:border-box;display:flex;height:18px;line-height:18px;margin-left:21px;padding:0 8px 0 3px}.list-subjuct .fontsizeIcon{color:#3e71f6;font-size:14px}.list-subjuct span{color:#3e71f6;font-size:12px;font-weight:500;margin-left:3px;max-width:197px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.blogIcon{background-image:url("https://s2.51cto.com/blog/sprites/homeIcon12x.png");background-size:137px 80px}.webp .blogIcon{background-image:url("https://s2.51cto.com/blog/sprites/homeIcon12x.png?x-oss-process=image/format,webp")}.blogIcon-article{background-position:0 0;height:40px;width:40px}.blogIcon-huifu-2{background-position:-96px -18px;height:14px;width:20px}.blogIcon-icon_huati{background-position:-80px -39px;height:14px;width:14px}.blogIcon-icon_rank{background-position:-80px -18px;height:21px;width:16px}.blogIcon-icon_xiewenzhang{background-position:-94px -39px;height:14px;width:14px}.blogIcon-identity{background-position:-40px 0;height:40px;width:40px}.blogIcon-liulan{background-position:-116px -18px;height:14px;width:20px}.blogIcon-manager{background-position:0 -40px;height:40px;width:40px}.blogIcon-more1{background-position:-108px -39px;height:10px;width:6px}.blogIcon-more2{background-position:-114px -39px;height:10px;width:6px}.blogIcon-move{background-position:-40px -40px;height:40px;width:40px} 
</style>
             </head>
<body class="webp">
<img src="https://s2.51cto.com/images/100/blog/share_default.jpeg?x-oss-process=image/format,webp/ignore-error,1"  border="0" style="width:0; height:0; position:absolute;">
<div class="Content-box">
    <div class="Content detail-content-new">
    <!--关注-->
    <div class="fixtitle">
        <div class="clearfix Page">
            <h3 class="fl title">机器学习sklearn 模型导出 sklearn导入数据</h3>
            <div class="messbox fr">
                                                            <a id="checkFollow1_16203600" class="follow-1 checkFollow on">关注</a>
                                                    <a href="https://blog.51cto.com/u_16213600" class="name" target="_blank" title="mob64ca13fc5fb6">mob64ca13fc5fb6</a>
                <strong>
                    <a href="https://blog.51cto.com/u_16213600" class="avatar" target="_blank">
                        <img class="is-vip-img is-vip-img-4" data-uid="16203600" src="https://s2.51cto.com/images/100/ucenter/noavatar_middle.gif">
                    </a>
                </strong>
            </div>
        </div>
    </div>
    <!--大模块引入-->
    <div class="clearfix Page" id="page_center" style="position:relative;">
                <aside class="detail-content-directory common-content-directory">
     <!-- 文章目录 -->
     <section class="common-section common-spacing table-contents"  style="background:none">
        <div class="clearfix common-sub-title">
            <strong title="文章目录">文章目录</strong>
            <i class="iconblog blogquxiao18" id="closeDirectory"></i>
        </div>
        <div class="directory" id="directory-parent2" >
            <ul class="directory-list directory-list-left" id="directory-left">
                                                                   <li                             class="lv3"
                                                    >
                            <div class="title">
                                <span data-id="#h0">
                                                                        1. 获取数据                                </span>
                            </div>
                        </li>
                                                                                            <li                             class="lv4"
                                                    >
                            <div class="title">
                                <span data-id="#h1">
                                                                        1.1 导入sklearn数据集                                </span>
                            </div>
                        </li>
                                                                                            <li                             class="lv4"
                                                    >
                            <div class="title">
                                <span data-id="#h2">
                                                                        1.2 创建数据集                                </span>
                            </div>
                        </li>
                                                                                            <li                             class="lv3"
                                                    >
                            <div class="title">
                                <span data-id="#h3">
                                                                        2. 数据预处理                                </span>
                            </div>
                        </li>
                                                                                            <li                             class="lv4"
                                                    >
                            <div class="title">
                                <span data-id="#h4">
                                                                        2.1 数据归一化                                </span>
                            </div>
                        </li>
                                                                                            <li                             class="lv4"
                                                    >
                            <div class="title">
                                <span data-id="#h5">
                                                                        2.2 正则化（normalize）                                </span>
                            </div>
                        </li>
                                                                                            <li                             class="lv4"
                                                    >
                            <div class="title">
                                <span data-id="#h6">
                                                                        &nbsp;2.3 one-hot编码                                </span>
                            </div>
                        </li>
                                                                                            <li                             class="lv3"
                                                    >
                            <div class="title">
                                <span data-id="#h7">
                                                                        3. 数据集拆分                                </span>
                            </div>
                        </li>
                                                                                            <li                             class="lv3"
                                                    >
                            <div class="title">
                                <span data-id="#h8">
                                                                        4. 定义模型                                </span>
                            </div>
                        </li>
                                                                                            <li                             class="lv4"
                                                    >
                            <div class="title">
                                <span data-id="#h9">
                                                                        &nbsp;4.1 线性回归                                </span>
                            </div>
                        </li>
                                                                                            <li                             class="lv4"
                                                    >
                            <div class="title">
                                <span data-id="#h10">
                                                                        &nbsp;4.2 逻辑回归LR                                </span>
                            </div>
                        </li>
                                                                                            <li                             class="lv4"
                                                    >
                            <div class="title">
                                <span data-id="#h11">
                                                                        &nbsp;4.3 朴素贝叶斯算法NB                                </span>
                            </div>
                        </li>
                                                                                            <li                             class="lv4"
                                                    >
                            <div class="title">
                                <span data-id="#h12">
                                                                        &nbsp;4.4 决策树DT                                </span>
                            </div>
                        </li>
                                                                                            <li                             class="lv4"
                                                    >
                            <div class="title">
                                <span data-id="#h13">
                                                                        4.5 支持向量机SVM                                </span>
                            </div>
                        </li>
                                                                                            <li                             class="lv4"
                                                    >
                            <div class="title">
                                <span data-id="#h14">
                                                                        &nbsp;4.6 k近邻算法KNN                                </span>
                            </div>
                        </li>
                                                                                            <li                             class="lv4"
                                                    >
                            <div class="title">
                                <span data-id="#h15">
                                                                        4.7 多层感知机（神经网络）                                </span>
                            </div>
                        </li>
                                                                                            <li                             class="lv3"
                                                    >
                            <div class="title">
                                <span data-id="#h16">
                                                                        5. 模型评估与选择篇                                </span>
                            </div>
                        </li>
                                                                                            <li                             class="lv4"
                                                    >
                            <div class="title">
                                <span data-id="#h17">
                                                                        5.1 交叉验证                                </span>
                            </div>
                        </li>
                                                                                            <li                             class="lv4"
                                                    >
                            <div class="title">
                                <span data-id="#h18">
                                                                        5.2 检验曲线                                </span>
                            </div>
                        </li>
                                                                                            <li                             class="lv3"
                                                    >
                            <div class="title">
                                <span data-id="#h19">
                                                                        6. 保存模型                                </span>
                            </div>
                        </li>
                                                                                            <li                             class="lv4"
                                                    >
                            <div class="title">
                                <span data-id="#h20">
                                                                        6.1 保存为pickle文件                                </span>
                            </div>
                        </li>
                                                                                            <li                             class="lv4"
                                                    >
                            <div class="title">
                                <span data-id="#h21">
                                                                        6.2 sklearn自带方法joblib                                </span>
                            </div>
                        </li>
                                                        </ul>
        </div>
    </section>
</aside>
                <article class="detail-content-left">
    <div class="common-section common-spacing mb30 article-detail">
    <div class="title">
        <h1>机器学习sklearn 模型导出 sklearn导入数据</h1>
         
                <span class="reprint">转载</span>
        
    </div>
    <div class="messbox">
        <p class="clearfix mess-line1">
            <a class="fl" href="https://blog.51cto.com/u_16213600" rel="nofollow">mob64ca13fc5fb6</a>
            <time class="fl" pubdate="2024-05-16 10:05:52">2024-05-16 10:05:52</time>
                                </p>
        <p class="clearfix mess-tag">
                            <strong class="fl">
                    <em class="fl">文章标签</em>
                                            <a href="https://blog.51cto.com/topic/5160e71e3f0df7a.html" class="fl shence_tag" target="_blank" >机器学习sklearn 模型导出</a>
                                            <a href="https://blog.51cto.com/topic/rengongzhineng.html" class="fl shence_tag" target="_blank" >人工智能</a>
                                            <a href="https://blog.51cto.com/topic/data-structures-and-algorithms.html" class="fl shence_tag" target="_blank" >数据结构与算法</a>
                                            <a href="https://blog.51cto.com/topic/shujuji.html" class="fl shence_tag" target="_blank" >数据集</a>
                                            <a href="https://blog.51cto.com/topic/zhengzehua.html" class="fl shence_tag" target="_blank" >正则化</a>
                                    </strong>
                                        <strong class="fl">
                    <em class="fl">文章分类</em>
                                                                        <a href="https://blog.51cto.com/nav/machine" class="fl shence_cate" target="_blank" rel="nofollow">机器学习</a>
                                                                                                <a href="https://blog.51cto.com/nav/ai" class="fl shence_cate" target="_blank" rel="nofollow">人工智能</a>
                                                            </strong>
                                </p>
    </div>
                <div class="article-content-wrap" >
                    <div class="artical-content-bak main-content editor-side-new">
                <div class="con editor-preview-side" id="result"  data-version="1"><div class="editor-container container am-engine" id="container" data-element="root"><p><br></p><p>　　传统的机器学习任务从开始到建模的一般流程是：获取数据 -&gt; 数据预处理 -&gt; 训练建模 -&gt; 模型评估 -&gt; 预测，分类。本文我们将依据传统机器学习的流程，看看在每一步流程中都有哪些常用的函数以及它们的用法是怎么样的。希望你看完这篇文章可以最为快速的开始你的学习任务。</p><h3 id="h0">1. 获取数据</h3><h4 id="h1">1.1 导入sklearn数据集</h4><p>　　sklearn中包含了大量的优质的数据集，在你学习机器学习的过程中，你可以通过使用这些数据集实现出不同的模型，从而提高你的动手实践能力，同时这个过程也可以加深你对理论知识的理解和把握。（这一步我也亟需加强，一起加油！^-^）</p><p>首先呢，要想使用sklearn中的数据集，必须导入datasets模块：</p><p> <br></p><p> <br></p><div><pre class="language-plain"><code>from sklearn import datasets</code></pre></div><p> <br></p><p> <br></p><p>&nbsp;下图中包含了大部分sklearn中数据集，调用方式也在图中给出，这里我们拿iris的数据来举个例子：</p><p>　　<br></p><p style="text-align:center;"><img    src='https://s2.51cto.com/images/blog/202405/15015125_6643a49d0bfbd64134.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_30,g_se,x_10,y_10,shadow_20,type_ZmFuZ3poZW5naGVpdGk=/format,webp/resize,m_fixed,w_1184' alt='机器学习sklearn 模型导出 sklearn导入数据_人工智能'  style="width: 307px; visibility: visible;"></p><p style="text-align:center;"><img    src='https://s2.51cto.com/images/blog/202405/15015125_6643a49d1ef572503.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_30,g_se,x_10,y_10,shadow_20,type_ZmFuZ3poZW5naGVpdGk=/format,webp/resize,m_fixed,w_1184' alt='机器学习sklearn 模型导出 sklearn导入数据_数据结构与算法_02'  style="width: 298px; visibility: visible;"></p><p>  <br></p><div><pre class="language-plain"><code>iris = datasets.load_iris() # 导入数据集
X = iris.data # 获得其特征向量
y = iris.target # 获得样本label</code></pre></div><p>  <br></p><h4 id="h2">1.2 创建数据集</h4><p>　　你除了可以使用sklearn自带的数据集，还可以自己去创建训练样本，具体用法参见《<a rel="nofollow" href="http://scikit-learn.org/stable/datasets/">Dataset loading utilities</a>》，这里我们简单介绍一些，sklearn中的samples generator包含的大量创建样本数据的方法：</p><p>　　&nbsp;<br></p><p style="text-align:center;"><img    src='https://s2.51cto.com/images/blog/202405/15015125_6643a49d335358109.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_30,g_se,x_10,y_10,shadow_20,type_ZmFuZ3poZW5naGVpdGk=/format,webp/resize,m_fixed,w_1184' alt='机器学习sklearn 模型导出 sklearn导入数据_正则化_03'  style="width: 278px; visibility: visible;"></p><p style="text-align:center;"><img    src='https://s2.51cto.com/images/blog/202405/15015125_6643a49d46ae160081.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_30,g_se,x_10,y_10,shadow_20,type_ZmFuZ3poZW5naGVpdGk=/format,webp/resize,m_fixed,w_1184' alt='机器学习sklearn 模型导出 sklearn导入数据_人工智能_04'  style="width: 298px; visibility: visible;"></p><p>下面我们拿分类问题的样本生成器举例子：</p><p>  <br></p><div><pre class="language-plain"><code>from sklearn.datasets.samples_generator import make_classification

X, y = make_classification(n_samples=6, n_features=5, n_informative=2, 
    n_redundant=2, n_classes=2, n_clusters_per_class=2, scale=1.0, 
    random_state=20)

# n_samples：指定样本数
# n_features：指定特征数
# n_classes：指定几分类
# random_state：随机种子，使得随机状可重</code></pre></div><p>  <br></p><div><pre class="language-plain"><code>&gt;&gt;&gt; for x_,y_ in zip(X,y):
    print(y_,end=': ')
    print(x_)

    
0: [-0.6600737  -0.0558978   0.82286793  1.1003977  -0.93493796]
1: [ 0.4113583   0.06249216 -0.90760075 -1.41296696  2.059838  ]
1: [ 1.52452016 -0.01867812  0.20900899  1.34422289 -1.61299022]
0: [-1.25725859  0.02347952 -0.28764782 -1.32091378 -0.88549315]
0: [-3.28323172  0.03899168 -0.43251277 -2.86249859 -1.10457948]
1: [ 1.68841011  0.06754955 -1.02805579 -0.83132182  0.93286635]</code></pre></div><p>  <br></p><h3 id="h3">2. 数据预处理</h3><p>　　数据预处理阶段是机器学习中不可缺少的一环，它会使得数据更加有效的被模型或者评估器识别。下面我们来看一下sklearn中有哪些平时我们常用的函数：</p><p>  <br></p><div><pre class="language-plain"><code>from sklearn import preprocessing</code></pre></div><p>  <br></p><h4 id="h4">2.1 数据归一化</h4><p>　　为了使得训练数据的标准化规则与测试数据的标准化规则同步，preprocessing中提供了很多Scaler：</p><p>  <br></p><div><pre class="language-plain"><code>data = [[0, 0], [0, 0], [1, 1], [1, 1]]
# 1. 基于mean和std的标准化
scaler = preprocessing.StandardScaler().fit(train_data)
scaler.transform(train_data)
scaler.transform(test_data)

# 2. 将每个特征值归一化到一个固定范围
scaler = preprocessing.MinMaxScaler(feature_range=(0, 1)).fit(train_data)
scaler.transform(train_data)
scaler.transform(test_data)
#feature_range: 定义归一化范围，注用（）括起来</code></pre></div><p>  <br></p><h4 id="h5">2.2 正则化（<code style="background-color: rgb(231, 243, 237); padding: 1px 3px; border-radius: 4px; overflow-wrap: break-word; text-indent: 0px; display: inline-block;">normalize</code>）</h4><p>　　当你想要计算两个样本的相似度时必不可少的一个操作，就是正则化。其思想是：首先求出样本的p-范数，然后该样本的所有元素都要除以该范数，这样最终使得每个样本的范数都为1。</p><p>  <br></p><div><pre class="language-plain"><code>&gt;&gt;&gt; X = [[ 1., -1.,  2.],
...      [ 2.,  0.,  0.],
...      [ 0.,  1., -1.]]
&gt;&gt;&gt; X_normalized = preprocessing.normalize(X, norm='l2')

&gt;&gt;&gt; X_normalized                                      
array([[ 0.40..., -0.40...,  0.81...],
       [ 1.  ...,  0.  ...,  0.  ...],
       [ 0.  ...,  0.70..., -0.70...]])</code></pre></div><p>  <br></p><h4 id="h6">&nbsp;2.3 one-hot编码</h4><p>　　one-hot编码是一种对离散特征值的编码方式，在LR模型中常用到，用于给线性模型增加非线性能力。</p><p>  <br></p><div><pre class="language-plain"><code>data = [[0, 0, 3], [1, 1, 0], [0, 2, 1], [1, 0, 2]]
encoder = preprocessing.OneHotEncoder().fit(data)
enc.transform(data).toarray()</code></pre></div><p>  <br></p><h3 id="h7">3. 数据集拆分</h3><p>　　在得到训练数据集时，通常我们经常会把训练数据集进一步拆分成训练集和验证集，这样有助于我们模型参数的选取。</p><p>  <br></p><div><pre class="language-plain"><code># 作用：将数据集划分为 训练集和测试集
# 格式：train_test_split(*arrays, **options)
from sklearn.mode_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
"""
参数
---
arrays：样本数组，包含特征向量和标签

test_size：
　　float-获得多大比重的测试样本 （默认：0.25）
　　int - 获得多少个测试样本

train_size: 同test_size

random_state:
　　int - 随机种子（种子固定，实验可复现）
　　
shuffle - 是否在分割之前对数据进行洗牌（默认True）

返回
---
分割后的列表，长度=2*len(arrays), 
　　(train-test split)
"""</code></pre></div><p>  <br></p><h3 id="h8">4. 定义模型</h3><p>　　在这一步我们首先要分析自己数据的类型，搞清出你要用什么模型来做，然后我们就可以在sklearn中定义模型了。sklearn为所有模型提供了非常相似的接口，这样使得我们可以更加快速的熟悉所有模型的用法。在这之前我们先来看看模型的常用属性和功能：</p><p>  <br></p><div><pre class="language-plain"><code># 拟合模型
model.fit(X_train, y_train)
# 模型预测
model.predict(X_test)

# 获得这个模型的参数
model.get_params()
# 为模型进行打分
model.score(data_X, data_y) # 线性回归：R square； 分类问题： acc</code></pre></div><p>  <br></p><h4 id="h9">&nbsp;4.1 线性回归</h4><p>  <br></p><div><pre class="language-plain"><code>from sklearn.linear_model import LinearRegression
# 定义线性回归模型
model = LinearRegression(fit_intercept=True, normalize=False, 
    copy_X=True, n_jobs=1)
"""
参数
---
    fit_intercept：是否计算截距。False-模型没有截距
    normalize： 当fit_intercept设置为False时，该参数将被忽略。 如果为真，则回归前的回归系数X将通过减去平均值并除以l2-范数而归一化。
     n_jobs：指定线程数
"""</code></pre></div><p>  　　　　　　<br></p><p style="text-align:center;"><img    src='https://s2.51cto.com/images/blog/202405/15015125_6643a49d5a9109125.png?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_30,g_se,x_10,y_10,shadow_20,type_ZmFuZ3poZW5naGVpdGk=/format,webp/resize,m_fixed,w_1184' alt='机器学习sklearn 模型导出 sklearn导入数据_数据结构与算法_05'  style="width: 213px; visibility: visible;"></p><h4 id="h10">&nbsp;4.2 逻辑回归LR</h4><p>  <br></p><div><pre class="language-plain"><code>from sklearn.linear_model import LogisticRegression
# 定义逻辑回归模型
model = LogisticRegression(penalty=’l2’, dual=False, tol=0.0001, C=1.0, 
    fit_intercept=True, intercept_scaling=1, class_weight=None, 
    random_state=None, solver=’liblinear’, max_iter=100, multi_class=’ovr’, 
    verbose=0, warm_start=False, n_jobs=1)

"""参数
---
    penalty：使用指定正则化项（默认：l2）
    dual: n_samples &gt; n_features取False（默认）
    C：正则化强度的反，值越小正则化强度越大
    n_jobs: 指定线程数
    random_state：随机数生成器
    fit_intercept: 是否需要常量
"""</code></pre></div><p>  <br></p><h4 id="h11">&nbsp;4.3 朴素贝叶斯算法NB</h4><p>  <br></p><div><pre class="language-plain"><code>from sklearn import naive_bayes
model = naive_bayes.GaussianNB() # 高斯贝叶斯
model = naive_bayes.MultinomialNB(alpha=1.0, fit_prior=True, class_prior=None)
model = naive_bayes.BernoulliNB(alpha=1.0, binarize=0.0, fit_prior=True, class_prior=None)
"""
文本分类问题常用MultinomialNB
参数
---
    alpha：平滑参数
    fit_prior：是否要学习类的先验概率；false-使用统一的先验概率
    class_prior: 是否指定类的先验概率；若指定则不能根据参数调整
    binarize: 二值化的阈值，若为None，则假设输入由二进制向量组成
"""</code></pre></div><p>  <br></p><h4 id="h12">&nbsp;4.4 决策树DT</h4><p>  <br></p><div><pre class="language-plain"><code>from sklearn import tree 
model = tree.DecisionTreeClassifier(criterion=’gini’, max_depth=None, 
    min_samples_split=2, min_samples_leaf=1, min_weight_fraction_leaf=0.0, 
    max_features=None, random_state=None, max_leaf_nodes=None, 
    min_impurity_decrease=0.0, min_impurity_split=None,
     class_weight=None, presort=False)
"""参数
---
    criterion ：特征选择准则gini/entropy
    max_depth：树的最大深度，None-尽量下分
    min_samples_split：分裂内部节点，所需要的最小样本树
    min_samples_leaf：叶子节点所需要的最小样本数
    max_features: 寻找最优分割点时的最大特征数
    max_leaf_nodes：优先增长到最大叶子节点数
    min_impurity_decrease：如果这种分离导致杂质的减少大于或等于这个值，则节点将被拆分。
"""</code></pre></div><p>  <br></p><h4 id="h13">4.5 支持向量机SVM</h4><p>  <br></p><div><pre class="language-plain"><code>from sklearn.svm import SVC
model = SVC(C=1.0, kernel=’rbf’, gamma=’auto’)
"""参数
---
    C：误差项的惩罚参数C
    gamma: 核相关系数。浮点数，If gamma is ‘auto’ then 1/n_features will be used instead.
"""</code></pre></div><p>  <br></p><h4 id="h14">&nbsp;4.6 k近邻算法KNN</h4><p>  <br></p><div><pre class="language-plain"><code>from sklearn import neighbors
#定义kNN分类模型
model = neighbors.KNeighborsClassifier(n_neighbors=5, n_jobs=1) # 分类
model = neighbors.KNeighborsRegressor(n_neighbors=5, n_jobs=1) # 回归
"""参数
---
    n_neighbors： 使用邻居的数目
    n_jobs：并行任务数
"""</code></pre></div><p>  <br></p><h4 id="h15">4.7 多层感知机（神经网络）</h4><p>  <br></p><div><pre class="language-plain"><code>from sklearn.neural_network import MLPClassifier
# 定义多层感知机分类算法
model = MLPClassifier(activation='relu', solver='adam', alpha=0.0001)
"""参数
---
    hidden_layer_sizes: 元祖
    activation：激活函数
    solver ：优化算法{‘lbfgs’, ‘sgd’, ‘adam’}
    alpha：L2惩罚(正则化项)参数。
"""</code></pre></div><p>  <br></p><h3 id="h16">5. 模型评估与选择篇</h3><h4 id="h17">5.1 交叉验证</h4><p>  <br></p><div><pre class="language-plain"><code>from sklearn.model_selection import cross_val_score
cross_val_score(model, X, y=None, scoring=None, cv=None, n_jobs=1)
"""参数
---
    model：拟合数据的模型
    cv ： k-fold
    scoring: 打分参数-‘accuracy’、‘f1’、‘precision’、‘recall’ 、‘roc_auc’、'neg_log_loss'等等
"""</code></pre></div><p>  <br></p><h4 id="h18">5.2 检验曲线</h4><p>　　使用检验曲线，我们可以更加方便的改变模型参数，获取模型表现。</p><p>  <br></p><div><pre class="language-plain"><code>from sklearn.model_selection import validation_curve
train_score, test_score = validation_curve(model, X, y, param_name, param_range, cv=None, scoring=None, n_jobs=1)
"""参数
---
    model:用于fit和predict的对象
    X, y: 训练集的特征和标签
    param_name：将被改变的参数的名字
    param_range： 参数的改变范围
    cv：k-fold
   
返回值
---
   train_score: 训练集得分（array）
    test_score: 验证集得分（array）
"""</code></pre></div><p>  <br></p><p><a rel="nofollow" href="http://scikit-learn.org/stable/auto_examples/model_selection/plot_validation_curve.html#sphx-glr-auto-examples-model-selection-plot-validation-curve-py">例子</a></p><h3 id="h19">6. 保存模型</h3><p>　　最后，我们可以将我们训练好的model保存到本地，或者放到线上供用户使用，那么如何保存训练好的model呢？主要有下面两种方式：</p><h4 id="h20">6.1 保存为pickle文件</h4><p>  <br></p><div><pre class="language-plain"><code>import pickle

# 保存模型
with open('model.pickle', 'wb') as f:
    pickle.dump(model, f)

# 读取模型
with open('model.pickle', 'rb') as f:
    model = pickle.load(f)
model.predict(X_test)</code></pre></div><p>  <br></p><h4 id="h21">6.2 sklearn自带方法joblib</h4><p>  <br></p><div><pre class="language-plain"><code>from sklearn.externals import joblib

# 保存模型
joblib.dump(model, 'model.pickle')

#载入模型
model = joblib.load('model.pickle')</code></pre></div><p> <br></p><p><br></p></div></div>
            </div>
        
        <div id="asideoffset"></div>
        <div class="clearfix label-list">

            <!--            <span>本文包含：</span>-->
            <!--          -->
            <!--            <a href="" target="_blank"></a>-->

        </div>
                    <div class="copytext2">本文章为转载内容，我们尊重原作者对文章享有的著作权。如有内容错误或侵权问题，欢迎原作者联系我们进行内容更正或删除文章。 </div>
            </div>
    <div class="action-box">
        <ul>
                        <li>
                <strong class="is-praise  " type="1" blog_id="10820896" userid='16203600'>
                    <a href="javascript:;"><i></i></a>
                    <span><b class="praise-num"></b>赞</span>
                </strong>
            </li>
            <li>
                <strong class="favorites-opt">
                    <a href="javascript:;"><i></i></a>
                    <span><b class="favorites-num"></b>收藏</span>
                </strong>
            </li>
            <li>
                <strong class="Topraise">
                    <a href="javascript:;"><i class="iconblog blogpinglun"></i></a>
                    <span><b class="comments_num"></b>评论</span>
                </strong>
            </li>
            <li class="share">
                <strong class="">
                    <a href="javascript:;"><i class="iconblog blogfen"></i></a>
                    <span>分享</span>
                </strong>
            </li>
                            <li>
                    <strong class="article-report">
                        <a href="javascript:;"><i class="iconblog blogjubaobeifen report-icon" style="font-size: 23px"></i></a>
                        <span>举报</span>
                    </strong>
                </li>
                    </ul>
    </div>
    <div class="clearfix lists">
                    <p class="fl"><span>上一篇：</span><a href="https://blog.51cto.com/u_16213600/10820845">将proto文件转为python能用的py文件 protobuf 转json</a></p>
                            <p class="fr"><span>下一篇：</span><a href="https://blog.51cto.com/u_16213600/10821582">Java毕设 springboot能用吗 springboot毕设题目</a></p>
            </div>
    <div class="text-aticle">

    </div>
</div>
    

<div class="common-section common-spacing mb30 comment-box" id="comment">
    <div class="comment-textarea clearfix">
        <div class="avatar">
            <a href="https://blog.51cto.com/" class="header-img" target="_blank">
                <img  src="https://ucenter.51cto.com/images/noavatar_middle.gif"/>
            </a>
        </div>
        <div class="textarea-box">
            <div class="textarea-show clearfix">
                <span>提问和评论都可以，用心的回复会被更多人看到</span>
                <strong>评论</strong>
            </div>
            <div class="textarea-hide">
                <div class="top">
                    <textarea class="textareadiv textareadiv-publish" name="" id="textareadiv-publish" placeholder="提问和评论都可以，用心的回复会被更多人看到和认可" maxlength="500"></textarea>
                </div>
                <div class="bot clearfix">
                    <strong class="fr publish-btn" flag="1" id="publish-btn">发布评论</strong>
                </div>
            </div>
        </div>
    </div>
    <div class="comment-num"  style="display:none;">
        <strong>全部评论</strong>
        <span>(<b id="CommentNum"></b>)</span>
        <span class="fr sort" type="up_num" order="0"><i class="iconblog blogzuire"></i>最热</span>
        <span class="fr sort on" type="create_time" order="0"><i class="iconblog blogzuixinblogzuixin"></i>最新</span>
    </div>
    <div class="comment-List-box">
        </div>
</div>
    
    <section class="common-section common-spacing mb30">
        <div class="clearfix common-sub-title">
            <strong>相关文章</strong>
        </div>
        <ul class="recommend-about">
                            <li>
                    <div class="about-aticle-list">
                        <a href="https://blog.51cto.com/u_16701217/10755546"
                           data-report-query="xiangguantuijian&01" target="_blank" class="title">
                            <div class="tit">机器学习之sklearn基础教程</div>
                            <p> Scikit-learn（简称sklearn）是Python中最受欢迎的机器学习库之一，它提供了丰富的机器学习算法和数据预处理工具。本文将深入浅出地介绍sklearn的基础概念，核心理论，常见问题和易错点，并给出代码示例。1. 基础概念1.1 模型选择与训练在sklearn中，模型被封装在sklearn.model_selection模块下，如sklearn.linear_model.Li</p>
                        </a>
                        <!-- 标签页 -->
                                                    <div class="tag-box">
                                                                    <span class="tag-item">
                                         python                                    </span>
                                                                    <span class="tag-item">
                                         机器学习                                    </span>
                                                                    <span class="tag-item">
                                         特征选择                                    </span>
                                                            </div>
                                                                    </div>

                </li>
                            <li>
                    <div class="about-aticle-list">
                        <a href="https://blog.51cto.com/u_16866380/11457469"
                           data-report-query="xiangguantuijian&02" target="_blank" class="title">
                            <div class="tit">sklearn预测评估指标：混淆矩阵计算</div>
                            <p> 很多时候需要对自己模型进行性能评估，对于一些理论上面的知识我想基本不用说明太多，关于校验模型准确度的指标主要有混淆矩阵、准确率、精确率、召回率、F1 score。这里我们主要进行实践利用sklearn快速实现模型数据校验，完成基础指标计算。混淆矩阵查准率（precision）与查全率（recall）是对于需求在信息检索、Web搜索等应用评估性能度量适应度高的检测数值。对于二分类问题，可将真实类别与</p>
                        </a>
                        <!-- 标签页 -->
                                                    <div class="tag-box">
                                                                    <span class="tag-item">
                                         混淆矩阵                                    </span>
                                                                    <span class="tag-item">
                                         参数说明                                    </span>
                                                                    <span class="tag-item">
                                         反例                                    </span>
                                                            </div>
                                                                    </div>

                </li>
                            <li>
                    <div class="about-aticle-list">
                        <a href="https://blog.51cto.com/u_16841384/11136494"
                           data-report-query="xiangguantuijian&03" target="_blank" class="title">
                            <div class="tit">Python数据处理之导入导出excel数据</div>
                            <p> Python的一大应用就是数据分析了，而数据分析中，经常碰到需要处理Excel数据的情况。这里做一个Python处理Excel数据的总结，基本受用大部分情况。</p>
                        </a>
                        <!-- 标签页 -->
                                                    <div class="tag-box">
                                                                    <span class="tag-item">
                                         数据                                    </span>
                                                                    <span class="tag-item">
                                         Python                                    </span>
                                                                    <span class="tag-item">
                                         excel                                    </span>
                                                            </div>
                                                                    </div>

                </li>
                            <li>
                    <div class="about-aticle-list">
                        <a href="https://blog.51cto.com/u_14693305/5650011"
                           data-report-query="xiangguantuijian&04" target="_blank" class="title">
                            <div class="tit">机器学习Sklearn数据集</div>
                            <p> 目录​​1 数据集​​​​1.1 可用数据集​​​​1.1.1 Scikit-learn工具介绍​​​​1.1.2 安装​​​​1.1.3 Scikit-learn包含的内容​​​​1.2 sklearn数据集​​​​1.2.1 scikit-learn数据集API介绍​​​​1.2.2 sklearn小数据集​​​​1.2.3 sklearn大数据集​​​​1.2.4 sklearn数据集的使用</p>
                        </a>
                        <!-- 标签页 -->
                                                    <div class="tag-box">
                                                                    <span class="tag-item">
                                         机器学习                                    </span>
                                                                    <span class="tag-item">
                                         sklearn                                    </span>
                                                                    <span class="tag-item">
                                         python                                    </span>
                                                                    <span class="tag-item">
                                         数据集                                    </span>
                                                                    <span class="tag-item">
                                         数据                                    </span>
                                                            </div>
                                                                    </div>

                </li>
                            <li>
                    <div class="about-aticle-list">
                        <a href="https://blog.51cto.com/mouday/3048347"
                           data-report-query="xiangguantuijian&05" target="_blank" class="title">
                            <div class="tit">机器学习：sklearn数据集简介</div>
                            <p> 算法分类监督学习 特征值 + 目标值    -分类 目标值是离散数据    -回归 目标值是连续数据无监督学习  只有特征值    -聚类数据集数据-训练集 80% 70% 75%-测试集 20% 30% 25%数据拆分：sklearn.model_selection.train_test_splitsklearn数据集sklearn.datasets	-小规模数据...</p>
                        </a>
                        <!-- 标签页 -->
                                                    <div class="tag-box">
                                                                    <span class="tag-item">
                                         机器学习                                    </span>
                                                            </div>
                                                                    </div>

                </li>
                            <li>
                    <div class="about-aticle-list">
                        <a href="https://blog.51cto.com/u_16213670/8171488"
                           data-report-query="xiangguantuijian&06" target="_blank" class="title">
                            <div class="tit">采用机器学习库 sklearn导入数据集 sklearn怎么导入数据</div>
                            <p> 机器学习的一般流程：&nbsp; &nbsp; &nbsp;1、获取数据&nbsp; &nbsp; &nbsp;2、数据预处理&nbsp; &nbsp; &nbsp;3、数据集分拆&nbsp; &nbsp; &nbsp;4、搭建模型&nbsp; &nbsp; &nbsp;5、模型评估&nbsp; &nbsp; &nbsp;6、模型保存&nbsp; &nbsp; &nbsp;7、模型优化接下来，以S</p>
                        </a>
                        <!-- 标签页 -->
                                                    <div class="tag-box">
                                                                    <span class="tag-item">
                                         数据集                                    </span>
                                                                    <span class="tag-item">
                                         数据                                    </span>
                                                                    <span class="tag-item">
                                         归一化                                    </span>
                                                            </div>
                                                                    </div>

                </li>
                            <li>
                    <div class="about-aticle-list">
                        <a href="https://blog.51cto.com/u_16213666/10744302"
                           data-report-query="xiangguantuijian&07" target="_blank" class="title">
                            <div class="tit">linearregression sklearn 模型导出 sklearn 模型选择</div>
                            <p> 写在前言&nbsp; &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;当你决定调用sklearn中提供的模型去做回归或分类等操作的时候，在不考虑数据优劣的情况下，你就只能依赖sklearn中提供模型和模型对应参数来进行拟合来达到最后的最优结果，这个时候大部分人就会处在我到底选择哪个模型，选择了模型之后我模型参数我该</p>
                        </a>
                        <!-- 标签页 -->
                                                    <div class="tag-box">
                                                                    <span class="tag-item">
                                         sklearn                                    </span>
                                                                    <span class="tag-item">
                                         机器学习                                    </span>
                                                                    <span class="tag-item">
                                         模型调参                                    </span>
                                                                    <span class="tag-item">
                                         数据                                    </span>
                                                                    <span class="tag-item">
                                         交叉验证                                    </span>
                                                            </div>
                                                                    </div>

                </li>
                            <li>
                    <div class="about-aticle-list">
                        <a href="https://blog.51cto.com/u_13317/9571235"
                           data-report-query="xiangguantuijian&08" target="_blank" class="title">
                            <div class="tit">sklearn 机器学习 sklearn教程</div>
                            <p> 文章目录sklearnscikit-learn数据集`sklearn.datasets`：加载获取流行数据集`sklearn`大数据集`sklearn`数据集返回值介绍查看数据分布seaborn数据集划分api交叉验证概念目的api机器学习基本流程特征预处理归一化标准化 sklearnscikit-learn数据集sklearn.datasets：加载获取流行数据集datasets.load_*</p>
                        </a>
                        <!-- 标签页 -->
                                                    <div class="tag-box">
                                                                    <span class="tag-item">
                                         sklearn 机器学习                                    </span>
                                                                    <span class="tag-item">
                                         机器学习                                    </span>
                                                                    <span class="tag-item">
                                         python                                    </span>
                                                                    <span class="tag-item">
                                         人工智能                                    </span>
                                                                    <span class="tag-item">
                                         数据集                                    </span>
                                                            </div>
                                                                    </div>

                </li>
                            <li>
                    <div class="about-aticle-list">
                        <a href="https://blog.51cto.com/u_16213583/10624185"
                           data-report-query="xiangguantuijian&09" target="_blank" class="title">
                            <div class="tit">sklearn迁移学习 sklearn导入外部的数据</div>
                            <p> 如有错误，恳请指出。 文章目录1. scikit-learn概述1.1 技巧介绍1.2 模型保存1.3 模型优化2. scikit-learn涵盖内容3. scikit-learn数据集获取3.1 生成聚类数据：make_blobs3.2 生成分类数据：make_classification3.3 生成环形数据：make_circles3.4 生成回归数据：make_regression3.5 导</p>
                        </a>
                        <!-- 标签页 -->
                                                    <div class="tag-box">
                                                                    <span class="tag-item">
                                         sklearn迁移学习                                    </span>
                                                                    <span class="tag-item">
                                         sklearn                                    </span>
                                                                    <span class="tag-item">
                                         scikit-learn                                    </span>
                                                                    <span class="tag-item">
                                         学习                                    </span>
                                                                    <span class="tag-item">
                                         数据                                    </span>
                                                            </div>
                                                                    </div>

                </li>
                            <li>
                    <div class="about-aticle-list">
                        <a href="https://blog.51cto.com/u_16213696/8956626"
                           data-report-query="xiangguantuijian&10" target="_blank" class="title">
                            <div class="tit">机器学习 sklearn 匹配 sklearn实例</div>
                            <p> 文章目录前言单输出分类问题KN分类器质心分类器NCA直接分类降维对比识别手写数字回归问题多输出人脸示例 前言由于项目需要使用近邻算法进行分类，便读了一些官方案例。单输出分类问题KN分类器scikit-learn实现了两个不同的最近邻分类器：KNeighborsClassifier基于实现学习RadiusNeighborsClassifier,在数据未被均匀采样的情况下，基于半径的邻居分类Radi</p>
                        </a>
                        <!-- 标签页 -->
                                                    <div class="tag-box">
                                                                    <span class="tag-item">
                                         机器学习 sklearn 匹配                                    </span>
                                                                    <span class="tag-item">
                                         数据集                                    </span>
                                                                    <span class="tag-item">
                                         git                                    </span>
                                                                    <span class="tag-item">
                                         ci                                    </span>
                                                            </div>
                                                                    </div>

                </li>
                            <li>
                    <div class="about-aticle-list">
                        <a href="https://blog.51cto.com/u_13446/8171889"
                           data-report-query="xiangguantuijian&11" target="_blank" class="title">
                            <div class="tit">机器学习 sklearn 回归模型 知乎 sklearn 回归分析</div>
                            <p> Python中的sklearn库提供了方便的机器学习算法，那么实现简单的线性回归，所需步骤如下：提出问题理解问题清洗数据构建模型评估模型下面是具体的案例展示，案例数据为”学习时间“与”分数“首先准备数据：提出问题：”学习时间“与”分数“之间是否线性相关，如果是，求出最佳拟合度如何？理解数据：查看数据属性上图可以看出，这是一个20行，两列的二维数组，数据信息完整。数据集中只有两列数据，查看相关系数R</p>
                        </a>
                        <!-- 标签页 -->
                                                    <div class="tag-box">
                                                                    <span class="tag-item">
                                         数据                                    </span>
                                                                    <span class="tag-item">
                                         拟合                                    </span>
                                                                    <span class="tag-item">
                                         线性回归                                    </span>
                                                            </div>
                                                                    </div>

                </li>
                            <li>
                    <div class="about-aticle-list">
                        <a href="https://blog.51cto.com/u_16099258/9062316"
                           data-report-query="xiangguantuijian&12" target="_blank" class="title">
                            <div class="tit">sklearn常用机器学习 sklearn算法</div>
                            <p> 机器学习常用算法小结有监督有答案的商用最多的，主要是分类无监督没有答案半监督部分有答案使用有答案的数据进行训练模型，然后使用陌生数据进行验证过拟合和欠拟合过拟合：使用样本的特征过多，导致很多无用的特征被加入到计算中，导致模型泛化受到过多无用特征的影响，精度变得很低欠拟合：在选取特征时，选取的过于简单，主要的特征没有获取，导致模型在测试集上的表现很差kNNk近邻算法距离抽象的问题，采用欧式距离最近的</p>
                        </a>
                        <!-- 标签页 -->
                                                    <div class="tag-box">
                                                                    <span class="tag-item">
                                         sklearn常用机器学习                                    </span>
                                                                    <span class="tag-item">
                                         岭回归                                    </span>
                                                                    <span class="tag-item">
                                         数据                                    </span>
                                                                    <span class="tag-item">
                                         朴素贝叶斯                                    </span>
                                                            </div>
                                                                    </div>

                </li>
                            <li>
                    <div class="about-aticle-list">
                        <a href="https://blog.51cto.com/u_16099361/9539123"
                           data-report-query="xiangguantuijian&13" target="_blank" class="title">
                            <div class="tit">sklearn机器学习分类 sklearn算法</div>
                            <p> 一、K邻近算法的基本概念　　一个样本在特征空间中最邻近(距离)的K个样本大多数属于某一个类别，则该样本也属于这个类别。二、sklearn使用欧氏距离实现KNN算法     # 倒入sklearn库中的KNN算法类from sklearn.neighbors import KNeighborsClassifier# 创建KNN算法实例并设置K值KNN_classifier = KNeighb</p>
                        </a>
                        <!-- 标签页 -->
                                                    <div class="tag-box">
                                                                    <span class="tag-item">
                                         sklearn机器学习分类                                    </span>
                                                                    <span class="tag-item">
                                         人工智能                                    </span>
                                                                    <span class="tag-item">
                                         python                                    </span>
                                                                    <span class="tag-item">
                                         权重                                    </span>
                                                                    <span class="tag-item">
                                         数据                                    </span>
                                                            </div>
                                                                    </div>

                </li>
                            <li>
                    <div class="about-aticle-list">
                        <a href="https://blog.51cto.com/u_15127557/3497525"
                           data-report-query="xiangguantuijian&14" target="_blank" class="title">
                            <div class="tit">机器学习sklearn（三十）：模型保存</div>
                            <p> 在训练完 scikit-learn 模型之后，最好有一种方法来将模型持久化以备将来使用，而无需重新训练。 以下部分为您提供了有关如何使用 pickle 来持久化模型的示例。 在使用 pickle 序列化时，我们还将回顾一些安全性和可维护性方面的问题。 pickle的另一种方法是使用相关项目中列出的模</p>
                        </a>
                        <!-- 标签页 -->
                                                    <div class="tag-box">
                                                                    <span class="tag-item">
                                         数据                                    </span>
                                                                    <span class="tag-item">
                                         持久化                                    </span>
                                                                    <span class="tag-item">
                                         可维护性                                    </span>
                                                                    <span class="tag-item">
                                         python                                    </span>
                                                                    <span class="tag-item">
                                         加载                                    </span>
                                                            </div>
                                                                    </div>

                </li>
                            <li>
                    <div class="about-aticle-list">
                        <a href="https://blog.51cto.com/u_15049790/3498900"
                           data-report-query="xiangguantuijian&15" target="_blank" class="title">
                            <div class="tit">机器学习sklearn（三）：加载数据集(数据导入)</div>
                            <p> 1 Loading an example dataset scikit-learn comes with a few standard datasets, for instance the iris and digits datasets for classification and the dia</p>
                        </a>
                        <!-- 标签页 -->
                                                    <div class="tag-box">
                                                                    <span class="tag-item">
                                         git                                    </span>
                                                                    <span class="tag-item">
                                         sed                                    </span>
                                                                    <span class="tag-item">
                                         python                                    </span>
                                                                    <span class="tag-item">
                                         2d                                    </span>
                                                                    <span class="tag-item">
                                         lua                                    </span>
                                                            </div>
                                                                    </div>

                </li>
                            <li>
                    <div class="about-aticle-list">
                        <a href="https://blog.51cto.com/u_14344/9474980"
                           data-report-query="xiangguantuijian&16" target="_blank" class="title">
                            <div class="tit">机器学习 sklearn 模型评估 评估可视化 sklearn 模型选择</div>
                            <p> 这节内容很详细齐全，跟着里面的思路走，差不多就能把sklearn的用法以及建模的套路弄懂。一边学习一边理解一边操作一起开始sklearn的学习吧~sklearn介绍scikit-learn是数据挖掘与分析的简单而有效的工具。&nbsp;依赖于NumPy， SciPy和matplotlib。首先要知道的是sklearn中包含的主要功能有什么？classification 分类Regression 回</p>
                        </a>
                        <!-- 标签页 -->
                                                    <div class="tag-box">
                                                                    <span class="tag-item">
                                         数据                                    </span>
                                                                    <span class="tag-item">
                                         正则化                                    </span>
                                                                    <span class="tag-item">
                                         模型选择                                    </span>
                                                            </div>
                                                                    </div>

                </li>
                            <li>
                    <div class="about-aticle-list">
                        <a href="https://blog.51cto.com/u_16213588/9186214"
                           data-report-query="xiangguantuijian&17" target="_blank" class="title">
                            <div class="tit">sklearn 常用机器学习算法 sklearn入门</div>
                            <p> sklearn快速入门教程 – 准备工作1. 前言sklearn全称 scikit-learn，它是一个集成了目前市面上最常用的机器学习模型的库，使用起来非常轻松简单，因此获得了广泛的应用。从官网显示数据来看，这个项目始于2007年，工具箱在2011年正式发布，并且在机器学习顶级杂志 Journal of Machine Learning Research 发表了对应的论文。能在JMLR上发文章就</p>
                        </a>
                        <!-- 标签页 -->
                                                    <div class="tag-box">
                                                                    <span class="tag-item">
                                         sklearn 常用机器学习算法                                    </span>
                                                                    <span class="tag-item">
                                         sklearn                                    </span>
                                                                    <span class="tag-item">
                                         人工智能                                    </span>
                                                                    <span class="tag-item">
                                         机器学习                                    </span>
                                                                    <span class="tag-item">
                                         python                                    </span>
                                                            </div>
                                                                    </div>

                </li>
                            <li>
                    <div class="about-aticle-list">
                        <a href="https://blog.51cto.com/u_16213658/11090074"
                           data-report-query="xiangguantuijian&18" target="_blank" class="title">
                            <div class="tit">sklearn 机器学习 回归 sklearn 回归树</div>
                            <p> 回归树重要参数，属性和接口【1】criterion【2】交叉验证cross_val_score【3】实例：一维回归的图像绘制绘制图像 重要参数，属性和接口class sklearn.tree.DecisionTreeClassifier(criterion='mse'                                          ,splitter=&quot;random&quot;</p>
                        </a>
                        <!-- 标签页 -->
                                                    <div class="tag-box">
                                                                    <span class="tag-item">
                                         sklearn 机器学习 回归                                    </span>
                                                                    <span class="tag-item">
                                         机器学习                                    </span>
                                                                    <span class="tag-item">
                                         深度学习                                    </span>
                                                                    <span class="tag-item">
                                         二维                                    </span>
                                                                    <span class="tag-item">
                                         随机数                                    </span>
                                                            </div>
                                                                    </div>

                </li>
                            <li>
                    <div class="about-aticle-list">
                        <a href="https://blog.51cto.com/u_16099190/9141616"
                           data-report-query="xiangguantuijian&19" target="_blank" class="title">
                            <div class="tit">sklearn机器学习速 sklearn常用算法</div>
                            <p> 常用算法在Sklearn中的关键参数详解聚类算法K-Means算法基于Sklearn中的参数from sklearn.cluster import KMeansKMeans(n_clusters=8       , init='k-means++'       ,n_init=10       ,max_iter=300       , tol=0.0001       , preco</p>
                        </a>
                        <!-- 标签页 -->
                                                    <div class="tag-box">
                                                                    <span class="tag-item">
                                         sklearn机器学习速                                    </span>
                                                                    <span class="tag-item">
                                         sklearn                                    </span>
                                                                    <span class="tag-item">
                                         python                                    </span>
                                                                    <span class="tag-item">
                                         算法                                    </span>
                                                                    <span class="tag-item">
                                         分类算法                                    </span>
                                                            </div>
                                                                    </div>

                </li>
                            <li>
                    <div class="about-aticle-list">
                        <a href="https://blog.51cto.com/u_16099346/11094942"
                           data-report-query="xiangguantuijian&20" target="_blank" class="title">
                            <div class="tit">机器学习sklearn入门基础学习 sklearn算法</div>
                            <p> sklearn数据集数据集划分sklearn机器学习算法的实现-估计器在sklearn中，估计器(estimator)是一个重要的角色，分类器和回归器都属于estimator，是一类实现了算法的API1、用于分类的估计器：sklearn.neighbors k-近邻算法sklearn.naive_bayes 贝叶斯sklearn.linear_model.LogisticRegression 逻辑</p>
                        </a>
                        <!-- 标签页 -->
                                                    <div class="tag-box">
                                                                    <span class="tag-item">
                                         机器学习sklearn入门基础学习                                    </span>
                                                                    <span class="tag-item">
                                         python                                    </span>
                                                                    <span class="tag-item">
                                         机器学习                                    </span>
                                                                    <span class="tag-item">
                                         决策树                                    </span>
                                                                    <span class="tag-item">
                                         算法                                    </span>
                                                            </div>
                                                                    </div>

                </li>
                            <li>
                    <div class="about-aticle-list">
                        <a href="https://blog.51cto.com/u_16099203/11486289"
                           data-report-query="xiangguantuijian&21" target="_blank" class="title">
                            <div class="tit">mes供应商 德</div>
                            <p> 先别看企业，看需求。上层的ERP是哪家的，支持哪些接口，或者说是二次开发的难度大不大，然后对接有没有WMS，仓储的管理分配，需不需要MES做深度介入，APS自动排程有没有上，算法和信息来源的关系，有没有进行机器学习和喂数据，需要哪方面的数据，DCS目前做了哪些事情，痛点和亟待解决的硬伤在哪些方面。TPM系统有没有上，有没有设备管理方面的需求，关于产品生命周期的一些考量，工艺部门是否对数据追溯有一些</p>
                        </a>
                        <!-- 标签页 -->
                                                    <div class="tag-box">
                                                                    <span class="tag-item">
                                         mes供应商 德                                    </span>
                                                                    <span class="tag-item">
                                         主流mes厂商                                    </span>
                                                                    <span class="tag-item">
                                         生命周期                                    </span>
                                                                    <span class="tag-item">
                                         数据                                    </span>
                                                                    <span class="tag-item">
                                         解决方案                                    </span>
                                                            </div>
                                                                    </div>

                </li>
                            <li>
                    <div class="about-aticle-list">
                        <a href="https://blog.51cto.com/u_16213673/11490398"
                           data-report-query="xiangguantuijian&22" target="_blank" class="title">
                            <div class="tit">java获取日期差值分钟 java计算日期之差</div>
                            <p> 这篇文章主要为大家详细总结了常用的java日期比较和日期计算方法,具有一定的参考价值，感兴趣的小伙伴们可以参考一下&nbsp;1.获取两个日期的差值（返回的是时间戳）/**
	 * 这个是用来获取两个日期的差值的
	 * 
	 * @return 差值
	 */
	public static Long getSubTime(String date3,String date4) {
		Date d</p>
                        </a>
                        <!-- 标签页 -->
                                                    <div class="tag-box">
                                                                    <span class="tag-item">
                                         java获取日期差值分钟                                    </span>
                                                                    <span class="tag-item">
                                         java日期比较                                    </span>
                                                                    <span class="tag-item">
                                         日期计算                                    </span>
                                                                    <span class="tag-item">
                                         System                                    </span>
                                                                    <span class="tag-item">
                                         java                                    </span>
                                                            </div>
                                                                    </div>

                </li>
                            <li>
                    <div class="about-aticle-list">
                        <a href="https://blog.51cto.com/u_16099169/11494736"
                           data-report-query="xiangguantuijian&23" target="_blank" class="title">
                            <div class="tit">archive_command用设置吗</div>
                            <p> 配置数据库归档模式（ARCHIVELOG/NOARCHIVELOG）本文介绍如何启动或关闭数据库归档模式&nbsp;Oracle数据库可以运行在2种模式下:归档模式(archivelog)和非归档模式(noarchivelog)&nbsp;&nbsp;归档与非归档的区别请参考ORACLE相关文档。&nbsp;&nbsp;数据库循环使用LOG文件，若数据库处于“非归档日志”模式，当LOG文件被使用后</p>
                        </a>
                        <!-- 标签页 -->
                                                    <div class="tag-box">
                                                                    <span class="tag-item">
                                         archive_command用设置吗                                    </span>
                                                                    <span class="tag-item">
                                         数据库                                    </span>
                                                                    <span class="tag-item">
                                         SQL                                    </span>
                                                                    <span class="tag-item">
                                         hive                                    </span>
                                                            </div>
                                                                    </div>

                </li>
                            <li>
                    <div class="about-aticle-list">
                        <a href="https://blog.51cto.com/u_16213615/11494749"
                           data-report-query="xiangguantuijian&24" target="_blank" class="title">
                            <div class="tit">基础java代码题 java基础编程题及答案</div>
                            <p> Java入门——（1）Java编程基础第二章 Java编程基础&nbsp;JAVA 代码的基本格式：修饰符 class 类名{程序代码}&nbsp;2.1关键字：赋予了特殊含义的单词。&nbsp;2.2标识符：在程序中定义的一些名称。比如：类名a-z 0-9 _ $数字不可以开头，不可以使用关键字，一般首字母大写。&nbsp;2.3注释：注解说明程序的文字。作用：1、对程序进行说明。&nbsp; </p>
                        </a>
                        <!-- 标签页 -->
                                                    <div class="tag-box">
                                                                    <span class="tag-item">
                                         基础java代码题                                    </span>
                                                                    <span class="tag-item">
                                         运算符                                    </span>
                                                                    <span class="tag-item">
                                         Java                                    </span>
                                                                    <span class="tag-item">
                                         赋值                                    </span>
                                                            </div>
                                                                    </div>

                </li>
                            <li>
                    <div class="about-aticle-list">
                        <a href="https://blog.51cto.com/u_16099270/11500225"
                           data-report-query="" target="_blank" class="title">
                            <div class="tit">java kafka根据topic查寻数据 kafka查找数据的过程</div>
                            <p> 最近有学习些Kafak的源码，想给大家分享下Kafak中改进的二分查找算法。二分查找，是每个程序员都应掌握的基础算法，而Kafka是如何改进二分查找来应用于自己的场景中，这很值得我们了解学习。由于Kafak把二分查找应用于索引查找的场景中，所以本文会先对Kafka的日志结构和索引进行简单的介绍。在Kafak中，消息以日志的形式保存，每个日志其实就是一个文件夹，且存有多个日志段，一个日志段指的是文件</p>
                        </a>
                        <!-- 标签页 -->
                                                    <div class="tag-box">
                                                                    <span class="tag-item">
                                         算法                                    </span>
                                                                    <span class="tag-item">
                                         java                                    </span>
                                                                    <span class="tag-item">
                                         python                                    </span>
                                                                    <span class="tag-item">
                                         redis                                    </span>
                                                                    <span class="tag-item">
                                         mysql                                    </span>
                                                            </div>
                                                                    </div>

                </li>
                    </ul>
    </section>

</article>
        
<aside class="detail-content-right">
    <!--右上角统计-->
    <section class="common-section common-spacing mb24 user-intr">
        <div class="user-content">
            <div class="top">
                <div class="avatar">
                    <div class="avatar-img">
                        <a href="https://blog.51cto.com/u_16213600" target="_blank" rel="nofollow">
                            <img class="is-vip-img is-vip-img-4" data-uid="16203600" src="https://ucenter.51cto.com/images/noavatar_middle.gif">
                        </a>
                    </div>
                </div>
                <div class="clearfix username">
                    <a href="https://blog.51cto.com/u_16213600" target="_blank"><span class="blog-user" title="mob64ca13fc5fb6">mob64ca13fc5fb6</span></a>
                    <div class="icon">
                        <ul class="clearfix detail-list"></ul>
                    </div>
                </div>
            </div>
            <div class="identify-list"></div>
            <div class="bottom" id="userStat"></div>
            <div id="medalListBox" class="medal-list"></div>
            <div class="operating clearfix ">
                                                            <a id="checkFollow2_16203600" class="follow-1 checkFollow on" rel="nofollow">关注</a>
                                                    <button class="sx" data="https://home.51cto.com/space?uid=16203600" id="ToSx"><a href="javascript:;" rel="nofollow"><i class="iconblog blogsixin"></i>私信</a></button>
            </div>
        </div>
    </section>
    <section class="mb24 blogger-ranking">
    </section>
    <!-- 分类列表 -->
        <!-- 近期文章 -->
            <section class="common-section common-spacing mb24">
            <div class="clearfix common-sub-title">
                <strong title="近期文章">近期文章</strong>
            </div>
            <ul class="common-list" id="updatelist">
                                    <li>
                        <a href="https://blog.51cto.com/u_15130867/11512749" target="_blank" title="【YashanDB培训心得】--国产崖山数据库YCA认证学习day4">1.【YashanDB培训心得】--国产崖山数据库YCA认证学习day4</a>
                    </li>
                                    <li>
                        <a href="https://blog.51cto.com/u_15933803/11512952" target="_blank" title="Linux-进程控制（1）">2.Linux-进程控制（1）</a>
                    </li>
                                    <li>
                        <a href="https://blog.51cto.com/u_16536418/11512957" target="_blank" title="蓝易云服务器 - linux网络连通性判断工具mtr">3.蓝易云服务器 - linux网络连通性判断工具mtr</a>
                    </li>
                                    <li>
                        <a href="https://blog.51cto.com/u_16847915/11512844" target="_blank" title="无需标注即可训练，自监督学习框架实现大量未标注毫米波雷达数据预训练自动驾驶感知任务">4.无需标注即可训练，自监督学习框架实现大量未标注毫米波雷达数据预训练自动驾驶感知任务</a>
                    </li>
                                    <li>
                        <a href="https://blog.51cto.com/u_16847915/11512807" target="_blank" title="降本增效CRKD：通过跨模态知识蒸馏增强相机与毫米波雷达目标检测精度">5.降本增效CRKD：通过跨模态知识蒸馏增强相机与毫米波雷达目标检测精度</a>
                    </li>
                            </ul>
        </section>
        <section class="common-fix">
        <!-- 新人活动 -->
        <a href="https://blog.51cto.com/activity-first-publish#xiang" target="_blank" class="ac-box mb24">
            <img ps-lazy="https://s2.51cto.com/blog/activity/bride/DetailsBride.gif?x-oss-process=image/ignore-error,1" src="https://s2.51cto.com/images/100/base/empty.png?x-oss-process=image/format,webp/ignore-error,1" alt="新人福利">
        </a>

        <!-- 文章目录 -->
                    <div class="common-section common-spacing table-contents common-content-directory">
                <div class="clearfix common-sub-title">
                    <strong title="文章目录">文章目录</strong>
                </div>
                <div class="directory" id="directory-parent1">
                    <ul class="directory-list" id="directory-right">
                                                                                    <li  class="lv3" >
                                    <div class="title">
                                        <span data-id="#h0">
                                                                                        1. 获取数据                                        </span>
                                    </div>
                                </li>
                                                                                                                <li  class="lv4" >
                                    <div class="title">
                                        <span data-id="#h1">
                                                                                        1.1 导入sklearn数据集                                        </span>
                                    </div>
                                </li>
                                                                                                                <li  class="lv4" >
                                    <div class="title">
                                        <span data-id="#h2">
                                                                                        1.2 创建数据集                                        </span>
                                    </div>
                                </li>
                                                                                                                <li  class="lv3" >
                                    <div class="title">
                                        <span data-id="#h3">
                                                                                        2. 数据预处理                                        </span>
                                    </div>
                                </li>
                                                                                                                <li  class="lv4" >
                                    <div class="title">
                                        <span data-id="#h4">
                                                                                        2.1 数据归一化                                        </span>
                                    </div>
                                </li>
                                                                                                                <li  class="lv4" >
                                    <div class="title">
                                        <span data-id="#h5">
                                                                                        2.2 正则化（normalize）                                        </span>
                                    </div>
                                </li>
                                                                                                                <li  class="lv4" >
                                    <div class="title">
                                        <span data-id="#h6">
                                                                                        &nbsp;2.3 one-hot编码                                        </span>
                                    </div>
                                </li>
                                                                                                                <li  class="lv3" >
                                    <div class="title">
                                        <span data-id="#h7">
                                                                                        3. 数据集拆分                                        </span>
                                    </div>
                                </li>
                                                                                                                <li  class="lv3" >
                                    <div class="title">
                                        <span data-id="#h8">
                                                                                        4. 定义模型                                        </span>
                                    </div>
                                </li>
                                                                                                                <li  class="lv4" >
                                    <div class="title">
                                        <span data-id="#h9">
                                                                                        &nbsp;4.1 线性回归                                        </span>
                                    </div>
                                </li>
                                                                                                                <li  class="lv4" >
                                    <div class="title">
                                        <span data-id="#h10">
                                                                                        &nbsp;4.2 逻辑回归LR                                        </span>
                                    </div>
                                </li>
                                                                                                                <li  class="lv4" >
                                    <div class="title">
                                        <span data-id="#h11">
                                                                                        &nbsp;4.3 朴素贝叶斯算法NB                                        </span>
                                    </div>
                                </li>
                                                                                                                <li  class="lv4" >
                                    <div class="title">
                                        <span data-id="#h12">
                                                                                        &nbsp;4.4 决策树DT                                        </span>
                                    </div>
                                </li>
                                                                                                                <li  class="lv4" >
                                    <div class="title">
                                        <span data-id="#h13">
                                                                                        4.5 支持向量机SVM                                        </span>
                                    </div>
                                </li>
                                                                                                                <li  class="lv4" >
                                    <div class="title">
                                        <span data-id="#h14">
                                                                                        &nbsp;4.6 k近邻算法KNN                                        </span>
                                    </div>
                                </li>
                                                                                                                <li  class="lv4" >
                                    <div class="title">
                                        <span data-id="#h15">
                                                                                        4.7 多层感知机（神经网络）                                        </span>
                                    </div>
                                </li>
                                                                                                                <li  class="lv3" >
                                    <div class="title">
                                        <span data-id="#h16">
                                                                                        5. 模型评估与选择篇                                        </span>
                                    </div>
                                </li>
                                                                                                                <li  class="lv4" >
                                    <div class="title">
                                        <span data-id="#h17">
                                                                                        5.1 交叉验证                                        </span>
                                    </div>
                                </li>
                                                                                                                <li  class="lv4" >
                                    <div class="title">
                                        <span data-id="#h18">
                                                                                        5.2 检验曲线                                        </span>
                                    </div>
                                </li>
                                                                                                                <li  class="lv3" >
                                    <div class="title">
                                        <span data-id="#h19">
                                                                                        6. 保存模型                                        </span>
                                    </div>
                                </li>
                                                                                                                <li  class="lv4" >
                                    <div class="title">
                                        <span data-id="#h20">
                                                                                        6.1 保存为pickle文件                                        </span>
                                    </div>
                                </li>
                                                                                                                <li  class="lv4" >
                                    <div class="title">
                                        <span data-id="#h21">
                                                                                        6.2 sklearn自带方法joblib                                        </span>
                                    </div>
                                </li>
                                                                        </ul>
                </div>
                <div class="table-contents"></div>
            </div>
            </section>



</aside>
    </div>
    <!--悬浮小菜单-->
        <aside class="minmenu">
        <ul>
            <li class="signIn" signId="2">
                <button id="signIn">  每日签到</button>
            </li>
            <li class="editArticle" editId="2">
                <!-- <div class="new_bloger ">新人福利</div> -->
                 <button id="editArticle"><i class="iconblog blogxiewz"></i></button>
            </li>
            <li class="feedback">
              <a href="https://blog.51cto.com/feedback?utm_medium=rightsuspension" target="_blank">意见<br />反馈</a>
            </li>
            <li class="scrollToTop">
              <i class="iconblog bloggengduo1"></i>
            </li>
        </ul>
    </aside>
</div>
<!-- 蒙层 -->
<div class="Mask"></div>

<div class="report-dialog-root">
    <div class="report-dialog-container">
        <p class="report-dialog-title">举报文章</p>
        <div class="report-type-container model-split_top" data-type="0" id="report-specific-type">
            <p class="report-type-tit">请选择举报类型</p>
            <div class="report-type-enmu">
                <span class="report-type-item type-item_first" data-type="1">内容侵权</span>
                <span class="report-type-item type-item_first item-split" data-type="2">涉嫌营销</span>
                <span class="report-type-item type-item_first item-split" data-type="3">内容抄袭</span>
                <span class="report-type-item type-item_first item-split" data-type="4">违法信息</span>
                <span class="report-type-item type-item_first item-split" data-type="5">其他</span>
            </div>
        </div>
        <div class="report-type-container model-split_top report-hide-model" id="report-specific-reasons" data-type="0">
            <p class="report-type-tit">具体原因</p>
            <div class="report-type-enmu">
                <span class="report-type-item type-item_second" data-type="1">包含不真实信息</span>
                <span class="report-type-item type-item_second item-split" data-type="2">涉及个人隐私</span>
            </div>
        </div>
        <div class="report-type-container model-split_top report-hide-model" id="report-original-link">
            <p class="report-type-tit">原文链接（必填）</p>
            <input type="text" placeholder="请输入被侵权的原文链接" class="report-orgin_input"/>
        </div>
        <div class="report-type-container model-split_top textarea-content">
            <p class="report-type-tit">补充说明</p>
            <textarea maxlength="200" class="report-reason_textarea" placeholder="请详细描述您的举报内容" id="report-more-info"></textarea>
            <p class="report-textarea-tip"><span class="tip-left">0</span><span>/200</span></p>
        </div>
        <div class="report-type-container">
            <p class="report-type-tit">上传截图</p>
            <div class="report-img-container">
                <i class="iconblog blogtianjiabeifen report-add-icon"></i>
                <input type="file" accept="image/jpg,image/jpeg,image/png" name="file" class="repot-btn-select" onchange="selectImg(this)"></input>
            </div>
            <p class="report-img_rule">格式支持JPEG/PNG/JPG，图片不超过1.9M</p>
            <div class="report-img-show" >
                <img src="" alt="" id="report-img">
                <div class="report-img-close">
                    <i class="iconblog bloga-shanchutupian report-close-icon"></i>
                </div>
            </div>
        </div>
        <div class="report-btn-container">
            <button class="report-btn-cancel">取消</button>
            <button class="report-btn-concert">确认</button>
        </div>
        <div class="report-warm-tip report-hide-model">
            已经收到您得举报信息，我们会尽快审核
        </div>
    </div>
</div>
<div class="imgViewDom disnone" style="display: none;">
    <div class="img-content"></div>
</div>
<!--左边悬浮操作项-->
<aside class="action-aside action-aside-left">
    <div class="inner">
        <ul>
                        <li>
                <strong class="is-praise  " type="1" blog_id="10820896" userid='16203600'>
                    <a href="javascript:;"><i></i></a>
                    <span><b class="praise-num"></b>赞</span>
                </strong>
            </li>
            <li>
                <strong class="favorites-opt">
                    <a href="javascript:;"><i></i></a>
                    <span><b class="favorites-num"></b>收藏</span>
                </strong>
            </li>
            <li>
                <strong class="Topraise">
                    <a href="javascript:;"><i class="iconblog blogpinglun"></i></a>
                    <span><b class="comments_num"></b>评论</span>
                </strong>
            </li>
            <li class="share">
                <strong class="">
                    <a href="javascript:;"><i class="iconblog blogfen"></i></a>
                    <span>分享</span>
                </strong>
            </li>
        </ul>
    </div>
</aside>
    <div class="modal-bg">
         <div class="modal">
            <i class="iconblog blogquxiao18 close-btn"></i>
            <div class="content " ></div>
            <div class="tip-box">如有误判或任何疑问，可联系 <a  href="javascript:;" class="zhiCustomBtn">「小助手微信：cto51cto」</a><span class="appeal_text">申诉及反馈</span>。</div>
             <div class="know-box">
                <span class="know-btn">我知道了</span>
             </div>

         </div>
    </div>
<div class="dialog-box">
    <div class="mask"></div>
    <div class="body">
        <div id="close" class="close"></div>
        <div id="medalListBox2"></div>
    </div>
</div>
<div class="dialog-box-small">
    <div class="mask"></div>
    <div class="body">
        <div id="close" class="close"></div>
        <div id="medalBox2" class="medal-list">
        </div>
    </div>
</div></div>
  <header class="home-top">
    <div class="Page">
        <div class="top_box">
            <div class="left_nav">
                               <div class="item-lf "><a class="top"  href="https://www.51cto.com" target="_blank" rel="nofollow"   data-id="1"   target="_blank"> 51CTO首页                                </a></div>
                               <div class="item-lf  hot"><a class="top"  href="https://www.51cto.com/aigc/" target="_blank" rel="nofollow"   data-id="2"   target="_blank"> AI.x社区                                    <span class="hot-div" ><img src="https://s9.51cto.com/oss/202404/07/2331c9f60a7383b36c1333314be286f249b5b3.png" alt=""></span>
                                </a></div>
                               <div class="item-lf "><a class="top"  href="https://blog.51cto.com/" target="_blank" rel="nofollow"   data-id="3"   target="_blank"> 博客                                </a></div>
                               <div class="item-lf "><a class="subweb"  href="https://edu.51cto.com/?utm_source=hometop" target="_blank" rel="nofollow"   data-id="4"   target="_blank"> 学堂                                </a></div>
                               <div class="item-lf "><a class="subweb"  href="https://e.51cto.com/?utm_platform=pc&utm_medi-um=51cto&utm_source=zhuzhan&utm_content=sy_topbar" target="_blank" rel="nofollow"   data-id="5"   target="_blank"> 精品班                                </a></div>
                               <div class="item-lf "><a class="top"  href="https://edu.51cto.com/surl=o0bwJ2" target="_blank" rel="nofollow"   data-id="33"   target="_blank"> 免费课                                </a></div>
                               <div class="item-lf "><a class="subweb"  href="https://b.51cto.com/index?utm_source=hometop" target="_blank" rel="nofollow"   data-id="6"   target="_blank"> 企业培训                                </a></div>
                               <div class="item-lf "><a class="subweb"  href="https://ost.51cto.com/?utm_source=hometop" target="_blank" rel="nofollow"   data-id="9"   target="_blank"> 鸿蒙开发者社区                                </a></div>
                               <div class="item-lf "><a class="top"  href="https://51cto.com/wot/?utm_source=dhl" target="_blank" rel="nofollow"   data-id="10"   target="_blank"> WOT技术大会                                </a></div>
                               <div class="item-lf "><a class="top"  href="https://www.51cto.com/act/aigc/awards" target="_blank" rel="nofollow"   data-id="34"   target="_blank"> AIGC创新中国行                                </a></div>
                               <div class="item-lf  hot"><a class="top"  href="https://edu.51cto.com/cert/?utm_platform=pc&utm_medium=51cto&utm_source=edu&utm_content=dh" target="_blank" rel="nofollow"   data-id="35"   target="_blank"> IT证书                                    <span class="hot-div" ><img src="https://s2.51cto.com/oss/202405/15/91545ec31a576825683629ce5f37d4b8a6512c.png" alt=""></span>
                                </a></div>
                           </div>
            <div class="top_right">
                <div class="item-rt"><a href="http://so.51cto.com/?keywords=&amp;sort=time" target="_blank" class="search-top" rel="nofollow"><i class="iconblog blogsou blog-search"></i></a></div>
                <div class="item-rt"><span class="wechatlist" data-id="wechatImageList">公众号矩阵</span></div>
                <div class="item-rt"><span class="applist" data-id="appImageList">移动端</span></div>

            </div>
        </div>
    </div>
    <div class="nav-more-container "  >
        <div class="Page nav-contant-box" >
                                                                                                                                   <div class="nav-contant " data-id="4" >
                                           <a href="https://edu.51cto.com/videolist/index.html?utm_platform=pc&utm_medium=51cto&utm_source=zhuzhan&utm_content=dh" target="_blank">短视频</a>
                                              <a href="https://edu.51cto.com/courselist/index-zh5.html?utm_source=hometop" target="_blank">免费课程</a>
                                              <a href="https://edu.51cto.com/ranking/index.html?utm_source=hometop" target="_blank">课程排行</a>
                                              <a href="https://e.51cto.com/ncamp/list?utm_platform=pc&utm_medium=51cto&utm_source=zhuzhan&utm_content=sy_topbar&rtm_frd=13" target="_blank">直播课</a>
                                              <a href="https://e.51cto.com/rk/?utm_platform=pc&utm_medi-um=51cto&utm_source=zhuzhan&utm_content=sy_topbar&rtm_frd=14" target="_blank">软考学堂</a>
                                            </div>
                                                                  <div class="nav-contant " data-id="5" >
                                           <a href="https://e.51cto.com/wejob/list?utm_platform=pc&utm_medi-um=51cto&utm_source=zhuzhan&utm_content=sy_topbar" target="_blank">全部课程</a>
                                              <a href="https://e.51cto.com/wejob/list?pid=5&utm_platform=pc&utm_medium=51cto&utm_source=zhuzhan&utm_content=sy_topbar&rtm_frd=41" target="_blank">厂商认证</a>
                                              <a href="https://e.51cto.com/wejob/list?pid=1&utm_platform=pc&utm_medium=51cto&utm_source=zhuzhan&utm_content=sy_topbar&rtm_frd=42" target="_blank">IT技术</a>
                                              <a href="https://e.51cto.com/rk/?utm_platform=pc&utm_medium=51cto&utm_source=zhuzhan&utm_content=sy_xyzq_rightwzl&rtm_frd=07&utm_medium=51cto&utm_source=zhuzhan&utm_content=sy_topbar&rtm_frd=43" target="_blank">2024年软考</a>
                                              <a href="https://e.51cto.com/wejob/list?pid=33&utm_platform=pc&utm_medium=51cto&utm_source=zhuzhan&utm_content=sy_topbar&rtm_frd=44" target="_blank">PMP项目管理</a>
                                              <a href="https://edu.51cto.com/rk/" target="_blank">软考资讯</a>
                                            </div>
                                                                                              <div class="nav-contant " data-id="6" >
                                           <a href="https://b.51cto.com/index?utm_source=hometop" target="_blank">在线学习</a>
                                            </div>
                                                                  <div class="nav-contant " data-id="9" >
                                           <a href="https://ost.51cto.com/postlist" target="_blank">文章</a>
                                              <a href="https://ost.51cto.com/resource" target="_blank">资源</a>
                                              <a href="https://ost.51cto.com/answerlist" target="_blank">问答</a>
                                              <a href="https://ost.51cto.com/study" target="_blank">课堂</a>
                                              <a href="https://ost.51cto.com/column" target="_blank">专栏</a>
                                              <a href="https://ost.51cto.com/activity" target="_blank">直播</a>
                                            </div>
                                                                                                                                                    <div class="nav-contant wechatImageList" data-id="wechatImageList" >
                                           <div class="ewmbox"><div class="imgbox"><img src="https://s5.51cto.com/oss/202302/07/862966771f540df82857144db74b27ee5b4b23.jpeg"/></div><span class="txt">51CTO</span></div>
                                              <div class="ewmbox"><div class="imgbox"><img src="https://s4.51cto.com/oss/202302/07/d53d67c771f5cc42bac359bceb138c4cb1713b.jpg"/></div><span class="txt">鸿蒙开发者社区</span></div>
                                              <div class="ewmbox"><div class="imgbox"><img src="https://s6.51cto.com/oss/202302/07/58786f9973e5e929ef521783e1ee40413b04de.jpeg"/></div><span class="txt">51CTO技术栈</span></div>
                                              <div class="ewmbox"><div class="imgbox"><img src="https://s3.51cto.com/oss/202302/07/c77c03983d48589b1af789dfc284acb6a7c529.jpeg"/></div><span class="txt">51CTO官微</span></div>
                                              <div class="ewmbox"><div class="imgbox"><img src="https://s4.51cto.com/oss/202302/07/544d71641d983430fc9955636e625e6bb21ff9.jpeg"/></div><span class="txt">51CTO学堂</span></div>
                                              <div class="ewmbox"><div class="imgbox"><img src="https://s3.51cto.com/oss/202302/07/f1bd61e720bf669483d941a8486c124f32c451.jpeg"/></div><span class="txt">51CTO博客</span></div>
                                              <div class="ewmbox"><div class="imgbox"><img src="https://s9.51cto.com/oss/202302/07/4719e7b27bae3af5e33552481b6cb913288b01.jpeg"/></div><span class="txt">CTO训练营</span></div>
                                              <div class="ewmbox"><div class="imgbox"><img src="https://s5.51cto.com/oss/202302/07/61a991f484307eed2fe9356cc215c4d8f2dc0f.jpg"/></div><span class="txt">鸿蒙开发者社区订阅号</span></div>
                                              <div class="ewmbox"><div class="imgbox"><img src="https://s3.51cto.com/oss/202405/09/5576f843208b7973bf3965a2cdfd62e4a86054.png"/></div><span class="txt">51CTO题库小程序</span></div>
                                            </div>
                                                        <div class="nav-contant appImageList" data-id="appImageList" >
                                           <div class="ewmbox"><div class="imgbox"><img src="https://s8.51cto.com/oss/202302/07/24febb8152cc24e264e642f8cb8bb515efea26.jpeg"/></div><span class="txt">51CTO学堂APP</span></div>
                                              <div class="ewmbox"><div class="imgbox"><img src="https://s9.51cto.com/oss/202302/07/43cca7d0489cc5d1f70060be760bde17d552e2.jpeg"/></div><span class="txt">51CTO学堂企业版APP</span></div>
                                              <div class="ewmbox"><div class="imgbox"><img src="https://s5.51cto.com/oss/202302/07/c4d2220826890472539671d7c428f0c0ee9451.jpg"/></div><span class="txt">鸿蒙开发者社区视频号</span></div>
                                            </div>
                        </div>
    </div>
</header>
<div class="Header  " style="height:70px;">
     <div class="header-content">
        <div class="header-left">
                            <div class="Logo"><a href="https://blog.51cto.com/"><img src="https://s2.51cto.com/media/2024/blog/logo.png?x-oss-process=image/format,webp/ignore-error,1" alt="51CTO博客" width="100" title="51CTO博客">
                    <h2>51CTO博客</h2>
                </a></div>
                  <ul class="Navigates  commonhide">
            <li ><a href="https://blog.51cto.com/">首页</a>
                <div class="spam-classifications" style="display:none;">
                    <div class="spam-classifications-content">
                        <div class="classification-ipc" id="classification-ipc"></div>
                        <div class="classification-primary-list-box" id="classification-primary-list-box"></div>

                    </div>
                </div>
            </li>
            <li ><a href="https://blog.51cto.com/nav/following">关注</a></li>
            <li ><a href="https://blog.51cto.com/ranking/hot/aigc">排行榜</a><img class="hot-img" src="https://s2.51cto.com/blog/ai.png?x-oss-process=image/format,webp/ignore-error,1" alt="排行榜"></li>
            <li class="">
                <a href="https://blog.51cto.com/cloumn/index" >订阅专栏</a>
            </li>
                            <li class="first"><a href="https://blog.51cto.com/activity-first-publish#shouye" target="_blank"><img  alt="新人福利" src="https://s2.51cto.com/images/100/blog/activity/first2.gif?x-oss-process=image/ignore-error,1"></a></li>
                        </ul>
     </div>
        <ul class="header-right">
                <li class="search">
                    <form class=" form-search" method='get' action="https://blog.51cto.com/search/result" target="_blank" novalidate>
                        <input type="text" name="q" placeholder="搜索文章、作者" id="TopSearchInput" autocomplete="off" required>
                         <i class="iconblog  bloga-shanchutupian" ></i>
                        <button class="iconblog blogsou" id="TopSearchBtn" ></button>
                    </form>
                    <div class="focusSelect focusSelect_his">

                        <div class="searchHistoryList">
                            <div class="clearfix hishead">搜索历史
                                <span class="clearhis"><i class="iconblog blogshanchu18 "></i>清空</span>
                            </div>
                            <div class="hisitem-wrap"></div>
                        </div>

                        <div class="hotList">
                            <div class="clearfix hishead">热门搜索</div>
                            <div class="hot-wrap"></div>
                        </div>

                    </div>

                    <div class="focusSelect focusSelect_key">
                        <div class="keyitem-wrap">

                        </div>
                        <div class="clearfix checkSearchResult">
                            <span>查看【</span>
                            <span class="checkKey"></span>
                            <span>】的结果</span>
                        </div>
                    </div>
                </li>
                                      <li class="write commonhide">
                       
                        <a href="javascript:;" id="toPublish" onClick="Login({scene:'write1'})" rel="nofollow"> <i class="iconblog  blogxiewenzhang"></i>写文章</a></li>
                      <li class="creative"><a href="/creative-center/index">创作中心</a><a href="/creative-center/task" class="task"></a></li>
                                                         <li class="logins">
                    <a href="https://home.51cto.com/index?from_service=blog&scene=login1&reback=https://blog.51cto.com/u_16213600/10820896" target="_self" class="clearfix" rel="nofollow"><span class="fl">登录</span><b class="fgline fl"></b><span class="fl">注册</span></a>
                </li>
                    </ul>

    </div>
</div>
    <!-- if publish show -->
    <div class="Footer">
        <div class="Page ">
            <div class="fl">
                <a href="https://blog.51cto.com/" class="Logo"><img src="https://s2.51cto.com/images/100/blog/logo4.png?x-oss-process=image/format,webp/ignore-error,1" alt="51CTO博客" width="214" title="51CTO博客"></a>
                <p class="copy">Copyright &copy; 2005-2024 <a href="https://www.51CTO.com" target="_blank">51CTO.COM</a>
                    版权所有 京ICP证060544号</p>
            </div>

            <dl class="foot_ab fr">
                <dt>关于我们</dt>
                <dd>
                    <table class="aboutList">
                        <tr>
                            <td><a href="https://blog.51cto.com/51ctoblog" target="_blank">官方博客</a></td>
                            <td><a href="https://blog.51cto.com/nav" target="_blank">全部文章</a></td>
                            <td><a href="https://blog.51cto.com/topic/all" target="_blank">热门标签</a></td>
                            <td ><a href="https://blog.51cto.com/class-blog/index" target="_blank" data-v-6e9e21b4="">班级博客</a></td>
                        </tr>
                        <tr>
                            <td><a href="https://www.51cto.com/about/aboutus.html" target="_blank">了解我们</a></td>
                            <td><a href="https://www.51cto.com/about/map.html" target="_blank">网站地图</a></td>
                            <td><a href="https://blog.51cto.com/feedback?utm_medium=aboutus2" target="_blank">意见反馈</a></td>

                        </tr>
                    </table>
                </dd>
            </dl>


            <dl class="foot_link fr">
                <dt>友情链接</dt>
                <dd>
                    <table class="aboutList-2">
                        <tr>
                            <td><a href="https://ost.51cto.com/?utm_source=blogsitemap" target="_blank">鸿蒙开发者社区</a></td>
                            <td><a href="https://edu.51cto.com/" target="_blank">51CTO学堂</a></td>
                        </tr>
                        <tr>
                            <td><a href="https://www.51cto.com" target="_blank">51CTO</a></td>
                            <td><a href="https://edu.51cto.com/rk/" target="_blank">软考资讯</a></td>
                        </tr>
                    </table>
                </dd>
            </dl>

        </div>
    </div>
    

<script>
    var userId="";
var uid="";
var user_id=16203600;
var isLogin=0;
var imgpath="https://s2.51cto.com/";
var BLOG_URL="https://blog.51cto.com/";
var HOME_URL="https://home.51cto.com/";
var STATICPATH="https://static2.51cto.com/edu/";
var SA_SERVER_URL_YM="https://sc.51cto.com/sa?project=production";
var cururl="https://blog.51cto.com/u_16213600/10820896";
var login_url="https://home.51cto.com/mobile/client-login?reback=https://blog.51cto.com/u_16213600/10820896";
var praise_url="https://blog.51cto.com/praise/praise";
var qrcodeSid="";
var qr_code="";
var router="blog/index";
var csrfParam="_csrf";
var csrfToken="gndgE6EsufWIyFRj7T4bPFoYy2eLFUVDPG1FzSIVWF2RJugqdDSqRNpAXpURsov5yu20qlo_VW5-AOBV7hMGNA==";
var is_load=0;
var uc_url="https://ucenter.51cto.com/";
var blog_url="https://blog.51cto.com/";
var isBuy=1;
var isPc=0;
var writeMessage="机器学习sklearn 模型导出 sklearn导入数据\r\nhttps:\/\/blog.51cto.com\/u_16213600\/10820896";
var isCodeCopy=0;
var cid="";
var fid=0;
var commentListPage="";
var originalUrl="https://blog.51cto.com/u_16213600/original";
var followersUrl="https://blog.51cto.com/u_16213600/followers";
var translateUrl="https://blog.51cto.com/u_16213600/translate";
var reproduceUrl="https://blog.51cto.com/u_16213600/reproduce";
var followingUrl="https://blog.51cto.com/u_16213600/following";
var page="detail";
var tipStatus=1;
var addReply_url="https://blog.51cto.com/addBlogComment";
var removeUrl="https://blog.51cto.com/delBlogComment";
var blog_id=10820896;
var is_comment=0;
var comment_list="https://blog.51cto.com/getBlogCommentList";
var index_url="https://blog.51cto.com/u_16213600";
var img_url="https://static2.51cto.com/edu/blog/";
var i_user_id="";
var c_user_id=16203600;
var collect_url="https://blog.51cto.com/addUserCollect";
var is_old=2;
var nicknameurl="https://blog.51cto.com/u_16213600";
var nickname="mob64ca13fc5fb6";
var shareimgUrl="/qr/qr-url?url=https%3A%2F%2Fblog.51cto.com%2Fu_16213600%2F10820896";
var checkFollow=1;
var seoTitle="";
var articleABtest=0;
var blog_source=1;
var blog_source_video=1;
var blog_add_time=1715825152;
var word_type=1;
var custom_id=0;
var firstTwoCate=36;
var webTitle="机器学习sklearn 模型导出 sklearn导入数据";
            !function(f,p){"use strict";var h=new RegExp("\\.css"),y=p.head||p.getElementsByTagName("head")[0],r=+navigator.userAgent.replace(/.*(?:AppleWebKit|AndroidWebKit)\/?(\d+).*/i,"$1")<536;function s(e){return"complete"===e.readyState||"loaded"===e.readyState}function v(e,t,n){var o="onload"in e;function a(){e.onload=e.onreadystatechange=null,e=null,t()}"css"!==n||!r&&o?o?(e.onload=a,e.onerror=function(){e.onerror=null}):e.onreadystatechange=function(){s(e)&&a()}:setTimeout(function(){!function e(t,n){var o;t.sheet&&(o=!0),setTimeout(function(){o?n():e(t,n)},20)}(e,t)},1)}function u(t,n,e,o){if(t)if(h.test(t)){var a=t,r=e,c=u,i=p.createElement("link");if(r.attrs)for(var l in r.attrs)i.setAttribute(l,r.attrs[l]);r.prefetch?(i.href=a,i.rel="prefetch",c&&c()):(i.rel="stylesheet",v(i,c,"css"),i.href=a),y.appendChild(i)}else{var c=t,d=e,a=u,f=d.prefetch?p.createElement("link"):p.createElement("script");if(d.attrs)for(var s in d.attrs)f.setAttribute(s,d.attrs[s]);d.prefetch?(f.href=c,f.rel="prefetch",a&&a()):(f.charset="utf-8",v(f,a,"js"),f.async=!1,f.src=c),y.appendChild(f)}else setTimeout(function(){u()});function u(){var e=n.indexOf(t);-1<e&&n.splice(e,1),0===n.length&&o()}}function c(e="load",t){var n="object"==typeof t.option?t.option:{},t="function"==typeof t.callback?t.callback:null;return n.attrs="object"==typeof n.attrs?n.attrs:{},n.loaded="boolean"==typeof n.loaded&&n.loaded,n[e]=!0,{option:n,cb:t}}function i(c,e,t="load"){var n,o,a,r,i,l;function d(){var e=c,t=i,n=l;function o(){n&&n()}if(0===(e=Array.prototype.slice.call(e||[])).length)o();else for(var a=0,r=e.length;a<r;a++)u(e[a],e,t,o)}c&&c.length&&(i=e.option,l=e.cb,e=p,n=function(){"load"===t&&i.loaded?setTimeout(d,2e3):d()},("ready"===(o=t)?"loading"!==e.readyState:s(e))?n():(a=!1,r=function(){a||(n(),a=!0)},"load"===o?f.addEventListener("load",r):"ready"===o&&p.addEventListener("DOMContentLoaded",r),setTimeout(function(){r()},1500)))}f.PsLoader={ready:function(e,t,n={}){var o=[],a=[];e.forEach(function(e){(h.test(e)?o:a).push(e)}),n.loaded=!1,i(o,c("ready",{option:n,callback:function(){t(o)}}),"ready"),i(a,c("load",{option:n,callback:function(){t(a)}}))},load:function(e,t,n={}){i(e,c("load",{option:n,callback:t}))},prefetch:function(e,t,n={}){i(e,c("prefetch",{option:n,callback:t}))}}}(window,document);        !function(m,g){var t=["scroll","wheel","mousewheel","resize","animationend","transitionend","touchmove"];function n(e){if("object"!=typeof e)throw new Error("CLazy option is not Object");var f={defaultImg:e.defaultImg||"data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7",preLoad:e.preLoad||1.3,preLoadTop:e.preLoadTop||0,complete:e.complete||null,events:e.events||t,capture:e.capture||!1},v=0,p={},h={},i={},A=this;function l(e){var t=e;if("object"!=typeof t)return!1;if(!t.el)for(var r in p)if(e===p[r].el){t=p[r];break}return t}function c(e){var e=e.getBoundingClientRect(),t=f.preLoad,r=f.preLoadTop;return e.top<m.innerHeight*t&&e.bottom>r&&e.left<m.innerWidth*t&&0<e.right}function u(e,t){var r,n=e.bindType,o=e.el;switch(t){case"loading":case"error":r=f.defaultImg;break;default:r=e.src}n?e.src&&(o.style[n]='url("'+r+'")'):o.getAttribute("src")!==r&&o.setAttribute("src",r),o.setAttribute("lazy",t)}this.add=function(e,t){var r=function(e){var t,r=!1;for(t in p)if(p[t].el===e){r=p[t];break}return r}(e);if(r)return this.check(r),!1;r="e_"+ ++v;if(p[r])return this.check(p[r]),!1;for(var n,o={id:r,el:e,bindType:"IMG"===e.tagName?null:"background-image",src:(n=e,(t=t)?t.value:n.getAttribute("ps-lazy")),$parent:function(e){if(!(e instanceof HTMLElement))return m;var t=e;for(;t&&t!==g.body&&t!==g.documentElement&&t.parentNode;){if(/(scroll|auto)/.test(function(e){return y(e,"overflow")+y(e,"overflow-y")+y(e,"overflow-x")}(t)))return t;t=t.parentNode}return m}(e)},a=(h[r]=function(e){A.check(o)},p[r]=o),i=h[r],c=0;c<f.events.length;c++){s=d=u=l=void 0;var[l,u,d,s=!1]=[a.$parent,f.events[c],i,f.capture];l&&l.addEventListener(u,d,s),m!==l&&m.addEventListener(u,d,s)}this.check(o)},this.remove=function(e){for(var e=l(e),t=(e.el&&e.el.removeAttribute("ps-lazy"),e),r=h[e.id],n=0;n<f.events.length;n++){c=i=a=o=void 0;var[o,a,i,c=!1]=[t.$parent,f.events[n],r,f.capture];o&&o.removeEventListener(a,i,c),m!==o&&m.removeEventListener(a,i,c)}delete h[e.id],delete p[e.id]},this.check=function(e){var t,r,n,o,a=l(e);c(a.el)&&(m===a.$parent||c(a.$parent))?(e=function(e){u(a,e),A.remove(a),f.complete&&f.complete({el:a.el,src:a.src,state:e})},a.src?(t=a.src,r=e,n=encodeURIComponent(t),i[n]?r(i[n]):((o=new Image).onload=function(){i[n]="loaded",r(i[n])},o.onerror=function(){i[n]="error",r(i[n])},o.src=t)):e("loaded")):u(a,"loading")},this.checkAll=function(){for(var e in p)A.check(p[e])}}function y(e,t){return"undefined"!=typeof getComputedStyle?getComputedStyle(e,null).getPropertyValue(t):e.style[t]}m.PsLazy=function(e={}){function t(e){for(var t=e.path||event.composedPath&&event.composedPath()||e._getPath&&e._getPath(),r=0;r<t.length;r++){var n=t[r];if(n&&"hasAttribute"in n&&n.hasAttribute("ps-lazy-check")){o.format();break}}}function r(){var e=g.querySelector("img[data-share]");e&&!e.getAttribute("src")&&e.setAttribute("src",e.getAttribute("data-share"))}var o=this;n.call(o,e),g.addEventListener("click",t),g.addEventListener("mouseover",t),this.format=function(){var e=g.querySelectorAll("[ps-lazy]");if(!e.length)return!1;for(var t=0;t<e.length;t++)o.add(e[t])},this.format();"complete"===(e=g).readyState||"loaded"===e.readyState?r():m.addEventListener("load",r,!1)}}(window,document);        PsLoader.load(["https://static2.51cto.com/edu/blog/blog-static/static/css/pc_detailinline.min.css?v=f7524d2aae","https://static2.51cto.com/edu/blog/blog-static/static/css/pc_detail.min.css?v=8bd4a251ef","https://cdn.51cto.com/jquery/jquery-2.2.4.min.js","https://static2.51cto.com/edu/center/js/interaction_iframe.js","https://cdn.51cto.com/jquery/swiper-4.5.3.js","https://cdn.51cto.com/svga/2.3.1/svga.min.js","https://static2.51cto.com/edu/blog/blog-static/static/js/pc_base.min.js?v=d06e4f1e8b","https://static2.51cto.com/edu/blog/blog-static/js/mprime.js?v=2cb70144db","https://cdn.51cto.com/lingjing-agent/1.0.7/js/index.global.js","https://static2.51cto.com/edu/blog/blog-static/js/lingjing-agent/lingjing.js?v=9c85312fef","https://static2.51cto.com/edu/blog/blog-static/static/js/pc_detail.min.js?v=f68e6d567c"], function() {
                    articleCopy();
            })
    PsLoader.prefetch(["https://static2.51cto.com/edu/blog/blog-static/static/css/pc_base.min.css?v=8d92ab701b","https://static2.51cto.com/edu/blog/blog-static/static/css/pc_indexinline.min.css?v=400a5f4051","https://static2.51cto.com/edu/blog/blog-static/static/css/pc_newIndexinline.min.css?v=16927be427","https://static2.51cto.com/edu/blog/blog-static/static/css/pc_listinline.min.css?v=71cfee60b1","https://static2.51cto.com/edu/blog/blog-static/static/css/pc_newListinline.min.css?v=8f92cf000e","https://static2.51cto.com/edu/blog/blog-static/static/css/pc_topicinline.min.css?v=ab62f5f632","https://static2.51cto.com/edu/blog/blog-static/static/css/pc_topicdetailinline.min.css?v=fc7a3eae0b","https://static2.51cto.com/edu/blog/blog-static/static/css/pc_bloggerinline.min.css?v=4c33bc4c88","https://static2.51cto.com/edu/blog/blog-static/markdown/dist/js/main.js?v=12e5a1a2fe","https://static2.51cto.com/edu/blog/blog-static/static/js/pc_index_js.min.js?v=835c51179f","https://static2.51cto.com/edu/blog/blog-static/static/js/pc_list_js.min.js?v=eab52af915","https://static2.51cto.com/edu/blog/blog-static/static/js/pc_topic.min.js?v=873da4210c","https://static2.51cto.com/edu/blog/blog-static/static/js/pc_topic_static.min.js?v=8533cb9e02","https://static2.51cto.com/edu/blog/blog-static/static/js/pc_topicdetail.min.js?v=901345e7d5","https://static2.51cto.com/edu/blog/blog-static/static/js/pc_blogger_js.min.js?v=24bf77cbf1"]);
    var Lazy = new PsLazy({
        defaultImg: "https://s2.51cto.com/images/100/base/empty.png?x-oss-process=image/format,webp/ignore-error,1",
        preLoad: 1.3,
        complete: function(opt) {},
    })
</script>
</body>
</html>
