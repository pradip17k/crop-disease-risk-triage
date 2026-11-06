"""Capture heuristics, not a trained leaf/OOD detector.
Detect substantial alpha and regular neutral checkerboard borders commonly baked
into stock cutouts. Does not establish whether an accepted photo is a real leaf.
"""
import math

def alternating_border(pixels):
    # Neutral, near-flat alternating bands; plain backgrounds must not trigger.
    if len(pixels)<64:return False
    gray=[]
    for pixel in pixels:
        rgb=pixel[:3]
        if max(rgb)-min(rgb)>4:return False
        gray.append(sum(rgb)/3)
    low,high=min(gray),max(gray)
    if low<140 or not 8<=high-low<=80:return False
    midpoint=(low+high)/2
    clusters=[[v for v in gray if v<=midpoint],[v for v in gray if v>midpoint]]
    if any(not c or max(c)-min(c)>6 for c in clusters):return False
    gray=[low if v<=midpoint else high for v in gray]
    runs=[];last=gray[0];length=0
    for value in gray:
        if value==last:length+=1
        else:runs.append((last,length));last=value;length=1
    runs.append((last,length))
    if len(runs)<7:return False
    middle=runs[1:-1];levels=sorted({v for v,n in middle})
    if len(levels)!=2 or not 8<=levels[1]-levels[0]<=80 or levels[0]<140:return False
    widths=[n for v,n in middle];typical=sorted(widths)[len(widths)//2]
    if not 4<=typical<=80 or max(widths)-min(widths)>2:return False
    return all(middle[i][0]!=middle[i-1][0] for i in range(1,len(middle)))

def check_cutout(image):
    rgba=image.convert('RGBA');w,h=rgba.size
    alpha=rgba.getchannel('A').histogram();transparent=sum(alpha[:250])/(w*h)
    if transparent>.15:
        return 'This image has a substantial transparent background and may be a cutout. Use an original camera photograph of a leaf.'
    # Inspect bounded-resolution outer edges; never use filename or disease label.
    ratio=min(1,512/max(w,h));rgba=rgba.resize((max(1,round(w*ratio)),max(1,round(h*ratio))))
    w,h=rgba.size
    lines=[[rgba.getpixel((x,y)) for x in range(w)] for y in [0,h-1]]
    lines += [[rgba.getpixel((x,y)) for y in range(h)] for x in [0,w-1]]
    if sum(alternating_border(line) for line in lines)>=2:
        return 'A regular checkerboard background suggests an edited cutout. Use an original photograph with a natural background; no disease inference was performed.'
    return None
