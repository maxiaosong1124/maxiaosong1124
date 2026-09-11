const path = require('node:path');
const fs = require('node:fs');
const { chromium } = require(process.env.PLAYWRIGHT_PACKAGE || '../tools/render/node_modules/playwright');

(async()=>{
  const root=path.resolve(__dirname,'..');
  const browser=await chromium.launch({headless:true,args:['--no-sandbox','--enable-unsafe-swiftshader']});
  try {
    const page=await browser.newPage({viewport:{width:1056,height:1000},deviceScaleFactor:1});
    const errors=[];page.on('pageerror',e=>errors.push(e.message));
    await page.route('https://**/*',route=>route.abort());
    await page.goto('file://'+path.join(root,'_site/index.html'));
    await page.locator('.terrain-ready canvas').waitFor();
    await page.locator('#terrain-auto').uncheck();
    for(const [name,width] of [['desktop',1056],['mobile',516]]){
      await page.setViewportSize({width,height:1000});
      await page.locator('#terrain').scrollIntoViewIfNeeded();
      const directory=path.join(root,'_frames',name);fs.mkdirSync(directory,{recursive:true});
      const hashes=new Set();
      for(let i=0;i<64;i++){
        const angle=-12+Math.sin(i/64*Math.PI*2)*18;
        const png=await page.evaluate(angle=>{
          const slider=document.querySelector('#terrain-angle');slider.step='any';slider.value=angle;
          slider.dispatchEvent(new Event('input',{bubbles:true}));
          return document.querySelector('#terrain canvas').toDataURL('image/png').split(',')[1];
        },angle);
        hashes.add(png);fs.writeFileSync(path.join(directory,String(i).padStart(3,'0')+'.png'),Buffer.from(png,'base64'));
      }
      if(hashes.size<30)throw new Error('Terrain animation has too few distinct frames');
      console.log(`${name}: 64 frames, ${hashes.size} distinct views`);
    }
    if(errors.length)throw new Error(errors.join('\n'));
  } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
