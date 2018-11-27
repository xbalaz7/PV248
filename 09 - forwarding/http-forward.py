import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
import http
import socket
import json
import ssl

def parse_url(url):    
    url = url.replace("https://", "")   
    url = url.replace("http://", "") 
    url_split = url.split("/", 1)   
    
    if len(url_split) > 1:    
       return url_split[0], ("/" + url_split[1])
    else:
       return url_split[0], "/"

def handle_request(url, request_type, headers = None, content = None, timeout = 1):    
    name, parameters = parse_url(url)
   
    try:              
       connection = http.client.HTTPSConnection(name, context=ssl._create_unverified_context(), timeout = timeout)        
       connection.request(request_type, parameters, content, headers=headers)           
       return connection.getresponse()
    except socket.timeout:       
       return "timeout"
    except:
       return None


def get_handler(url):
    class RequestHandler(BaseHTTPRequestHandler):
        def do_GET(self):   
            if 'Host' in self.headers:
                del self.headers['Host']

            response = handle_request(url, "GET", headers = self.headers, content = None, timeout = 1)
            result = {}             
            
            if response == "timeout":
               result["code"] = "timeout"
            elif response:
               result["code"] = response.status
               result["headers"] = dict(response.getheaders())
               content = response.read().decode("UTF-8")
              
               try:
                  loaded = json.loads(content)
                  result["json"] = loaded
               except:                  
                  result["content"] = content
            else:
               result["code"] = "connection failed"            
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')            
            self.end_headers()
            self.wfile.write(bytes(json.dumps(result, indent=4, ensure_ascii = False), "UTF-8"))            

        def do_POST(self):             
            result = {}                
            
            try:
               content_length = int(self.headers['Content-Length'])
               data = self.rfile.read(content_length).decode("UTF-8")               
               data = json.loads(data)
               
               request_type = "GET"
               try:
                  request_type = data["type"]
               except:
                  pass

               if request_type != "POST": request_type = "GET"
              
               url = data["url"]               
               headers = data["headers"] if "headers" in data else {}
              
               content = None
               if request_type == "POST":
                  content = data["content"]
                  content = content.encode("UTF-8")                 
          
               timeout = 1
               try:
                  timeout = int(data["timeout"])
               except:
                  pass                       
               
               response = handle_request(url, request_type, headers, content, timeout)              
              
               if response == "timeout":
                  result["code"] = "timeout"
               elif response:      
                  result["code"] = response.status   
                  result["headers"] = dict(response.getheaders())                 
                  content = response.read().decode("UTF-8")
                  
                  try:
                    loaded = json.loads(content)
                    result["json"] = loaded
                  except:                  
                    result["content"] = content
               else:
                  result["code"] = "connection failed"
               
               self.send_response(200)
               self.send_header('Content-Type', 'application/json')               
               self.end_headers()
               self.wfile.write(bytes(json.dumps(result, indent=4, ensure_ascii = False), "UTF-8"))
            except:
               result["code"] = "invalid json"
               self.send_response(200)
               self.send_header('Content-Type', 'application/json')
               self.end_headers()
               self.wfile.write(bytes(json.dumps(result, indent=4, ensure_ascii = False), "UTF-8"))


    return RequestHandler



def main(argv):      
    port = int(sys.argv[1])
    url = sys.argv[2]    

    server = HTTPServer(('', port), get_handler(url))
    server.serve_forever()


if __name__ == "__main__":
    main(sys.argv[1:])
