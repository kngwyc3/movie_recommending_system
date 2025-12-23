import { ref, onMounted } from 'vue';

export function useParticles() {
  const particlesContainer = ref(null);
  const numberOfParticles = 20;

  const createParticles = () => {
    if (!particlesContainer.value) return;
    
    particlesContainer.value.innerHTML = '';
    
    for (let i = 0; i < numberOfParticles; i++) {
      const particle = document.createElement('div');
      particle.className = 'particle';
      particle.style.left = Math.random() * 100 + '%';
      particle.style.animationDelay = Math.random() * 15 + 's';
      particle.style.animationDuration = (Math.random() * 10 + 10) + 's';
      
      const colors = ['#00f0ff', '#bf00ff', '#ff006e'];
      particle.style.background = colors[Math.floor(Math.random() * colors.length)];
      
      particlesContainer.value.appendChild(particle);
    }
  };

  onMounted(() => {
    createParticles();
  });

  return {
    particlesContainer
  };
}
