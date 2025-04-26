// THREE.js Heart Animation
import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.132.2/build/three.module.js';
import { OrbitControls } from 'https://cdn.jsdelivr.net/npm/three@0.132.2/examples/jsm/controls/OrbitControls.js';
import { GLTFLoader } from 'https://cdn.jsdelivr.net/npm/three@0.132.2/examples/jsm/loaders/GLTFLoader.js';

let scene, camera, renderer, heartModel, controls;
let mixer, clock;

function init() {
  // Get the container element
  const container = document.getElementById('heart-animation-container');
  if (!container) return;

  // Create scene
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0xffffff);

  // Set up camera
  camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 1000);
  camera.position.set(0, 0, 5);

  // Set up renderer
  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setPixelRatio(window.devicePixelRatio);
  renderer.setSize(container.clientWidth, container.clientHeight);
  renderer.outputEncoding = THREE.sRGBEncoding;
  container.appendChild(renderer.domElement);

  // Add soft ambient light
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
  scene.add(ambientLight);

  // Add directional light
  const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
  directionalLight.position.set(1, 1, 1);
  scene.add(directionalLight);

  // Add a soft pink light for effect
  const pinkLight = new THREE.PointLight(0xff6b81, 0.7);
  pinkLight.position.set(2, 2, 2);
  scene.add(pinkLight);

  // Create clock for animations
  clock = new THREE.Clock();

  // Load GLTF model
  const loader = new GLTFLoader();
  loader.load('/static/3d/heart_with_burst_lines.gltf', function(gltf) {
    heartModel = gltf.scene;
    
    // Adjust model position and scale
    heartModel.scale.set(0.5, 0.5, 0.5);
    heartModel.position.set(0, 0, 0);
    
    scene.add(heartModel);
    
    // If the model has animations
    if (gltf.animations && gltf.animations.length) {
      mixer = new THREE.AnimationMixer(heartModel);
      const action = mixer.clipAction(gltf.animations[0]);
      action.play();
    } else {
      // If no animations, we'll create our own
      animateHeart();
    }
    
  }, undefined, function(error) {
    console.error('An error happened while loading the model:', error);
  });

  // Add OrbitControls for better interaction
  controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.05;
  controls.screenSpacePanning = false;
  controls.enableZoom = false;
  controls.autoRotate = true;
  controls.autoRotateSpeed = 1;

  // Handle window resize
  window.addEventListener('resize', onWindowResize, false);

  // Start animation loop
  animate();
}

// Custom animation for heart model if needed
function animateHeart() {
  if (!heartModel) return;
  
  // Simple pulse animation
  const pulseAnimation = () => {
    const scale = 0.5 + Math.sin(Date.now() * 0.002) * 0.05;
    heartModel.scale.set(scale, scale, scale);
    
    // Rotate slightly
    heartModel.rotation.y += 0.01;
    
    requestAnimationFrame(pulseAnimation);
  };
  
  pulseAnimation();
}

// Handle window resize
function onWindowResize() {
  const container = document.getElementById('heart-animation-container');
  if (!container) return;
  
  camera.aspect = container.clientWidth / container.clientHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(container.clientWidth, container.clientHeight);
}

// Animation loop
function animate() {
  requestAnimationFrame(animate);
  
  // Update mixer if it exists
  if (mixer) {
    mixer.update(clock.getDelta());
  }
  
  if (controls) {
    controls.update();
  }
  
  renderer.render(scene, camera);
}

// Initialize when the document is ready
document.addEventListener('DOMContentLoaded', function() {
  // Initialize three.js scene
  init();
  
  // Get the heart container element
  const container = document.getElementById('heart-animation-container');
  
  // Create loading indicator
  if (container) {
    const loadingText = document.createElement('div');
    loadingText.className = 'loading-text';
    loadingText.textContent = 'Loading Heart Animation...';
    container.appendChild(loadingText);
    
    // Remove loading text when model loads
    const checkLoadStatus = setInterval(() => {
      if (heartModel) {
        const loadingElement = container.querySelector('.loading-text');
        if (loadingElement) {
          loadingElement.remove();
        }
        clearInterval(checkLoadStatus);
      }
    }, 500);
  }
});