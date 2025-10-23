// Init animations and PWA
window.addEventListener('load', ()=>{
  if(window.AOS){ AOS.init({ once: true, duration: 500, easing: 'ease-out' }); }

  if('serviceWorker' in navigator){
    navigator.serviceWorker.register('/static/complaints/service-worker.js').catch(()=>{});
  }

  // Install prompt handling
  let installEvent;
  const btn = document.getElementById('installPwaBtn');
  window.addEventListener('beforeinstallprompt', (e)=>{
    e.preventDefault(); installEvent = e;
    if(btn){ btn.style.display = 'inline-flex'; }
  });
  if(btn){
    btn.addEventListener('click', async ()=>{
      if(installEvent){ installEvent.prompt(); await installEvent.userChoice; installEvent = null; }
    });
  }
});
