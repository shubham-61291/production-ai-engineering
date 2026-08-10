import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';

function createCircularTexture() {
  const size = 64;
  const canvas = document.createElement('canvas');
  canvas.width = size;
  canvas.height = size;
  
  const context = canvas.getContext('2d');
  const centerX = size / 2;
  const centerY = size / 2;
  const radius = size / 2;

  if (context) {
    context.beginPath();
    context.arc(centerX, centerY, radius, 0, 2 * Math.PI, false);
    context.fillStyle = 'rgba(255,255,255,1)';
    context.fill();
  }
  
  const texture = new THREE.CanvasTexture(canvas);
  texture.needsUpdate = true;
  return texture;
}

export default function MagnetarBackground() {
  const canvasRef = useRef(null);

  useEffect(() => {
    let animationFrameId;
    let scene, camera, renderer, controls, particleSystem, fieldLinesGroup;

    const canvas = canvasRef.current;
    if (!canvas) return;

    // 1. Scene
    scene = new THREE.Scene();

    // 2. Camera
    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.z = 5;

    // 3. Renderer
    renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true, alpha: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    // 4. Orbit Controls
    controls = new OrbitControls(camera, renderer.domElement);
    controls.enableZoom = false;
    controls.autoRotate = true;
    controls.autoRotateSpeed = 1.2;

    // 5. Lights
    scene.add(new THREE.AmbientLight(0x404040, 2));
    const pointLight = new THREE.PointLight(0xffffff, 1.5);
    pointLight.position.set(5, 5, 5);
    scene.add(pointLight);

    // 6. Particle Flares (Corona)
    const N = 5000;
    const positions = new Float32Array(N * 3);
    const minShellRadius = 1.0;
    const maxShellRadius = 5.0;

    for (let i = 0; i < N; i++) {
      const i3 = i * 3;
      const radius = Math.random() * (maxShellRadius - minShellRadius) + minShellRadius; 
      const vec = new THREE.Vector3(
        (Math.random() - 0.5) * 2,
        (Math.random() - 0.5) * 2,
        (Math.random() - 0.5) * 2
      ).normalize().multiplyScalar(radius);
      
      positions[i3] = vec.x;
      positions[i3 + 1] = vec.y;
      positions[i3 + 2] = vec.z;
    }
    
    const particleGeometry = new THREE.BufferGeometry();
    particleGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    
    const particleTexture = createCircularTexture();
    const particleMaterial = new THREE.PointsMaterial({
      color: 0xddeeff,
      size: 0.04,
      transparent: true,
      opacity: 0.9,
      depthWrite: false,
      sizeAttenuation: true,
      map: particleTexture,
      alphaTest: 0.5,
    });

    particleSystem = new THREE.Points(particleGeometry, particleMaterial);
    scene.add(particleSystem);

    // Core Star
    const coreRadius = 0.35;
    const coreGeometry = new THREE.SphereGeometry(coreRadius, 32, 32); 
    const coreMaterial = new THREE.MeshStandardMaterial({
      color: 0xffffff,
      emissive: 0xbbbbff,
      emissiveIntensity: 15,
      toneMapped: false
    });
    const coreMesh = new THREE.Mesh(coreGeometry, coreMaterial);
    scene.add(coreMesh);

    // Magnetic Plasma Field Loops
    fieldLinesGroup = new THREE.Group();
    const lineMaterial = new THREE.LineBasicMaterial({
      color: 0x66ddff,
      transparent: true,
      opacity: 0.7,
    });
    
    const lineCount = 45;
    const controlDist = 6.0;

    for (let i = 0; i < lineCount; i++) {
      const startVec = new THREE.Vector3(
        (Math.random() - 0.5) * 2,
        (Math.random() - 0.5) * 2,
        (Math.random() - 0.5) * 2
      ).normalize().multiplyScalar(coreRadius);
      
      const endVec = new THREE.Vector3(
        (Math.random() - 0.5) * 2,
        (Math.random() - 0.5) * 2,
        (Math.random() - 0.5) * 2
      ).normalize().multiplyScalar(coreRadius);

      const control1 = new THREE.Vector3(
        (Math.random() - 0.5) * controlDist, 
        (Math.random() - 0.5) * controlDist,
        (Math.random() - 0.5) * controlDist
      ).add(startVec);
      
      const control2 = new THREE.Vector3(
        (Math.random() - 0.5) * controlDist,
        (Math.random() - 0.5) * controlDist,
        (Math.random() - 0.5) * controlDist
      ).add(endVec);

      const curve = new THREE.CatmullRomCurve3([startVec, control1, control2, endVec]);
      const points = curve.getPoints(50);
      const lineGeometry = new THREE.BufferGeometry().setFromPoints(points);
      
      const line = new THREE.Line(lineGeometry, lineMaterial.clone());
      fieldLinesGroup.add(line);
    }
    scene.add(fieldLinesGroup);

    // Resize listener
    const handleResize = () => {
      const width = window.innerWidth;
      const height = window.innerHeight;
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
      renderer.setSize(width, height);
    };
    
    window.addEventListener('resize', handleResize);

    // Animation Loop
    const animate = () => {
      animationFrameId = requestAnimationFrame(animate);
      controls.update();

      particleSystem.rotation.y += 0.001;
      particleSystem.rotation.x += 0.0003;
      fieldLinesGroup.rotation.y += 0.0015;
      fieldLinesGroup.rotation.x += 0.0005;

      fieldLinesGroup.children.forEach(line => {
        if (line.material) {
          line.material.opacity = (Math.sin(Date.now() * 0.005 + line.id) * 0.3 + 0.4);
        }
      });

      renderer.render(scene, camera);
    };
    animate();

    return () => {
      window.removeEventListener('resize', handleResize);
      cancelAnimationFrame(animationFrameId);
      if (renderer) renderer.dispose();
      if (controls) controls.dispose();
      particleGeometry.dispose();
      particleMaterial.dispose();
      coreGeometry.dispose();
      coreMaterial.dispose();
      lineMaterial.dispose();
      fieldLinesGroup.children.forEach(line => {
        line.geometry.dispose();
        line.material.dispose();
      });
    };

  }, []);

  return (
    <div className="fixed inset-0 pointer-events-none z-0">
      <canvas ref={canvasRef} className="w-full h-full pointer-events-auto" />
    </div>
  );
}
