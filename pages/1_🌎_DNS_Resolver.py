import streamlit as st 
import re
import dns.resolver
import re
import os
import time

# https://www.cnblogs.com/Zzbj/p/11431015.html

def _max_width_(prcnt_width:int = 75):
    max_width_str = f"max-width: {prcnt_width}rem;"
    st.markdown(f""" 
                <style> 
                .block-container{{{max_width_str}}}
                </style>    
                """, 
                unsafe_allow_html=True,
    )
_max_width_(st.sidebar.slider('屏幕比例', 30, 100, 75))


st.title('Dns & nsookup')
ping_pattern = re.compile(r'(\d[^,]+)+')


# dns
options_dns = {
    '阿里 dns': ['223.5.5.5', '223.6.6.6'],
    '腾讯 dns': ['119.29.29.29', '182.254.116.116'],
    '百度 dns': ['180.76.76.76'],
    '114 dns': ['114.114.114.114', '114.114.115.115'],
    'Google dns': ['8.8.8.8', '8.8.8.9'],
    '自定义': []
}

dns_key = st.selectbox('选择 dns 服务器', options=options_dns.keys())
dns_servers = options_dns[dns_key]
if dns_key == '自定义':
    dns_servers = st.text_input('输入自定义 dns 服务器', placeholder='例如: 8.8.8.8,8.8.8.4.4', value='8.8.8.8').split(',')
resolver = dns.resolver.Resolver()
resolver.nameservers = dns_servers

# 域名
domains = [
    'www.baidu.com',
    'www.google.com',
    'www.qq.com',
    'www.163.com',
    'github.com',
    'raw.githubusercontent.com',
    '自定义'
]
domain = st.selectbox('选择域名', options=domains)
if domain == '自定义':
    domain = st.text_input('填写域名', value='www.baidu.com')


# 超时时间
timeout = st.slider('超时时间(s)', 1, 10, 1)

st.button('解析域名')

resolver.timeout = 1.0
try:
    with st.spinner('连接 dns 服务器...'):
        response = resolver.resolve(domain, 'A')
        resolver_servers = []
        for rdata in response:
            resolver_servers.append(rdata.address)
        # st.code(resolver_servers)
        pingresult = []
    
    with st.progress(1, '解析中...'):
        for i, dest_addr in enumerate(resolver_servers):
            st.progress(int((i+1) / len(resolver_servers) * 100), f'正在解析: {dest_addr}')
            # pingresult[dest_addr] = ping3.ping(dest_addr=dest_addr, timeout=1.0)
            start = time.perf_counter()
            with os.popen(f'ping {dest_addr} -c 1 -W {timeout}') as f:
                for line in f.readlines():
                    if 'transmitted' in line:
                        res = ping_pattern.findall(line)
                        if len(res) == 4:
                            ellip = int((time.perf_counter() - start)*1000)
                            pingresult.append({
                                '解析服务': dns_servers,
                                '解析域名': domain,
                                '目标地址': dest_addr,
                                '接收率': res[1],
                                '丢失率': res[2],
                                '耗时': f'{ellip}ms',
                                # '耗时': res[3],
                            })
        st.dataframe(pingresult, use_container_width=True)
    count = st.slider('选择次数', 0, 100, 10)
    missing = 0
    if st.button(f'立即进行 {count} 次 ping'):
        ellips = 0
        pingresult = []
        sss = st.dataframe(pingresult, use_container_width=True)
        for c in range(count):
            for i, dest_addr in enumerate(resolver_servers):
                # st.progress(int((i+1) / len(resolver_servers) * 100), f'正在解析: {dest_addr}')
                # pingresult[dest_addr] = ping3.ping(dest_addr=dest_addr, timeout=1.0)
                # start = time.time()
                start = time.perf_counter()
                with os.popen(f'ping {dest_addr} -c 1 -W {timeout}') as f:
                    for line in f.readlines():
                        if 'transmitted' in line:
                            res = ping_pattern.findall(line)
                            if len(res) == 4:
                                ellip = int((time.perf_counter() - start)*1000)
                                pingresult.append({
                                    '解析服务': dns_servers,
                                    '解析域名': domain,
                                    '目标地址': dest_addr,
                                    '接收率': res[1],
                                    '丢失率': res[2],
                                    '耗时': f'{ellip}ms',
                                })
                                if res[1].startswith('0'):
                                    missing += 1
                                ellips += ellip
                    sss.dataframe(pingresult, use_container_width=True)
        st.info(f'共发起 {count} 次 ping，耗时 {ellips/1000}s，丢包率为: {int(missing / count * 100)}%，注意这与您设置的超时时间为 {timeout} 有关。')
except dns.resolver.NoAnswer:
    st.warning(f'无法解析域名: {domain}')
except dns.resolver.NXDOMAIN:
    st.warning(f'域名不存在: {domain}')
except dns.exception.Timeout:
    st.warning('DNS 服务器超时')

# pip install dnspython (use)
# pip install ping3     (unuse)

# linux: ping 