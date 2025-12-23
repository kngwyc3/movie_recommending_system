export const posterMap = {
  '沙丘': 'https://image.tmdb.org/t/p/w500/d5NXSklXo0qyIYkgV94XAgMIckC.jpg',
  'Dune': 'https://image.tmdb.org/t/p/w500/d5NXSklXo0qyIYkgV94XAgMIckC.jpg',
  '星际穿越': 'https://image.tmdb.org/t/p/w500/rAiYTfKGqDCRIIqo664sY9XZIvQ.jpg',
  'Interstellar': 'https://image.tmdb.org/t/p/w500/rAiYTfKGqDCRIIqo664sY9XZIvQ.jpg',
  '盗梦空间': 'https://image.tmdb.org/t/p/w500/9gk7adHYeDvHkCSEqAvQNLV5Uge.jpg',
  'Inception': 'https://image.tmdb.org/t/p/w500/9gk7adHYeDvHkCSEqAvQNLV5Uge.jpg',
  '阿凡达': 'https://image.tmdb.org/t/p/w500/jRXYjXNq0Cs2TcJjLkki24MLp7u.jpg',
  'Avatar': 'https://image.tmdb.org/t/p/w500/jRXYjXNq0Cs2TcJjLkki24MLp7u.jpg'
};

export function resolvePoster(path, title = '', { width = '400', height = '600', buildResourceUrl, getReliableImageUrl }) {
  if (title && posterMap[title]) {
    return posterMap[title];
  }
  const built = buildResourceUrl?.(path);
  if (built) {
    return getReliableImageUrl ? getReliableImageUrl(built, width, height) : built;
  }
  return `https://placehold.co/${width}x${height}/1a1a2e/00f0ff?text=No+Image`;
}

