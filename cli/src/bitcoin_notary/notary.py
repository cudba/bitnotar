# -*- coding: utf8 -*-
try:
  import sys
  sys.path.append('pywallet')
  import pywallet
except:
  print "You have to checkout the git submodule 'pywallet'!"
  import sys; sys.exit(1)


def sha256sum(fn):
  '''
  Calculates the SHA 256 sum of the given byte-vector in the file ``fn``.
  '''
  from hashlib import sha256
  chunk_size = 1024 * 1024 # 1 MB
  cs = sha256()
  with open(fn, "rb") as f:
     while True:
       byte = f.read(chunk_size)
       if not byte: break
       cs.update(byte)
  return cs.hexdigest()

def get_keys(sec):
  '''
  returns: address, private key, hex private key
  '''
  from pywallet import EC_KEY, str_to_long, GetSecret, GetPubKey, SecretToASecret
  pkey = EC_KEY(str_to_long(sec.decode('hex')))
  secret = GetSecret(pkey)
  public_key = GetPubKey(pkey)
  addr = pywallet.public_key_to_bc_address(public_key)
  return addr, SecretToASecret(secret), secret.encode('hex')

verify_services = [ 'blockchain', 'local' ]

def verify_fn(fn, service):
  csum = sha256sum(fn)
  print "Checksum: %s" % csum
  keys = get_keys(csum)
  # does keys[0] exist?
  return verify(keys[0], service)

def verify(pubkey, service):
  '''
  This function verifies the given ``hashsum``.
  '''
  print "Checking %s" % pubkey
  if service == "blockchain":
    import urllib2, json
    q = urllib2.urlopen("http://blockchain.info/address/%s?format=json" % pubkey)
    data = json.loads(q.read())
    if data['total_received'] > 0:
      # get min block height of all transactoins:
      bh = min(_["block_height"] for _ in data["txs"])
      q2 = urllib2.urlopen("http://blockchain.info/rawblock/%s?format=json" % bh)
      data2 = json.loads(q2.read())
      ts = data2["time"]
      from datetime import datetime
      ts = datetime.utcfromtimestamp(ts)
      return True, ts.isoformat()
    return False, None
  else:
    print "Service %s not supported." % service
    return False

def testify(data):
  '''
  For the given ``data``, calculate the Bitcoin address where funds
  shoule be sent to.
  '''
  csum = sha256sum(data)
  print "Checksum: %s" % csum
  keys = get_keys(csum)
  print "Send a small amount to %s now" % keys[0]
  return keys

