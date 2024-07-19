import requests

data = {
    "url": "https://pioneer.particle.network/zh-CN/point",
    "invisible": True
}

r = requests.post("https://the-domain-of-deployment.com/turnstile/0x4AAAAAAAaHm6FnzyhhmePw", json=data)
token = r.text
print("Solved :: " + token)
