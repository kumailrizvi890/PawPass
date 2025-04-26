// Simple heart animation with burst lines
document.addEventListener('DOMContentLoaded', function() {
  const canvas = document.getElementById('heart-animation');
  if (!canvas) return;
  
  const ctx = canvas.getContext('2d');
  let width = canvas.width = canvas.offsetWidth;
  let height = canvas.height = canvas.offsetHeight;
  
  let heartSize = Math.min(width, height) * 0.25;
  let centerX = width / 2;
  let centerY = height / 2;
  let hue = 0;
  let beat = 0;
  let beatSpeed = 0.03;
  let lines = [];
  
  // Create initial burst lines
  createBurstLines();
  
  function createBurstLines() {
    lines = [];
    const lineCount = 16;
    
    for (let i = 0; i < lineCount; i++) {
      const angle = (Math.PI * 2 / lineCount) * i;
      const speed = 0.5 + Math.random() * 1.5;
      const length = heartSize * (0.7 + Math.random() * 0.6);
      
      lines.push({
        angle: angle,
        speed: speed,
        length: length,
        originalLength: length,
        x: 0,
        y: 0
      });
    }
  }
  
  function drawHeart(x, y, size, fillColor) {
    ctx.save();
    ctx.beginPath();
    
    // Heart curve
    const topCurveHeight = size * 0.3;
    ctx.moveTo(x, y + size * 0.25);
    ctx.bezierCurveTo(
      x, y, 
      x - size / 2, y, 
      x - size / 2, y + topCurveHeight
    );
    ctx.bezierCurveTo(
      x - size / 2, y + size * 0.65, 
      x, y + size * 0.9, 
      x, y + size
    );
    ctx.bezierCurveTo(
      x, y + size * 0.9, 
      x + size / 2, y + size * 0.65, 
      x + size / 2, y + topCurveHeight
    );
    ctx.bezierCurveTo(
      x + size / 2, y, 
      x, y, 
      x, y + size * 0.25
    );
    
    ctx.fillStyle = fillColor;
    ctx.fill();
    ctx.restore();
  }
  
  function drawBurstLines(heartSize, beat) {
    ctx.save();
    
    lines.forEach(line => {
      const extend = (Math.sin(beat) + 1) / 2; // 0 to 1
      const currentLength = line.originalLength * (0.8 + extend * 0.4);
      
      const startX = centerX;
      const startY = centerY;
      const endX = startX + Math.cos(line.angle) * currentLength;
      const endY = startY + Math.sin(line.angle) * currentLength;
      
      // Draw line with gradient
      const gradient = ctx.createLinearGradient(startX, startY, endX, endY);
      gradient.addColorStop(0, `hsla(${hue}, 100%, 65%, 0.8)`);
      gradient.addColorStop(1, `hsla(${hue}, 100%, 65%, 0)`);
      
      ctx.beginPath();
      ctx.moveTo(startX, startY);
      ctx.lineTo(endX, endY);
      ctx.strokeStyle = gradient;
      ctx.lineWidth = 3 + Math.sin(beat) * 2;
      ctx.stroke();
    });
    
    ctx.restore();
  }
  
  function animate() {
    ctx.clearRect(0, 0, width, height);
    
    // Background with subtle gradient
    const gradient = ctx.createRadialGradient(
      centerX, centerY, 0,
      centerX, centerY, height
    );
    
    // Use the site's color scheme
    const isColorblind = document.body.classList.contains('colorblind-mode');
    
    if (isColorblind) {
      gradient.addColorStop(0, 'rgba(0, 158, 115, 0.1)');
      gradient.addColorStop(1, 'rgba(0, 158, 115, 0.01)');
      hue = 160; // Green-teal hue for colorblind mode
    } else {
      gradient.addColorStop(0, 'rgba(244, 178, 186, 0.2)');
      gradient.addColorStop(1, 'rgba(244, 178, 186, 0.05)');
      hue = 350; // Pink-red hue for regular mode
    }
    
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, width, height);
    
    // Draw burst lines behind heart
    drawBurstLines(heartSize, beat);
    
    // Calculate heart beat effect
    beat += beatSpeed;
    const beatEffect = 1 + Math.sin(beat) * 0.08;
    const currentHeartSize = heartSize * beatEffect;
    
    // Draw heart
    const heartColor = isColorblind 
      ? `hsl(160, 80%, 50%)`
      : `hsl(350, 80%, 60%)`;
    
    drawHeart(
      centerX, 
      centerY - currentHeartSize * 0.5, 
      currentHeartSize,
      heartColor
    );
    
    requestAnimationFrame(animate);
  }
  
  // Handle window resize
  window.addEventListener('resize', function() {
    width = canvas.width = canvas.offsetWidth;
    height = canvas.height = canvas.offsetHeight;
    heartSize = Math.min(width, height) * 0.25;
    centerX = width / 2;
    centerY = height / 2;
    createBurstLines();
  });
  
  // Start animation
  animate();
});