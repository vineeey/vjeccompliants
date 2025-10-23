// Lightweight Three.js hero animation
(function(){
  const canvas = document.getElementById('hero3d');
  if(!canvas || !window.THREE){ return; }
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(55, canvas.clientWidth / canvas.clientHeight, 0.1, 100);
  camera.position.z = 6;

  const resize = ()=>{
    const w = canvas.clientWidth || canvas.parentElement.clientWidth;
    const h = canvas.clientHeight || 360;
    renderer.setSize(w, h, false);
    camera.aspect = w / h; camera.updateProjectionMatrix();
  };
  resize();
  window.addEventListener('resize', resize);

  // Create floating cards
  const group = new THREE.Group(); scene.add(group);
  const geo = new THREE.BoxGeometry(1.2, 0.8, 0.08);
  const mats = [0x4f46e5, 0x14b8a6, 0x64748b, 0xf59e0b].map(c => new THREE.MeshStandardMaterial({ color: c, roughness: 0.6, metalness: 0.15 }));
  for(let i=0;i<6;i++){
    const mesh = new THREE.Mesh(geo, mats[i % mats.length]);
    mesh.position.set((Math.random()-0.5)*4, (Math.random()-0.5)*2, (Math.random()-0.5)*2);
    mesh.rotation.set(Math.random()*0.5, Math.random()*0.5, Math.random()*0.5);
    mesh.castShadow = false; mesh.receiveShadow = false;
    group.add(mesh);
  }

  const light = new THREE.DirectionalLight(0xffffff, 0.8); light.position.set(2,2,3); scene.add(light);
  scene.add(new THREE.AmbientLight(0xffffff, 0.6));

  let t = 0;
  function animate(){
    requestAnimationFrame(animate);
    t += 0.01;
    group.children.forEach((m, idx)=>{
      m.position.y += Math.sin(t + idx) * 0.0015;
      m.rotation.x += 0.002; m.rotation.y += 0.003;
    });
    renderer.render(scene, camera);
  }
  animate();
})();
