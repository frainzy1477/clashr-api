#!/usr/bin/python3
# -*- coding: UTF-8 -*-

#############################################

#  将SSR订阅转为ClashR    By PartnerOfmE

#############################################

import requests
import base64
import codecs

def getBasefile(url):  # 获取链接文本
    try:
        html = requests.get(url)
        html.raise_for_status
        html.encoding = html.apparent_encoding
    except Exception as e:
        print('getBasefile Error:', e)
    else:
        print('从'+ url + '获取文本成功...')
        return str(html.text)
        


def getAllLinks(url):  # 从加密文本解码出所有ssr链接
    try:
        links = getBasefile(url)
        alllinks = base64_decode(links)
    except Exception as e:
        print('getAllLinks Error:', e)
    else:
        print('从编码文本解码成功...')
        return alllinks


def getAllNodes(url):  # 从ssr链接汇总得到所有节点信息
    try:
        allnodes = []
        links=getAllLinks(url).split('ssr://')
        
        for ssr in links:            
            if ssr:
                node = getNodeR(ssr.replace('\n', ''))                
                allnodes.append(node) 

    except Exception as e:
        print('getAllNodes Error:', e)
    else:
        print('获取所有节点信息成功...')
        return allnodes

def getNodeR(nodeinfo):  # 从ssr链接中得到节点信息 如参数不对应在此调整
    try:
        node_info = {}

        info=base64_decode(nodeinfo)
        
        front_val = info.split('/?')[0]
        node_info['server'] = front_val.split(':')[0]
        node_info['port'] = front_val.split(':')[1]
        node_info['protocol'] = front_val.split(':')[2]
        node_info['method'] = front_val.split(':')[3]
        node_info['obfs'] = front_val.split(':')[4]
        node_info['pwd'] = base64_decode(front_val.split(':')[5])
        
        rear_val=info.split('/?')[1]
        for a in rear_val.split('&'):
            b=a.split('=')[0]
            c=base64_decode(a.split('=')[1])
            node_info[b]=c
        
        #print(node_info)
        return node_info

    except Exception as e:
        print('getNodeR Error:', e)


def base64_decode(base64_encode_str):    # base64解码
    need_padding = len(base64_encode_str) % 4
    
    if need_padding !=0:
        missing_padding = 4 - need_padding
        base64_encode_str += '=' * missing_padding

    return base64.urlsafe_b64decode(base64_encode_str).decode('utf-8')


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
        
        if 'group' in node:
            group = node['group']
        else:
            group = ''
            
        if 'protoparam' in node:
            proparam = node['protoparam']
        else:
            proparam = ''
            
        if 'obfsparam' in node:
            obparam = node['obfsparam']
        else:
            obparam = ''
            
        proxy = '- { name: ' +'\"' +str(name).strip() +'\"'+ ', type: ssr, server: ' +'\"'+ str(server)+'\"' + ', port: '+str(port)+', password: ' +'\"'+ str(pwd)+'\"'+ ', cipher: ' +'\"'+ str(cipher)+'\"'+', protocol: '+'\"'+ str(protocol)+'\"'+', protocolparam: ' +'\"'+ str(proparam)+'\"'+', obfs: '+'\"' + str(obfs)+'\"'+', obfsparam: ' +'\"'+ str(obparam)+'\"'+' }\n'
        proxies.append(proxy)
    proxies.insert(0, '\nProxy:\n\n')
    return proxies


def setPG(nodes):  # 设置策略组 懂得可在下面自己编辑 反正我不懂
    proxy_names = ''
    for node in nodes:
        proxy_names = proxy_names + '\"' + (node['remarks']) + '\",'
    proxy_names = proxy_names[:-1]

    Proxy0 = '- { name: "总模式", type: select, proxies: ' + ' [\"手动切换\",\"延迟最低\",\"负载均衡\",\"故障切换\",\"DIRECT\"] }\n'   
    Proxy1 = '- { name: "手动切换", type: select, proxies: [' + str(proxy_names) + '] }\n'
    Proxy2 = '- { name: "延迟最低", type: url-test, proxies: [' + str(proxy_names) + '], url: "http://www.gstatic.com/generate_204", interval: 300 }\n'
    Proxy3 = '- { name: "故障切换", type: fallback, proxies: [' + str(proxy_names) + '], url: "http://www.gstatic.com/generate_204", interval: 300 }\n'
    Proxy4 = '- { name: "负载均衡", type: load-balance, proxies: [' + str(proxy_names) + '], url: "http://www.gstatic.com/generate_204", interval: 300 }\n'

    Apple = '- { name: "Apple服务", type: select, proxies: '+' [\"DIRECT\",\"手动切换\",' + str(proxy_names)+'] }\n'
    GlobalMedia = '- { name: "国际媒体", type: select, proxies: '+' [\"手动切换\",' + str(proxy_names)+'] }\n'
    MainlandMedia = '- { name: "中国媒体", type: select, proxies: '+' [\"DIRECT\"] }\n'
    RejectWeb =  '- { name: "屏蔽网站", type: select, proxies: '+' [\"REJECT\",\"DIRECT\"] }'+'\n\n\n\n\n\n'

    Rule = "# 规则\n"

    ProxyGroup = ['\nProxy Group:\n\n',Proxy0,Proxy1,Proxy2,Proxy3,Proxy4,Apple,GlobalMedia,MainlandMedia,RejectWeb,Rule]
    return ProxyGroup


def getClash(nodes):  #写文件
    try:
        rules = getBasefile('https://raw.githubusercontent.com/partnerofme/ClashR/master/Rule.yml')
        gener = getBasefile('https://raw.githubusercontent.com/partnerofme/ClashR/master/General.yml')
        
    except Exception as e:
        print('获取模板内容失败，可能是因为网络故障。退出...')
        return

    try:
        filename='config.yml'
        with codecs.open('./' + filename, "w",encoding = 'utf-8') as f:
            f.writelines(gener)

        info = setNodes(nodes) + setPG(nodes)
        with codecs.open('./' + filename, "a",encoding = 'utf-8') as f:
            f.writelines(info)

        rule = rules.split('# 规则\n')[1]
        with codecs.open('./' + filename, "a",encoding = 'utf-8') as f:
            f.writelines(rule)

    except Exception as e:
        print('写入文件失败，原因:{}',format(e))
    else:
        print('写入文件' + filename +'完成。')
        return
              
if __name__ == "__main__":
    try:
        url = 'http://publicsub.getenjoyment.net/alluser.html'        #替换订阅地址 只支持SSR订阅

        
        #上面订阅地址为免费订阅~ClashR暂不支持~仅在此做转换测试使用~但欢迎在其他客户端使用

        nodes = getAllNodes(url)
        getClash(nodes)
    
    except Exception as e:
        print('main Error:', e)
