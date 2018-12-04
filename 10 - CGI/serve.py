import sys
from http.server import CGIHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import http
import urllib
import os

def parse_path(url, dir_name):     
    if dir_name in url:
       url = url.split(dir_name, 1)[1]
    
    url_split = url 
    file = None
    if ".cgi" in url:      
       url_split = url.split(".cgi", 1)
       file = url_split[0][1:] + ".cgi"  
   
       return file, url_split[1]    
    else:
       return url_split[1:], ""

class ThreadHTTPServer(ThreadingMixIn, HTTPServer):
    pass


def serve_content(self, dir_name):     
    file_location, params = parse_path(self.path, dir_name)    
    path = os.path.abspath(os.path.join(dir_name, file_location))    
    
    if os.path.isfile(path):
       if path.endswith('.cgi'):
          # Has to contain directory name and entire string after it (dir, rest = self.cgi_info)        
          self.cgi_info = dir_name, file_location + params   
          # Runs cgi, and also sets all environment variables it can find         
          self.run_cgi()
       else:
          self.send_response(200)
          self.send_header('Content-Length', str(os.path.getsize(path)))
          self.end_headers()

          with open(path, "rb") as file:
             content = file.read()            
             self.wfile.write(content)                  
    else:
       self.send_error(404, explain="Not Found")


def get_handler(dir_name):
    class RequestHandler(CGIHTTPRequestHandler):
        def do_GET(self):            
            serve_content(self, dir_name)

        def do_POST(self):
            serve_content(self, dir_name)

        def do_HEAD(self):
            serve_content(self, dir_name)    

    return RequestHandler
   

def main(argv):      
    port = int(sys.argv[1])
    dir_name = sys.argv[2]   
    
    server = ThreadHTTPServer(('', port), get_handler(dir_name))
    
    server.serve_forever()


if __name__ == "__main__":
    main(sys.argv[1:])
