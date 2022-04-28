import requests
from requests.auth import HTTPDigestAuth
from requests_toolbelt.multipart import decoder
from pandas.io.json import json_normalize
import json
# ----------------------------------------------------------------------

class ConfigStruct:
    def __init__(self, **entries): 
        self.__dict__.update(entries)


# ----------------------------------------------------------------------

class MLRESTConnection(object):

    def __init__(self):
        self.cfg = ConfigStruct(host='localhost', port='8000', user='admin', password='admin', scheme='xquery', action='eval', param=None)
        self.search = ConfigStruct(start='1', page='10')

    def call_rest(self, args, code):
        df = None
        if args.mode == 'search':
            df = self._run_search(args,code) 
        else:
            df = self._eval_code(code) 
        return df
      
    def _eval_code(self, code):
        session = requests.session()
        session.auth = HTTPDigestAuth(self.cfg.user, self.cfg.password)
        payload = {self.cfg.scheme: code}
        if self.cfg.scheme == 'sql':
            code = code.replace('"',"'") 
            code = "xdmp:sql(\"{}\",'map')".format(code)
            payload = {"xquery": code}
        
        #logging.info(code)

        uri = 'http://%s:%s/v1/eval' % (self.cfg.host, self.cfg.port)
        #print(code)
        result = session.post(uri, data=payload)

        data = []
        df = None   
        status = str(result.status_code)
        if status == '200':
            #Don't always get content-type oddly
            if result.headers.get('Content-Type','').startswith("multipart/mixed"):
                data = self._get_multi_result(result)
            else:
                data.append({'data' : result.json()  , 'type' : 'text/plain'})               
        else:
            print(status)
            error = result.json()["errorResponse"]["message"]
            print(error)
        df = json_normalize(data)      
        return df
 
    def _run_search(self,args, code):
        session = requests.session()
        session.auth = HTTPDigestAuth(self.cfg.user, self.cfg.password) 
        params = {'start': args.start,'pageLength': args.results, 'format':'json'}
        headers = {'Content-type': 'application/json','Accept': 'application/json' }
        ##logging.info(code)
        #code = code.replace("'",'"')
        #code = "cts:parse:(\'{}\')".format(code)
        uri = 'http://%s:%s/v1/search' % (self.cfg.host, self.cfg.port)

        #print(code)
        result = session.post(uri, params=params, data=code, headers=headers)
        df = None    
        status = str(result.status_code)
        if status == '200':
            json_result = result.json()
            if int(json_result['total']) == 0:
                print("No results.")
            else:
                print("Returned {} to {} of {} results".format(json_result['start'],json_result['page-length'], json_result['total']))
                df = json_normalize(json_result['results'])
        else:
            print(status)
            error = result.json()["errorResponse"]["message"]
            print(error)
    
        return df
 
    def _get_multi_result(self,result):
        out = []
        multipart_data = decoder.MultipartDecoder.from_response(result)
        print("Returned {} results".format(len(multipart_data.parts)))
        for part in multipart_data.parts:
            ctype = part.headers[b'Content-Type'].decode('utf-8')
            raw = part.content
            data = json.loads(raw) if (ctype == 'application/json') else raw
            out.append({'data' : data, 'type' : ctype}) 
        return out 
    
    def endpoint(self,line):
        try:
            r = requests.utils.urlparse(line)
            self.cfg = ConfigStruct( host=r.hostname, port=r.port, user=r.username, password=r.password, scheme=r.scheme, action='eval', param=None)
        except:
            print('malformed connection' + line)
        return None

