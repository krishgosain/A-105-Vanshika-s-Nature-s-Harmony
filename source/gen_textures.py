import numpy as np
from PIL import Image, ImageFilter, ImageOps
import sys, os
OUT=sys.argv[1]; SRC=sys.argv[2]
rng=np.random.default_rng(7)
def noise(h,w,scale,oct=4):
    acc=np.zeros((h,w));amp=1
    for o in range(oct):
        s=max(1,int(scale/(2**o)))
        n=rng.random((h//s+2,w//s+2))
        im=Image.fromarray((n*255).astype(np.uint8)).resize((w+2*s,h+2*s),Image.BICUBIC)
        acc+=np.array(im)[s:s+h,s:s+w]/255*amp; amp*=0.5
    acc-=acc.min(); return acc/acc.max()
def save(a,name):
    Image.fromarray(np.clip(a,0,255).astype(np.uint8)).save(os.path.join(OUT,name),quality=90)
N=1024
# glossy cream floor tiles: texture spans 1.6m => 2x2 tiles of 0.8m
base=np.array([226,219,206.]); a=np.ones((N,N,3))*base
n=noise(N,N,128); a+= (n[...,None]-.5)*14
for t in range(4):  # per-tile tint
    pass
g=np.zeros((N,N),bool); w=3
for k in [0,N//2]: g[:,k:k+w]=True; g[k:k+w,:]=True
a[g]=[200,193,182]; save(a,"floor_tile.jpg")
# wood planks (master): span 1.2m x 1.2m ; planks 0.2 wide x 1.2 long
a=np.zeros((N,N,3)); pw=N//6
cols=[[128,72,38],[140,82,44],[118,64,33],[134,78,40],[122,70,36],[146,88,48]]
grain=noise(N,N,24,3)
for i in range(6):
    off=rng.integers(0,N)
    gr=np.roll(noise(N,pw,40,4),off,axis=0)
    streak=np.sin(np.linspace(0,40,pw)[None,:]+gr*9)*0.5+0.5
    c=np.array(cols[i]); blk=c*(0.82+0.3*streak[...,None]*0.6+0.1*gr[...,None])
    a[:,i*pw:(i+1)*pw]=blk
    a[:,i*pw:i*pw+2]=[70,38,20]
    cut=(off+N//3)%N; a[cut:cut+2,i*pw:(i+1)*pw]=[70,38,20]
a=a.transpose(1,0,2); save(a,"wood_floor.jpg")
# light oak (vertical grain)
gr=noise(N,N,30,4); st=np.sin(np.linspace(0,90,N)[None,:]+gr*14)*.5+.5
a=np.array([186,158,124.])*(0.88+0.14*st[...,None])+ (noise(N,N,8,2)[...,None]-.5)*8
save(a,"oak.jpg")
# walnut (doors, fins)
st=np.sin(np.linspace(0,70,N)[None,:]+gr*16)*.5+.5
a=np.array([112,62,32.])*(0.8+0.3*st[...,None]); save(a,"walnut.jpg")
# marble white with grey-gold veins
def marble(base,vein,n_veins,width,h=N,w=N):
    a=np.ones((h,w,3))*np.array(base,float)
    a+= (noise(h,w,200)[...,None]-.5)*10
    yy,xx=np.mgrid[0:h,0:w]
    for v in range(n_veins):
        warp=noise(h,w,220,5)
        ang=rng.uniform(-1.0,1.0); ph=rng.uniform(0,6.28)
        f=(xx*np.cos(ang)+yy*np.sin(ang))/w*rng.uniform(1.5,3)*6.28+warp*rng.uniform(6,10)+ph
        line=np.abs(np.sin(f)); m=np.clip(1-line/width,0,1)**3
        a=a*(1-m[...,None]*0.8)+np.array(vein,float)*m[...,None]*0.8
    return a
save(marble([238,236,232],[150,140,128],4,0.03),"marble_white.jpg")
save(marble([112,108,104],[175,170,165],3,0.06),"marble_grey.jpg")
save(marble([240,238,236],[185,182,180],3,0.02),"marble_table.jpg")
# bathroom grey tile 0.6m; span 1.2m => 2x2
a=np.zeros((N,N,3))
for i in range(2):
  for j in range(2):
    t=noise(N//2,N//2,90,4); c=rng.uniform(95,120)
    blk=c+ (t-.5)*45; blk=np.stack([blk,blk*1.02,blk*1.04],-1)
    a[i*N//2:(i+1)*N//2,j*N//2:(j+1)*N//2]=blk
a[:, :3]=60; a[:N, N//2:N//2+3]=60; a[:3,:]=60; a[N//2:N//2+3,:]=60
save(a,"bath_tile.jpg")
# light wall tile for bath upper (white-grey large)
a=np.ones((N,N,3))*np.array([214,214,212.]); a+=(noise(N,N,100)[...,None]-.5)*10
a[:, :3]=170; a[:3,:]=170; a[N//2:N//2+3,:]=170; save(a,"bath_tile_light.jpg")
# TV wallpaper: mirror-tile real crop
def seamless_from(path,size=512):
    im=Image.open(path).convert("RGB")
    im=im.resize((size//2,size//2),Image.LANCZOS)
    top=Image.new("RGB",(size,size))
    top.paste(im,(0,0)); top.paste(ImageOps.mirror(im),(size//2,0))
    bot=ImageOps.flip(top.crop((0,0,size,size//2)))
    top.paste(bot,(0,size//2)); return top
seamless_from(f"{SRC}/tv_wallpaper.png").save(f"{OUT}/tv_wallpaper.jpg",quality=90)
# BR2 wallpaper: light grey-blue mottled
n=noise(N,N,160,6); a=np.array([186,192,196.])+ (n[...,None]-.5)*40; save(a,"br2_wallpaper.jpg")
# grey textured wall (master / br3 accent)
n=noise(N,N,60,5); a=np.array([150,150,150.])+(n[...,None]-.5)*25; save(a,"grey_wall.jpg")
# master headboard wall panel: light grey wood
st=np.sin(np.linspace(0,120,N)[None,:]+noise(N,N,40,3)*10)*.5+.5
a=np.array([196,194,188.])*(0.93+0.08*st[...,None]); save(a,"panel_greywood.jpg")
# channel tufted fabric (vertical channels)
x=np.linspace(0,1,N); ch=(np.sin(x*2*np.pi*8)*.5+.5)**0.5
for name,c in [("channel_dark.jpg",[58,60,64]),("channel_beige.jpg",[170,150,122])]:
    a=np.array(c,float)[None,None,:]*(0.65+0.45*ch[None,:,None])*np.ones((N,1,1))
    a+= (noise(N,N,6,2)[...,None]-.5)*10; save(a,name)
# chevron headboard (grey)
yy,xx=np.mgrid[0:N,0:N]/N
f=((np.abs(xx-0.5)+yy)*5)%1; a=np.array([82,82,84.])*(0.75+0.35*np.abs(np.sin(f*np.pi)))[...,None]
save(a,"chevron.jpg")
# fabric textures
for name,c in [("fabric_sofa.jpg",[150,140,132]),("fabric_green.jpg",[38,58,52]),("fabric_bedgrey.jpg",[110,104,112]),("fabric_white.jpg",[236,232,224]),("fabric_teal.jpg",[70,86,92]),("fabric_black.jpg",[38,42,48])]:
    n=noise(N,N,4,2); a=np.array(c,float)+(n[...,None]-.5)*14; save(a,name)
# grey wood slats for ceiling band
a=np.ones((N,N,3))*np.array([110,108,104.]); 
for k in range(0,N,N//16): a[:,k:k+6]=70
a+= (noise(N,N,30,3)[...,None]-.5)*14; save(a,"slats.jpg")
# entry granite / corridor tile
save(marble([70,70,72],[100,100,104],2,0.05),"granite_dark.jpg")
n=noise(N,N,80,4); a=np.array([170,170,168.])+(n[...,None]-.5)*20; a[:, :3]=140;a[:3,:]=140; save(a,"corridor_tile.jpg")
# balcony tile
n=noise(N,N,60,4); a=np.array([158,152,144.])+(n[...,None]-.5)*20; a[:, :3]=120;a[:3,:]=120;a[N//2:N//2+3]=120;a[:,N//2:N//2+3]=120; save(a,"balcony_tile.jpg")
print("ok")
