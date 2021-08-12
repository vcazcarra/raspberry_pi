import socket
import sys
sys.path.append('/home/pi/emails_from_python/')
from lib_emails import send_email
import time


ip = '0.0.0.0'
receiver_email = "-------"

#wait that the rapsberry gets internet if we reboot...
time.sleep(60*2)

while True:
    
    #GEt the current ip
    current_ip = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]   
    
    #ceck if is the same
    if current_ip != ip:
        ip = current_ip
        message = """\
                Change ip raspberry

                New ip: """+ip
        send_email(message,receiver_email)
    
    #wait some time before checking again
    time.sleep(60*30)
