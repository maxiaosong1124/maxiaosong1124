const data = window.PROFILE;
const $ = (selector) => document.querySelector(selector);
const escapeHTML = (value) => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const localDate = (value) => new Intl.DateTimeFormat('sv-SE', {timeZone:'Asia/Shanghai', year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit'}).format(new Date(value));
const lastDay = data.days.at(-1).date;
const personal = data.personal;
if (!document.querySelector('.profile-intro')) {
$('.role').innerHTML = 'SYSTEMS <span>/</span> HPC <span>/</span> ML INFERENCE';
$('.stack').innerHTML = personal.languages.map(name => `<span>${escapeHTML(name)}</span>`).join('') + '<b>/</b>' + personal.frameworks.map(name => `<span>${escapeHTML(name)}</span>`).join('');
const introHTML = `<div lang="zh-CN"><p>${escapeHTML(personal.intro)}</p><p>${escapeHTML(personal.exploration)}</p></div><div lang="en" class="english-copy"><p>${escapeHTML(personal.en.intro)}</p><p>${escapeHTML(personal.en.exploration)}</p></div>`;
const learningHTML = `<p lang="zh-CN">${escapeHTML(personal.learning)}</p><p lang="en" class="english-copy">${escapeHTML(personal.en.learning)}</p>`;
const visionHTML = `<p lang="zh-CN">${escapeHTML(personal.vision)}</p><p lang="en" class="english-copy">${escapeHTML(personal.en.vision)}</p>`;
const aboutHTML = `<div class="personal-copy">${introHTML}<p><span class="section-meta">TECH STACK</span><br>${escapeHTML(personal.languages.join(' · '))}</p><p><span class="section-meta">FRAMEWORKS</span><br>${escapeHTML(personal.frameworks.join(' · '))}</p></div>`;
const horizonHTML = `<div class="personal-copy"><div><span class="section-meta">CURRENTLY LEARNING</span>${learningHTML}</div><div class="vision"><span class="section-meta">FUTURE VISION</span>${visionHTML}</div></div>`;
const aboutSections = document.querySelectorAll('.blank-section');
aboutSections[0].querySelector('.empty-code').outerHTML = aboutHTML;
aboutSections[1].querySelector('.empty-code').outerHTML = horizonHTML;
const introSection = aboutSections[0];
$('.bottom-grid').removeAttribute('id');
introSection.id = 'about';
introSection.classList.add('profile-intro');
introSection.querySelector('h2').innerHTML = '<span>00 /</span> 个人介绍 <span class="section-meta">ABOUT ME</span>';
introSection.querySelector('.personal-copy').innerHTML = introHTML;
introSection.insertAdjacentHTML('beforeend', `<div class="personal-copy profile-directions"><div><span class="section-meta">CURRENTLY LEARNING / 当前学习方向</span>${learningHTML}</div><div class="vision"><span class="section-meta">FUTURE VISION / 未来愿景</span>${visionHTML}</div></div>`);
aboutSections[1].remove();
introSection.querySelector(':scope > .section-meta').remove();
$('.subnav').before(introSection);
const readmeHeadings = [...document.querySelectorAll('.readme-body h3')];
readmeHeadings.find(el => el.textContent.includes('About Me')).insertAdjacentHTML('afterend', aboutHTML + `<div><strong>当前学习方向 / Currently learning</strong>${learningHTML}<h4>未来愿景 / Future vision</h4>${visionHTML}</div>`);
readmeHeadings.find(el => el.textContent.includes('Next Horizon')).remove();
const readmeIntro = readmeHeadings.find(el => el.textContent.includes('About Me'));
const readmeCopy = readmeIntro.nextElementSibling;
const readmeLearning = readmeCopy.nextElementSibling;
readmeIntro.textContent = '00 / 个人介绍 · About Me';
$('.readme-body > img:nth-of-type(2)').before(readmeIntro, readmeCopy, readmeLearning);
}
$('#date-range').textContent = `${data.days[0].date} — ${lastDay}`;
$('#snapshot-time').textContent = `SNAPSHOT / ${localDate(data.updated)} CST`;
const clock = () => { $('#clock').textContent = new Intl.DateTimeFormat('en-GB', {timeZone:'Asia/Shanghai',hour:'2-digit',minute:'2-digit',second:'2-digit'}).format(new Date()) + ' UTC+8'; };
clock(); setInterval(clock, 1000);
$('#metrics').innerHTML = [[data.total.toLocaleString(),'TOTAL CONTRIBUTIONS','/ year'],[data.active,'ACTIVE DAYS','days'],[data.best,'LONGEST STREAK','days'],[data.user.public_repos,'PUBLIC REPOSITORIES','repos']].map(([n,label,unit])=>`<div class="metric"><div class="metric-value">${n}<small>${unit}</small></div><div class="metric-label">${label}</div></div>`).join('');
let previousMonth = '';
$('#heatmap').replaceChildren();
$('#month-labels').replaceChildren();
data.days.forEach((day, index) => {
  const cell = document.createElement('span');
  cell.dataset.level = day.level;
  cell.title = `${day.date} · ${day.count} contributions`;
  cell.setAttribute('aria-label', cell.title);
  cell.addEventListener('mouseenter', () => { $('#heatmap-detail').textContent = cell.title; });
  cell.addEventListener('mouseleave', () => { $('#heatmap-detail').textContent = 'GITHUB CONTRIBUTIONS'; });
  $('#heatmap').append(cell);
  if (index % 7 === 0 && day.date.slice(0,7) !== previousMonth) {
    const label = document.createElement('span');
    label.textContent = new Date(day.date+'T12:00:00Z').toLocaleString('en-US',{month:'short',timeZone:'UTC'});
    label.style.gridColumn = `${Math.floor(index / 7) + 1} / span 1`;
    $('#month-labels').append(label); previousMonth = day.date.slice(0,7);
  }
});
$('#contributed-projects').innerHTML = data.contributed.length ? data.contributed.map(([repo,count]) => {
  const [owner, ...name] = repo.split('/');
  return `<a class="project" href="https://github.com/${escapeHTML(repo)}" target="_blank" rel="noreferrer"><span><span class="project-name"><span class="muted">${escapeHTML(owner)} / </span>${escapeHTML(name.join('/'))}</span><span class="project-sub">PUBLIC CONTRIBUTIONS</span></span><span class="project-right">${count}<small>EVENTS ↗</small></span></a>`;
}).join('') : '<p class="data-note">当前公开活动快照中暂无外部项目贡献。</p>';
$('#personal-repos').innerHTML = data.repos.filter(repo=>!repo.fork).slice(0,3).map(repo=>`<a class="repo-row" href="${escapeHTML(repo.html_url)}" target="_blank" rel="noreferrer">${escapeHTML(repo.name)}<span><i class="lang-dot"></i>${escapeHTML(repo.language || '—')} ↗</span></a>`).join('');
function renderSignal() {
  const range = Number($('#signal-range').value);
  const days = data.days.slice(-range);
  const max = Math.max(1,...days.map(day=>day.count));
  const sum = days.reduce((total,day)=>total+day.count,0);
  $('#signal-total').textContent = sum;
  $('#signal-period').textContent = `/ LAST ${range} DAYS`;
  $('#signal-start').textContent = days[0].date;
  $('#signal-end').textContent = lastDay;
  const summary = `${days.filter(day=>day.count).length} active days / peak ${max} contributions`;
  $('#signal-readout').textContent = summary;
  $('#signal-bars').replaceChildren(...days.map(day=>{
    const bar = document.createElement('button');
    bar.style.height = `${Math.max(1,day.count/max*92)}%`;
    bar.title = `${day.date} · ${day.count} contributions`;
    bar.setAttribute('aria-label',bar.title);
    const show = () => { $('#signal-readout').textContent = bar.title; };
    bar.addEventListener('mouseenter',show); bar.addEventListener('focus',show); bar.addEventListener('click',show);
    bar.addEventListener('mouseleave',()=>{ $('#signal-readout').textContent=summary; });
    return bar;
  }));
}
$('#signal-range').addEventListener('change',renderSignal); renderSignal();
let filter = 'all', visible = 6;
const types = {prs:['PullRequestEvent'],reviews:['PullRequestReviewEvent','PullRequestReviewCommentEvent'],pushes:['PushEvent']};
function renderActivity() {
  const events = data.events.filter(event=>filter==='all'||types[filter].includes(event.type));
  $('#activity-list').innerHTML = events.slice(0,visible).map(event=>`<a class="event-row" href="${escapeHTML(event.url)}" target="_blank" rel="noreferrer"><time class="event-date" datetime="${escapeHTML(event.date)}">${localDate(event.date)}</time><span class="event-main"><span class="event-icon" aria-hidden="true">${event.type.includes('Review')?'⊙':event.type==='PushEvent'?'↑':'⑂'}</span><span><span class="event-label">${escapeHTML(event.label)}${event.number?' <span class="green">#'+event.number+'</span>':''}</span>${event.title?'<span class="event-title">'+escapeHTML(event.title)+'</span>':''}</span></span><span class="event-repo">${escapeHTML(event.repo)}</span><span class="event-arrow" aria-hidden="true">↗</span></a>`).join('') || '<p class="empty-activity">当前快照中没有该类型的公开活动。</p>';
  $('#event-count').textContent = `${Math.min(visible,events.length)} / ${events.length} EVENTS · 公开活动快照`;
  $('#load-more').hidden = visible >= events.length;
}
document.querySelectorAll('[data-filter]').forEach(button=>button.addEventListener('click',()=>{
  filter=button.dataset.filter; visible=6;
  document.querySelectorAll('[data-filter]').forEach(item=>{item.classList.toggle('selected',item===button);item.setAttribute('aria-pressed',String(item===button));});
  renderActivity();
}));
$('#load-more').addEventListener('click',()=>{visible+=8;renderActivity();}); renderActivity();
document.querySelectorAll('[data-mode]').forEach(button=>button.addEventListener('click',()=>{
  const readme = button.dataset.mode === 'readme';
  $('#terminal-view').hidden=readme; $('#readme-view').hidden=!readme;
  document.querySelectorAll('[data-mode]').forEach(item=>{item.classList.toggle('active',item===button);item.setAttribute('aria-pressed',String(item===button));});
  window.scrollTo({top:0,behavior:'instant'});
}));
$('#readme-projects').innerHTML = data.contributed.map(([repo,count])=>`<tr><td><a href="https://github.com/${escapeHTML(repo)}">${escapeHTML(repo)}</a></td><td>${count}</td></tr>`).join('');
$('#readme-events').innerHTML = data.events.slice(0,8).map(event=>`<tr><td>${event.date.slice(0,10)}</td><td><a href="${escapeHTML(event.url)}">${escapeHTML(event.label)}${event.number?' #'+event.number:''}</a></td><td>${escapeHTML(event.repo)}</td></tr>`).join('');
$('#readme-stamp').textContent = `Public data snapshot: ${data.updated}. Activity is limited to the latest 100 public events; it is not a complete contribution history.`;
// Use historical authored contributions rather than the recent event window.
$('#contributed-projects').innerHTML = data.showcase.projects_html;
$('#personal-repos').innerHTML = data.showcase.featured_html;
$('#projects .data-note').hidden = true;
$('#readme-projects').innerHTML = data.showcase.table_html;
$('#readme-projects').closest('table').querySelector('thead').innerHTML = '<tr><th>Project</th><th>Contribution</th></tr>';
if (!$('.contributor-role')) {
  const badge = '<a class="contributor-role" href="https://github.com/RL-Align/RL-Kernel">RL-Kernel Core Contributor ↗</a>';
  $('.role').insertAdjacentHTML('beforeend',badge);
  $('.readme-body').insertAdjacentHTML('afterbegin',badge);
  $('#readme-projects').closest('table').insertAdjacentHTML('afterend','<h4>Featured Repositories</h4>'+data.showcase.featured_html);
  [...document.querySelectorAll('.readme-body > p')].find(p=>p.textContent.includes('latest 100-event snapshot')).hidden = true;
}
