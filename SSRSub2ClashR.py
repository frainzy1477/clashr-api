#!/usr/bin/python
# -*- coding: UTF-8 -*-
import requests
import base64
import codecs


def getBasefile(url):  # 获取链接文本
    try:
        html = requests.get(url)
        html.raise_for_status
        html.encoding = html.apparent_encoding
        return str(html.text)

    except Exception as e:
        print('getBasefile Error:', e)



def getAllLinks(url):  # 从加密文本解析出所有ssr链接
    try:
        links = getBasefile(url)      
        result = decodeInfo(links)
        alllinks = result.split('\\n')
        if len(alllinks[-1]) < 10:
            alllinks.pop()
        return alllinks
    
    except Exception as e:
        print('getAllLinks Error:', e)


def getAllNodes(url):  # 从ssr链接汇总得到所有节点信息
    try:
        allnodes = []
        links = getAllLinks(url)
        
        for ssr in links:            
            if len(ssr) > 10:
                link = ssr.split('//')[1].split("'")[0]    # 不同订阅不同的切分形式                        
                node = getNodeR(link)
                allnodes.append(node) 
        return allnodes

    except Exception as e:
        print('getAllNodes Error:', e)



def getNodeR(link):  # 从ssr链接中得到节点信息 如参数不对应在此调整
    try:
        node_info = {}
        
        info = decodeInfo(link)
        
        node_info['server'] = info.split(':')[0].split("'")[1]
        node_info['port'] = info.split(':')[1]
        node_info['pwd'] = decodeInfo(info.split('/')[0].split(':')[-1]).split("'")[1]
        node_info['protocol'] = info.split(':')[2]
        node_info['method'] = info.split(':')[3]
        node_info['obfs'] = info.split(':')[4]
        
        last_val=info.split('/?')[1].split("'")[0]
        for a in last_val.split('&'):
            b=a.split('=')[0]
            c=getName(a.split('=')[1])
            node_info[b]=c
        
        print(node_info)
        return node_info

    except Exception as e:
        print('getNodeR Error:', e)

def getName(info):  # 得到节点名称
    lens = len(info)

    if lens % 4 == 1:
        info = info + "==="
    elif lens % 4 == 2:
        info = info + "=="
    elif lens % 4 == 3:
        info = info + "="
    result = base64.urlsafe_b64decode(info).decode('utf-8', errors='ignore')
    return result

def decodeInfo(info):  # 解码加密内容
    lens = len(info)
    if lens % 4 == 1:
        info = info + "==="
    elif lens % 4 == 2:
        info = info + "=="
    elif lens % 4 == 3:
        info = info + "="
    result = str(base64.urlsafe_b64decode(info))
    return result


def setNodes(nodes):  # 设置SSR节点
    proxies = []
    for node in nodes:
        name = node['remarks']
        server = node['server']
        port = node['port']
        cipher = node['method']
        pwd = node['pwd']
        protocol = node['protocol']
        obfs = node['obfs']
        if 'protoparam' in node:
            proparam = node['protoparam']
        else:
            proparam = ''
            
        if 'obfsparam' in node:
            obparam = node['obfsparam']
        else:
            obparam = ''
            
        proxy = "- { name: " +"\"" +str(name).strip() +"\""+ ", type: ssr, server: " +"\""+ str(server)+"\"" + ", port: "+str(port)+", password: " +"\""+ str(pwd)+"\""+ ", cipher: " +"\""+ str(cipher)+"\""+", protocol: "+"\""+ str(protocol)+"\""+", protocolparam: " +"\""+ str(proparam)+"\""+", obfs: "+"\"" + str(obfs)+"\""+", obfsparam: " +"\""+ str(obparam)+"\""+" }\n"
        proxies.append(proxy)
    proxies.insert(0, '\nProxy:\n')
    return proxies


def setPG(nodes):  # 设置策略组 懂得可在下面自己编辑 反正我不懂
    proxy_names = []
    for node in nodes:
        proxy_names.append(node['remarks'])

    Proxy0 = "- { name: '总模式', type: select, proxies: " + " [\"手动切换\",\"延迟最低\",\"负载均衡\",\"故障切换\",\"DIRECT\"] }" +"\n"   
    Proxy1 = "- { name: '手动切换', type: select, proxies: " + str(proxy_names) + " }\n"
    Proxy2 = "- { name: '延迟最低', type: url-test, proxies: " + str(proxy_names) + ", url: 'http://www.gstatic.com/generate_204', interval: 300 }\n"
    Proxy3 = "- { name: '故障切换', type: fallback, proxies: " + str(proxy_names) + ", url: 'http://www.gstatic.com/generate_204', interval: 300 }\n"
    Proxy4 = "- { name: '负载均衡', type: load-balance, proxies: " + str(proxy_names) + ", url: 'http://www.gstatic.com/generate_204', interval: 300 }\n"

    Apple = "- { name: 'Apple服务', type: select, proxies: "+" [\"DIRECT\",\"手动切换\"] }" +"\n"
    GlobalMedia = "- { name: '国际媒体', type: select, proxies: "+" [\"手动切换\"] }" +"\n"
    MainlandMedia = "- { name: '国内媒体', type: select, proxies: "+" [\"DIRECT\"] }" +"\n"
    RejectWeb =  "- { name: '屏蔽网站', type: select, proxies: "+" [\"REJECT\",\"DIRECT\"] }"+"\n" +"\n"+"\n"+"\n"+"\n"+"\n"

    Rule = "#规则"+"\n"+"Rule:"+"\n"

    ProxyGroup = ['\nProxy Group:\n\n',Proxy0,Proxy1,Proxy2,Proxy3,Proxy4,Apple,GlobalMedia,MainlandMedia,RejectWeb,Rule]
    return ProxyGroup


def getClash(nodes):  #写文件

    rules = getBasefile('https://raw.githubusercontent.com/partnerofme/ClashR/master/Rule.yml')
    gener = getBasefile('https://raw.githubusercontent.com/partnerofme/ClashR/master/General.yml')

    with codecs.open("./config.yml", "w",encoding = 'utf-8') as f:
        f.writelines(gener)

    info = setNodes(nodes) + setPG(nodes)
    with codecs.open("./config.yml", "a",encoding = 'utf-8') as f:
        f.writelines(info)

    rule = rules.split('Rule:\n')[1]
    with codecs.open("./config.yml", "a",encoding = 'utf-8') as f:
        f.writelines(rule)


if __name__ == "__main__":
    try:
        url = "http://urmine.getenjoyment.net/alluser.html"         #替换订阅地址 只支持SSR订阅
        
        #上面订阅地址为免费订阅~ClashR暂不支持~仅在此做转换测试使用~但欢迎在其他客户端使用
        #没有条件测试~不知道能不能正常使用~请自行测试~~
        nodes = getAllNodes(url)
        getClash(nodes)
    
    except Exception as e:
        print('main Error:', e)
