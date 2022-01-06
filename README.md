ADD NETWORKS

1.In global config add these fields

        "network_info" : "/opt/mistnet/etc/networkinfo.json",
        
        "network_details_add" : "http://<probe_ip>:7000/"

2.Edit the addnetwork.json

{

  "user": "<user>",
  
  "password": "<password>",
  
  "encrypt": "<encrypt>",
  
  "ssl_ca_certs": "<ssl_ca_certs>",
  
  "sslcertpath": "<sslcertpath>",
  
  "database": "<database>",
  
  "host": "<host>"
  
}

3. Run `python3 addnetwork.py addnetwork.json`
   

