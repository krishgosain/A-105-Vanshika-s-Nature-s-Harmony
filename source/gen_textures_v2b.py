import numpy as np, os, sys
from PIL import Image, ImageFilter, ImageDraw
sys.argv=[sys.argv[0], sys.argv[1]]
exec(open("scripts/gen_textures_v2.py").read().split("# ------------------------------------------------------------- Calacatta")[0])
OUT=sys.argv[1]
def marble2(N, base, vein, gold, seed, nveins=3, width=(0.006,0.014)):
    r=np.random.default_rng(seed); yy,xx=np.mgrid[0:N,0:N]/N
    a=np.ones((N,N,3))*np.array(base,float)
    cloud=fbm(N,N,2,5,seed+1); a+=(cloud[...,None]-0.5)*22
    grey=fbm(N,N,3,4,seed+2); a-= np.clip(grey-0.62,0,1)[...,None]*60  # soft grey drifts
    for v in range(nveins):
        warp=fbm(N,N,2,3,seed+10+v)
        ang=r.uniform(0.5,1.0)*(1 if v%2==0 else -0.6)
        f=(xx*np.cos(ang)+yy*np.sin(ang))*r.uniform(0.9,1.6)+warp*r.uniform(0.18,0.3)+r.random()
        d=np.abs((f%1.0)-0.5); w=r.uniform(*width)*0.45
        m=np.exp(-(d/w)**2); halo=np.exp(-(d/(w*7))**2)
        col=np.array(gold if v==1 else vein,float)
        a=a*(1-halo[...,None]*0.12)+col*halo[...,None]*0.12
        a=a*(1-m[...,None]*0.8)+col*m[...,None]*0.8
        # branch veins
        warp2=fbm(N,N,4,3,seed+40+v); f2=(xx*np.cos(ang+0.7)+yy*np.sin(ang+0.7))*3+warp2*0.8
        d2=np.abs((f2%1.0)-0.5); m2=np.exp(-(d2/(w*0.35))**2)*np.clip(1-d*6,0,1)
        a=a*(1-m2[...,None]*0.6)+col*m2[...,None]*0.6
    return a
N=2048
a=marble2(N,[243,240,235],[120,116,112],[178,148,106],3,3); a[:3]*=0.86; a[:,:3]*=0.86
save(a,"marble_calacatta.jpg")
save(marble2(1024,[238,235,230],[130,124,118],[186,156,112],21,3),"marble_counter.jpg")
save(marble2(1024,[34,34,36],[170,166,158],[190,160,110],31,3,(0.004,0.009)),"marble_nero.jpg")
# true herringbone: planks 0.6 x 0.1 m (N=6 cells), texture 1.2 m = 12 cells
T=2048; cells=12; w=T/cells; Np=6
yy,xx=np.mgrid[0:T,0:T].astype(float)
ca=np.floor(xx/w).astype(int); cb=np.floor(yy/w).astype(int)
s=(ca+cb)%(2*Np)
horiz=s<Np
a0=ca-s; b0=cb-(s-Np)
pid=np.where(horiz, a0*131+cb*17, ca*131+b0*17+7)
pal=np.array([[178,130,86],[192,142,94],[166,118,78],[186,136,92],[172,126,84],[198,150,102],[182,132,88]],float)
col=pal[(np.abs(pid)*7919)%len(pal)]
g=fbm(T,T,24,4,71)
# grain along plank direction
gl=np.where(horiz, np.sin(yy/w*20+g*6), np.sin(xx/w*20+g*6))*0.5+0.5
a=col*(0.86+0.12*gl[...,None]+0.08*g[...,None])
fx=xx/w-ca; fy=yy/w-cb
edge=np.where(horiz,(fy<0.03)|(fy>0.97)|(((ca-a0)==0)&(fx<0.012))|(((ca-a0)==Np-1)&(fx>0.988)),
                    (fx<0.03)|(fx>0.97)|(((cb-b0)==0)&(fy<0.012))|(((cb-b0)==Np-1)&(fy>0.988)))
a[edge]*=0.5
save(a,"herringbone.jpg")
h=np.where(edge,0.0,1.0); h=np.array(Image.fromarray((h*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2)),float)/255
save(normal_from_height(h,4),"herringbone_n.png")
# gallery abstracts: organic-geometric (arches, moons, circles) on textured paper
def art(W,H,bg,shapes,seed):
    r=np.random.default_rng(seed)
    a=np.ones((H,W,3))*np.array(bg,float)+(fbm(H,W,3,5,seed,tile=False)[...,None]-0.5)*16
    im=Image.fromarray(np.clip(a,0,255).astype(np.uint8)).convert("RGBA")
    for sh in shapes:
        kind,c,box=sh[0],sh[1],sh[2]
        layer=Image.new("L",(W,H),0); d=ImageDraw.Draw(layer)
        x0,y0,x1,y1=[int(v*(W if k%2==0 else H)) for k,v in enumerate(box)]
        if kind=="circle": d.ellipse([x0,y0,x1,y1],fill=255)
        elif kind=="arch":
            rr=(x1-x0)//2; d.rectangle([x0,y0+rr,x1,y1],fill=255); d.ellipse([x0,y0,x1,y0+2*rr],fill=255)
        elif kind=="half": d.pieslice([x0,y0,x1,y1+(y1-y0)],180,360,fill=255)
        elif kind=="line":
            pts=[(x0+(x1-x0)*t, y0+(y1-y0)*0.5+np.sin(t*np.pi*1.3)*(y1-y0)*0.5) for t in np.linspace(0,1,60)]
            d.line(pts,fill=255,width=max(3,int(W*0.006)),joint="curve")
        layer=layer.filter(ImageFilter.GaussianBlur(1.2))
        tex=fbm(H,W,30,4,seed+len(sh[0]),tile=False)
        col=np.array(c,float)[None,None,:]*(0.9+0.16*tex[...,None])
        if kind=="gold": pass
        fill=Image.fromarray(np.clip(col,0,255).astype(np.uint8)).convert("RGBA")
        fill.putalpha(layer)
        im=Image.alpha_composite(im,fill)
    a=np.array(im.convert("RGB"),float)+(fbm(H,W,180,2,seed+7,tile=False)[...,None]-0.5)*10
    return a
G=[198,164,98]
save(art(2000,1200,[230,222,208],[("arch",[176,112,82],(0.12,0.18,0.36,0.95)),("circle",[52,74,72],(0.42,0.22,0.70,0.68)),("half",[214,196,170],(0.30,0.55,0.62,0.80)),("circle",G,(0.74,0.16,0.84,0.33)),("line",[40,38,36],(0.08,0.40,0.92,0.62))],401),"art_living.jpg")
save(art(1200,1500,[226,216,200],[("arch",[120,96,78],(0.22,0.20,0.78,0.90)),("circle",G,(0.40,0.10,0.64,0.30)),("half",[60,56,52],(0.10,0.70,0.90,0.90))],402),"art_dining.jpg")
save(art(1600,1000,[214,210,204],[("circle",[84,98,110],(0.18,0.20,0.48,0.80)),("arch",[170,176,178],(0.52,0.25,0.74,0.95)),("line",[40,44,50],(0.10,0.45,0.90,0.60))],403),"art_br3.jpg")
save(art(1000,1400,[228,220,206],[("arch",[34,38,44],(0.20,0.18,0.80,0.92)),("circle",G,(0.36,0.30,0.64,0.50))],404),"art_foyer.jpg")
print("v2b ok")
