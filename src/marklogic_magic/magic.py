from __future__ import print_function            

from IPython.core.magic import (Magics, magics_class, line_magic,
                                cell_magic, line_cell_magic, needs_local_scope)
from IPython.core.magic_arguments import argument, magic_arguments, parse_argstring

import requests
from requests.auth import HTTPDigestAuth
from requests_toolbelt.multipart import decoder
    
from .connection import MLRESTConnection  
  
# The class MUST call this class decorator at creation time
# print("Full access to the main IPython object:", self.shell)
# print("Variables in the user namespace:", list(self.shell.user_ns.keys()))
 
@magics_class
class MarkLogicMagic(Magics):
    
    def __init__(self,shell):
        # You must call the parent constructor
        super(MarkLogicMagic, self).__init__(shell)
        self.connection = MLRESTConnection()
        self.ret_var = 'result_var'
           
    @magic_arguments()
    @cell_magic
    @argument(
        '-s', '--start',default='1',
        help='start record'
    )
    @argument(
        '-r', '--results',default='10',
        help='number of results * = all'
    )
    @argument(
        '-o', '--output',default='ml_search',
        help='output to a var, default is ml_search'
    )    
    @argument(
        'connection', default=None,nargs='?',
        help='connection string; can be empty if set previously.'
    )
    def ml_search(self, line=None, cell=None,local_ns={}):
        args = parse_argstring(self.ml_search, line)
        args.mode='search'
        if args.connection is not None:
            self.connection.endpoint(args.connection)
        if cell is None:
            print("No contents")  
        else: 
            user_ns = self.shell.user_ns.copy()
            user_ns.update(local_ns)     
            df = self.connection.call_rest(args, cell)
            print('DataFrame returned in ' + args.output)     
            self.shell.user_ns.update({args.output: df})
 
    @magic_arguments()
    @cell_magic
    @argument(
        '-o', '--output',default='ml_fetch',
        help='output to a var, default is ml_fetch'
    )    
    @argument(
        'connection', default=None,nargs='?',
        help='connection string; can be empty if set previously.'
    )                       
    def ml_fetch(self, line=None, cell=None,local_ns={}):
        user_ns = self.shell.user_ns.copy()
        user_ns.update(local_ns)
        args = parse_argstring(self.ml_fetch, line)
        args.mode='fetch'
        if cell is None:
            print("No contents")
        else:
            #reset connection if given
            if args.connection is not None:
                self.connection.endpoint(args.connection) 
            #expand out {var} in cell body
            cell = cell.format(**user_ns)     
            df = self.connection.call_rest(args, cell)
            self.shell.user_ns.update({args.output: df})
            print('DataFrame returned in ' + args.output)
            
    def parse_line(self,line):
        if line is None:
            return line
        else:
            words = line.split()
            num_words = len(words)
            # sql://titanic-reader:titanic-reader@localhost:8079 >> test
            if num_words == 3 and words[1] == '>>':
                self.ret_var = words[2]
                return words[0]  
            # >> test
            if num_words == 2 and words[0] == '>>':
                self.ret_var = words[1]
                return None
            if num_words == 1:
                return words[0]
       
       

def load_ipython_extension(ipython, *args):
    ipython.register_magics(MarkLogicMagic)
    print("marklogic magic loaded.")


def unload_ipython_extension(ipython):
    print("marklogic magic unloaded.")




