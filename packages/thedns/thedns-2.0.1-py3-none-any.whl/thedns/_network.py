# import socket
# import hashlib
#
# def _get_private_ip():
#     s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     s.connect(('8.8.8.8', 80))
#     private_ip_string = s.getsockname()[0]
#     s.close()
#     return private_ip_string
#
# def _get_rr_string():
#     try:
#         with open('/etc/machine-id', 'r') as f:
#             rr_string = hashlib.md5(f.read().encode()).hexdigest()
#     except:
#         rr_string = hashlib.md5(socket.gethostname().encode()).hexdigest()
#     return rr_string
