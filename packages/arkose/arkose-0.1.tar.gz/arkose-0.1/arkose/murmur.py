def x64Add(m, n):
    m = [m[0] >> 16, m[0] & 0xffff, m[1] >> 16, m[1] & 0xffff]
    n = [n[0] >> 16, n[0] & 0xffff, n[1] >> 16, n[1] & 0xffff]
    o = [0, 0, 0, 0]
    o[3] += m[3] + n[3]
    o[2] += o[3] >> 16
    o[3] &= 0xffff
    o[2] += m[2] + n[2]
    o[1] += o[2] >> 16
    o[2] &= 0xffff
    o[1] += m[1] + n[1]
    o[0] += o[1] >> 16
    o[1] &= 0xffff
    o[0] += m[0] + n[0]
    o[0] &= 0xffff
    return [(o[0] << 16) | o[1], (o[2] << 16) | o[3]]

def x64Multiply(m, n):
    m = [m[0] >> 16, m[0] & 0xffff, m[1] >> 16, m[1] & 0xffff]
    n = [n[0] >> 16, n[0] & 0xffff, n[1] >> 16, n[1] & 0xffff]
    o = [0, 0, 0, 0]
    o[3] += m[3] * n[3]
    o[2] += o[3] >> 16
    o[3] &= 0xffff
    o[2] += m[2] * n[3]
    o[1] += o[2] >> 16
    o[2] &= 0xffff
    o[2] += m[3] * n[2]
    o[1] += o[2] >> 16
    o[2] &= 0xffff
    o[1] += m[1] * n[3]
    o[0] += o[1] >> 16
    o[1] &= 0xffff
    o[1] += m[2] * n[2]
    o[0] += o[1] >> 16
    o[1] &= 0xffff
    o[1] += m[3] * n[1]
    o[0] += o[1] >> 16
    o[1] &= 0xffff
    o[0] += m[0] * n[3] + m[1] * n[2] + m[2] * n[1] + m[3] * n[0]
    o[0] &= 0xffff
    return [(o[0] << 16) | o[1], (o[2] << 16) | o[3]]

def x64Rotl(m, n):
    return [(m[0] << n) | (m[1] >> (32 - n)), (m[1] << n) | (m[0] >> (32 - n))] if n < 32 else [(m[1] << (n - 32)) | (m[0] >> (64 - n)), (m[0] << (n - 32)) | (m[1] >> (64 - n))]

def x64LeftShift(m, n):
    return [(m[0] << n) | (m[1] >> (32 - n)), m[1] << n] if n < 32 else [m[1] << (n - 32), 0]

def x64Xor(m, n):
    return [m[0] ^ n[0], m[1] ^ n[1]]

def x64Fmix(h):
    h = x64Xor(h, [0, h[0] >> 1])
    h = x64Multiply(h, [0xFF51AFD7ED558CCD, 0xC4CEB9FE1A85EC53])
    h = x64Xor(h, [0, h[0] >> 1])
    h = x64Multiply(h, [0xC4CEB9FE1A85EC53, 0xFF51AFD7ED558CCD])
    h = x64Xor(h, [0, h[0] >> 1])
    return h

def murmur_hash(key, seed=0):
    key = key.encode('utf-8')
    length = len(key)
    nblocks = length // 16
    
    h1 = [seed, seed]
    h2 = [seed, seed]
    
    c1 = [0x87c37b91114253d5, 0x4cf5ad432745937f]
    c2 = [0x4cf5ad432745937f, 0x87c37b91114253d5]
    
    # Body
    for block_start in range(0, nblocks * 16, 16):
        k1 = [int.from_bytes(key[block_start:block_start+8], 'little'), int.from_bytes(key[block_start+8:block_start+16], 'little')]
        
        k1 = x64Multiply(k1, c1)
        k1 = x64Rotl(k1, 31)
        k1 = x64Multiply(k1, c2)
        
        h1 = x64Xor(h1, k1)
        h1 = x64Rotl(h1, 27)
        h1 = x64Add(h1, h2)
        h1 = x64Add(x64Multiply(h1, [0, 5]), [0, 0x52dce729])
        
        k2 = [int.from_bytes(key[block_start+8:block_start+16], 'little'), int.from_bytes(key[block_start:block_start+8], 'little')]
        
        k2 = x64Multiply(k2, c2)
        k2 = x64Rotl(k2, 33)
        k2 = x64Multiply(k2, c1)
        
        h2 = x64Xor(h2, k2)
        h2 = x64Rotl(h2, 31)
        h2 = x64Add(h2, h1)
        h2 = x64Add(x64Multiply(h2, [0, 5]), [0, 0x38495ab5])
    
    # Tail
    tail = key[nblocks * 16:]
    
    k1 = [0, 0]
    k2 = [0, 0]
    
    if len(tail) >= 15:
        k2 = x64Xor(k2, x64LeftShift([0, tail[14]], 48))
    if len(tail) >= 14:
        k2 = x64Xor(k2, x64LeftShift([0, tail[13]], 40))
    if len(tail) >= 13:
        k2 = x64Xor(k2, x64LeftShift([0, tail[12]], 32))
    if len(tail) >= 12:
        k2 = x64Xor(k2, x64LeftShift([0, tail[11]], 24))
    if len(tail) >= 11:
        k2 = x64Xor(k2, x64LeftShift([0, tail[10]], 16))
    if len(tail) >= 10:
        k2 = x64Xor(k2, x64LeftShift([0, tail[9]], 8))
    if len(tail) >= 9:
        k2 = x64Xor(k2, [0, tail[8]])
        k2 = x64Multiply(k2, c2)
        k2 = x64Rotl(k2, 33)
        k2 = x64Multiply(k2, c1)
        h2 = x64Xor(h2, k2)
    
    if len(tail) >= 8:
        k1 = x64Xor(k1, x64LeftShift([0, tail[7]], 56))
    if len(tail) >= 7:
        k1 = x64Xor(k1, x64LeftShift([0, tail[6]], 48))
    if len(tail) >= 6:
        k1 = x64Xor(k1, x64LeftShift([0, tail[5]], 40))
    if len(tail) >= 5:
        k1 = x64Xor(k1, x64LeftShift([0, tail[4]], 32))
    if len(tail) >= 4:
        k1 = x64Xor(k1, x64LeftShift([0, tail[3]], 24))
    if len(tail) >= 3:
        k1 = x64Xor(k1, x64LeftShift([0, tail[2]], 16))
    if len(tail) >= 2:
        k1 = x64Xor(k1, x64LeftShift([0, tail[1]], 8))
    if len(tail) >= 1:
        k1 = x64Xor(k1, [0, tail[0]])
        k1 = x64Multiply(k1, c1)
        k1 = x64Rotl(k1, 31)
        k1 = x64Multiply(k1, c2)
        h1 = x64Xor(h1, k1)
    
    # Finalization
    h1 = x64Xor(h1, [0, length])
    h2 = x64Xor(h2, [0, length])
    
    h1 = x64Add(h1, h2)
    h2 = x64Add(h2, h1)
    
    h1 = x64Fmix(h1)
    h2 = x64Fmix(h2)
    
    h1 = x64Add(h1, h2)
    h2 = x64Add(h2, h1)
    
    return f"{h1[0]:08x}{h1[1]:08x}{h2[0]:08x}{h2[1]:08x}"
