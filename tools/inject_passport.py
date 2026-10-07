import re
p='/home/ubuntu/wedding-site/index.html'; s=open(p).read()
svg=open('/home/ubuntu/wedding-site/partials/passport-card.svg').read()
a=s.index('<!-- PASSPORT ART START'); a=s.index('-->',a)+4
b=s.index('        <!-- PASSPORT ART END')
s=s[:a]+svg+'\n'+s[b:]
open(p,'w').write(s); print('injected')
