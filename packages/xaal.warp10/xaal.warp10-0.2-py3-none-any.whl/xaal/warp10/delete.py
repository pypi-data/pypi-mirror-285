from xaal.lib import config,tools
import urllib3
import sys


PACKAGE_NAME = "xaal.warp10"

def main():
    serie = sys.argv[1]
    cfg = tools.load_cfg_or_die(PACKAGE_NAME)['config']
    http = urllib3.PoolManager()
    DATA_BUF=""
    url = '/'.join(cfg['url'].split('/')[:-1]) + '/delete?deleteall&selector=%s' % sys.argv[1]
    print(url)
    rsp = http.request('GET',url,headers={'X-Warp10-Token':cfg['token']},body=DATA_BUF,retries=2)
    print(rsp.data)



if __name__ == '__main__':
    main()
    
