#import urllib
#urllib.urlretrieve("https://www.infofunerais.pt/image_temp/123X98_03c035b9d605e4fb3d682ccffadd4d86.jpeg", "00000001.jpg")

#import urllib
#f = open('00000001.jpg','wb')
#f.write(urllib.urlopen('https://www.infofunerais.pt/image_temp/123X98_03c035b9d605e4fb3d682ccffadd4d86.jpeg').read())
#f.close()

import requests
f = open('00000001.jpg','wb')
f.write(requests.get('https://www.infofunerais.pt/image_temp/123X98_03c035b9d605e4fb3d682ccffadd4d86.jpeg').content)
f.close()
