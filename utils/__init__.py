from urllib.parse import urlparse


def getProxies():
    proxies = []

    with open("apps/common/src/proxies.txt", 'r') as file:
        for line in file:
            proxies.append(line.strip())

    return proxies
