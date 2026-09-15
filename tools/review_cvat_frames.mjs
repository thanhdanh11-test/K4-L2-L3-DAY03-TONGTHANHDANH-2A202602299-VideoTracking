// Run inside ego-browser's Node runtime. Render source pixels + saved CVAT
// annotations for frame-by-frame visual review, without model predictions.
import fs from 'node:fs/promises';
const root = '/Users/macos/AIVIN_LAB/K4-L2-DAY03-TONGTHANHDANH-2A202602299-VideoTracking';
export async function backup(page) {
  await fs.mkdir(`${root}/annotations/review`, {recursive:true});
  for (const job of [4,5]) {
    const response = await page.fetch(`/api/jobs/${job}/annotations`);
    if (!response.ok) throw new Error(`Cannot read job ${job}`);
    await fs.writeFile(`${root}/annotations/review/before-job-${job}.json`, response.body, {flag:'wx'});
  }
}
export async function sheet(page, clip, start, count=10, revised=false) {
  const job = clip === 1 ? 5 : 4;
  const ann = JSON.parse(await fs.readFile(`${root}/annotations/review/${revised?'revised':'before'}-job-${job}.json`, 'utf8'));
  const frames=[];
  for(let f=start; f<start+count && f<=(clip===1?190:60); f++) {
    const path=`${root}/data/clips/clip_0${clip}/img1/${String(f).padStart(6,'0')}.jpg`;
    const boxes=[];
    ann.tracks.forEach((t,index)=>{
      const s=t.shapes.find(s=>s.frame===f-1);
      if(s && !s.outside) boxes.push({id:index+1,p:s.points,occluded:s.occluded});
    });
    frames.push({f,src:`data:image/jpeg;base64,${(await fs.readFile(path)).toString('base64')}`,boxes});
  }
  const result=await page.evaluate(async ({frames,clip})=>{
    const top=clip===1?210:0, h=540-top, cellH=h+28;
    const c=document.createElement('canvas'); c.width=1920;c.height=Math.ceil(frames.length/2)*cellH;
    const ctx=c.getContext('2d');ctx.fillStyle='#151515';ctx.fillRect(0,0,c.width,c.height);
    const colors=['#ffef00','#00ffff','#ff66ff','#ff5500','#00ff77','#ff9999','#99bbff','#ffffff'];
    for(let i=0;i<frames.length;i++) {
      const {f,src,boxes}=frames[i];const x=(i%2)*960,y=Math.floor(i/2)*cellH+28;
      const img=new Image();img.src=src;await img.decode();ctx.drawImage(img,0,top,960,h,x,y,960,h);
      ctx.font='19px monospace';ctx.fillStyle='white';ctx.fillText(`clip ${clip} | image ${f} / CVAT ${f-1}`,x+5,y-7);
      for(const b of boxes){ const [l,t,r,bt]=b.p;ctx.strokeStyle=colors[(b.id-1)%colors.length];ctx.lineWidth=1;ctx.strokeRect(x+l,y+t-top,r-l,bt-t);ctx.fillStyle=ctx.strokeStyle;ctx.font='15px monospace';ctx.fillText(String(b.id),x+l+2,y+t-top-3);}
      ctx.strokeStyle='#ffffff33';ctx.font='11px monospace';ctx.fillStyle='#ffffffaa';
      for(let xx=100;xx<960;xx+=100){ctx.beginPath();ctx.moveTo(x+xx,y);ctx.lineTo(x+xx,y+h);ctx.stroke();ctx.fillText(String(xx),x+xx,y+12);}
    }
    return c.toDataURL('image/png').split(',')[1];
  },{frames,clip});
  const path=`/tmp/review-clip${clip}-${start}${revised?'-after':''}.png`;
  await fs.writeFile(path,Buffer.from(result,'base64'));
  console.log(path);
}
export async function crops(page, clip, id, start, count=20, revised=false, region=null) {
  const job=clip===1?5:4;
  const ann=JSON.parse(await fs.readFile(`${root}/annotations/review/${revised?'revised':'before'}-job-${job}.json`,'utf8'));
  const track=ann.tracks[id-1], frames=[];
  for(let f=start;f<start+count&&f<=(clip===1?190:60);f++){
    const shape=track.shapes.find(s=>s.frame===f-1)||track.shapes.filter(s=>s.frame<f-1).at(-1)||track.shapes[0];
    const src=`data:image/jpeg;base64,${(await fs.readFile(`${root}/data/clips/clip_0${clip}/img1/${String(f).padStart(6,'0')}.jpg`)).toString('base64')}`;
    frames.push({f,src,p:region||shape.points,outside:shape.outside});
  }
  const result=await page.evaluate(async ({frames,clip,id})=>{
    const W=400,H=240,c=document.createElement('canvas');c.width=W*4;c.height=Math.ceil(frames.length/4)*H;
    const ctx=c.getContext('2d');ctx.fillStyle='#181818';ctx.fillRect(0,0,c.width,c.height);
    for(let i=0;i<frames.length;i++){
      const {f,src,p,outside}=frames[i];const [l,t,r,b]=p;
      const left=Math.max(0,Math.floor(l-40)),top=Math.max(0,Math.floor(t-40)),right=Math.min(960,Math.ceil(r+60)),bottom=Math.min(540,Math.ceil(b+45));
      const s=Math.min((W-8)/(right-left),(H-36)/(bottom-top),3),x=(i%4)*W+4,y=Math.floor(i/4)*H+34;
      const img=new Image();img.src=src;await img.decode();ctx.drawImage(img,left,top,right-left,bottom-top,x,y,(right-left)*s,(bottom-top)*s);
      ctx.fillStyle='white';ctx.font='12px monospace';ctx.fillText(`C${clip} ID${id} f${f} ${outside?'OUT':''} [${p.map(Math.round)}]`,x,y-17);
      ctx.strokeStyle='#00ff88';ctx.lineWidth=1;ctx.strokeRect(x+(l-left)*s,y+(t-top)*s,(r-l)*s,(b-t)*s);
      ctx.strokeStyle='#ffffff35';ctx.fillStyle='#fff';ctx.font='10px monospace';
      for(let xx=Math.ceil(left/20)*20;xx<right;xx+=20){ctx.beginPath();ctx.moveTo(x+(xx-left)*s,y);ctx.lineTo(x+(xx-left)*s,y+(bottom-top)*s);ctx.stroke();ctx.fillText(String(xx),x+(xx-left)*s,y+9);}
      for(let yy=Math.ceil(top/20)*20;yy<bottom;yy+=20){ctx.beginPath();ctx.moveTo(x,y+(yy-top)*s);ctx.lineTo(x+(right-left)*s,y+(yy-top)*s);ctx.stroke();ctx.fillText(String(yy),x,y+(yy-top)*s);}
    }
    return c.toDataURL('image/png').split(',')[1];
  },{frames,clip,id});
  const path=`/tmp/crop-c${clip}-id${id}-f${start}${revised?'-after':''}.png`;
  await fs.writeFile(path,Buffer.from(result,'base64'));console.log(path);
}
