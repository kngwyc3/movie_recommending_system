import { ref, onMounted } from 'vue';

export function useStars() {
  const starsContainer = ref(null);
  const numberOfStars = 100;

  const createStars = () => {
    if (!starsContainer.value) return;
    
    starsContainer.value.innerHTML = '';
    
    for (let i = 0; i < numberOfStars; i++) {
      const star = document.createElement('div');
      star.className = 'star';
      star.style.left = Math.random() * 100 + '%';
      star.style.top = Math.random() * 100 + '%';
      star.style.animationDelay = Math.random() * 3 + 's';
      star.style.width = Math.random() * 2 + 1 + 'px';
      star.style.height = star.style.width;
      starsContainer.value.appendChild(star);
    }
  };

  onMounted(() => {
    createStars();
  });

  return {
    starsContainer
  };
}
