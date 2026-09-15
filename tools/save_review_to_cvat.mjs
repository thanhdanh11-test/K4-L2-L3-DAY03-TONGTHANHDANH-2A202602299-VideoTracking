import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
const root='/Users/macos/AIVIN_LAB/K4-L2-DAY03-TONGTHANHDANH-2A202602299-VideoTracking/annotations/review';
function semantic(a) {
  return {tags:a.tags,shapes:a.shapes,tracks:a.tracks.map(t=>({
    id:t.id,label_id:t.label_id,group:t.group,frame:t.frame,attributes:t.attributes,
    shapes:t.shapes.map(s=>({frame:s.frame,type:s.type,points:s.points,
      outside:s.outside,occluded:s.occluded,rotation:s.rotation,
      z_order:s.z_order,attributes:s.attributes}))
  }))};
}
export async function save(page) {
  const report={reviewed_frames:{clip_01:190,clip_02:60},exported:false,jobs:[]};
  for(const job of [4,5]) {
    const before=JSON.parse(await fs.readFile(`${root}/before-job-${job}.json`,'utf8'));
    const revised=JSON.parse(await fs.readFile(`${root}/revised-job-${job}.json`,'utf8'));
    const currentResponse=await page.fetch(`/api/jobs/${job}/annotations`);
    assert(currentResponse.ok,'Read current annotations failed');
    const current=JSON.parse(currentResponse.body);
    assert.deepEqual(semantic(current),semantic(before),'Annotations changed since backup; refusing overwrite');
    assert.deepEqual(revised.tracks.map(t=>t.id),before.tracks.map(t=>t.id));
    for(const t of revised.tracks) {
      assert(t.shapes.length>0);
      const seen=new Set();
      for(const s of t.shapes) {
        assert(!seen.has(s.frame)); seen.add(s.frame);
        assert(s.frame>=0 && s.frame<(job===4?60:190));
        const [l,top,r,b]=s.points;
        assert(l>=0 && top>=0 && r<=960 && b<=540 && l<r && top<b);
      }
    }
    const payload={version:current.version,tags:[],shapes:[],tracks:revised.tracks};
    const result=await page.evaluate(async ({job,payload})=>{
      const csrf=document.cookie.split('; ').find(v=>v.startsWith('csrftoken='))?.slice(10);
      const headers={'Content-Type':'application/json'};
      if(csrf)headers['X-CSRFToken']=decodeURIComponent(csrf);
      const response=await fetch(`/api/jobs/${job}/annotations?action=update`,{
        method:'PATCH',headers,body:JSON.stringify(payload),credentials:'same-origin'
      });
      return {ok:response.ok,status:response.status,body:await response.text()};
    },{job,payload});
    if(!result.ok)throw Error(`Job ${job} save failed (${result.status}): ${result.body.slice(0,500)}`);
    const fetched=await page.fetch(`/api/jobs/${job}/annotations`);
    assert(fetched.ok);
    const saved=JSON.parse(fetched.body);
    assert.deepEqual(semantic(saved),semantic(revised),'Server readback does not match reviewed draft');
    await fs.writeFile(`${root}/saved-job-${job}.json`,JSON.stringify(saved,null,2)+'\n');
    const visible=saved.tracks.reduce((n,t)=>n+t.shapes.filter(s=>!s.outside).length,0);
    report.jobs.push({job,tracks:saved.tracks.length,visible_boxes:visible,
      track_ids_preserved:true,readback_verified:true});
    console.log(`Job ${job}: saved and verified ${visible} visible boxes; track IDs preserved`);
  }
  await fs.writeFile(`${root}/review-result.json`,JSON.stringify(report,null,2)+'\n');
}
