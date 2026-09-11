(() => {
  const host = document.querySelector('#terrain');
  if (!host || !window.THREE) return;
  const T = window.THREE;
  let renderer;
  try {
    renderer = new T.WebGLRenderer({ antialias: true, alpha: true, preserveDrawingBuffer: true });
  } catch { return; }
  const days = window.PROFILE.days;
  const scene = new T.Scene();
  const camera = new T.OrthographicCamera(-30,30,15,-15,.1,200);
  const group = new T.Group();
  scene.add(group);
  scene.add(new T.HemisphereLight(0xe5ffd6,0x26302a,2));
  const light = new T.DirectionalLight(0xffffff,2.5);
  light.position.set(-10,25,15); scene.add(light);
  const base = new T.Mesh(new T.BoxGeometry(55,.3,9),new T.MeshStandardMaterial({color:0x111e17,roughness:1}));
  base.position.y=-.28; group.add(base);
  const grid = new T.GridHelper(54,54,0x496341,0x263e2e);
  grid.scale.z=9/54; grid.position.y=-.1; group.add(grid);
  const peak = Math.max(1,...days.map(d=>d.count));
  const colors = [0x26382d,0x456730,0x679937,0x93c84d,0xb5ff5b];
  const geometry = new T.BoxGeometry(.78,1,.78);
  const bars = days.map((day,i)=>{
    const h=.16+Math.log1p(day.count)/Math.log1p(peak)*6;
    const bar=new T.Mesh(geometry,new T.MeshStandardMaterial({color:colors[day.level],roughness:.7,metalness:.12}));
    bar.scale.y=h; bar.position.set(Math.floor(i/7)-26,h/2,i%7-3);
    bar.userData.day=day; group.add(bar); return bar;
  });
  const canvas=renderer.domElement;
  canvas.setAttribute('aria-label','3D GitHub 贡献地形');
  canvas.setAttribute('role','img');
  renderer.setPixelRatio(Math.min(devicePixelRatio,2));
  host.append(canvas);
  const controls=document.querySelector('#terrain-controls');
  const slider=document.querySelector('#terrain-angle');
  const date=document.querySelector('#terrain-day');
  const reducedMotion=matchMedia('(prefers-reduced-motion: reduce)');
  const autoLabel=document.createElement('label');
  const auto=document.createElement('input');auto.type='checkbox';auto.id='terrain-auto';auto.checked=!reducedMotion.matches;
  autoLabel.append(auto,document.createTextNode('自动旋转'));controls.prepend(autoLabel);
  let offset=0, visible=false, frame=0, previous=0, phase=0;
  function stopAuto(){auto.checked=false;offset=0;}
  date.min=days[0].date;date.max=days.at(-1).date;date.value=days.at(-1).date;
  let selected;
  function select(bar) {
    if(selected) selected.material.emissive.setHex(0);
    selected=bar;
    if(bar){bar.material.emissive.setHex(0x493044);date.value=bar.userData.day.date;document.querySelector('#heatmap-detail').textContent=`${bar.userData.day.date} · ${bar.userData.day.count} contributions`;}
  }
  function render() {
    const w=host.clientWidth,h=host.clientHeight;
    if(!w||!h)return;
    renderer.setSize(w,h,false);
    const aspect=w/h, half=Math.max(14,31/aspect);
    camera.left=-half*aspect;camera.right=half*aspect;camera.top=half;camera.bottom=-half;
    camera.position.set(0,30,38);camera.lookAt(0,1,0);camera.updateProjectionMatrix();
    group.rotation.y=(Number(slider.value)+offset)*Math.PI/180;
    renderer.render(scene,camera);
  }
  slider.addEventListener('input',()=>{stopAuto();render();});
  date.addEventListener('change',()=>{stopAuto();select(bars.find(b=>b.userData.day.date===date.value));render();});
  const ray=new T.Raycaster();const pointer=new T.Vector2();let drag=null;
  canvas.addEventListener('pointerdown',e=>{stopAuto();drag={x:e.clientX,angle:Number(slider.value)};canvas.setPointerCapture(e.pointerId);});
  canvas.addEventListener('pointerup',()=>{drag=null;});
  canvas.addEventListener('pointercancel',()=>{drag=null;});
  canvas.addEventListener('pointermove',e=>{
    if(drag){slider.value=Math.max(-65,Math.min(65,drag.angle+(e.clientX-drag.x)*.25));render();return;}
    const rect=canvas.getBoundingClientRect();pointer.set((e.clientX-rect.left)/rect.width*2-1,-(e.clientY-rect.top)/rect.height*2+1);
    ray.setFromCamera(pointer,camera);const hit=ray.intersectObjects(bars)[0];if(hit){select(hit.object);render();}
  });
  canvas.addEventListener('webglcontextlost',e=>{e.preventDefault();host.classList.remove('terrain-ready');controls.hidden=true;});
  canvas.addEventListener('webglcontextrestored',()=>{render();host.classList.add('terrain-ready');controls.hidden=false;});
  new ResizeObserver(render).observe(host);
  function animate(now){
    frame=0;
    if(!visible||document.hidden||!auto.checked)return;
    if(now-previous>32){phase+=Math.min(now-previous,64)/1000;previous=now;offset=Math.sin(phase*.45)*8;render();}
    frame=requestAnimationFrame(animate);
  }
  function resume(){if(frame)cancelAnimationFrame(frame);frame=0;previous=performance.now();if(visible&&!document.hidden&&auto.checked)frame=requestAnimationFrame(animate);}
  auto.addEventListener('change',()=>{if(!auto.checked){offset=0;render();}resume();});
  reducedMotion.addEventListener('change',()=>{if(reducedMotion.matches){stopAuto();render();resume();}});
  document.addEventListener('visibilitychange',resume);
  new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;resume();}).observe(host);
  render();host.classList.add('terrain-ready');controls.hidden=false;
})();
