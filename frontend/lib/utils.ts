export function formatDate(date: string): string {
  return new Date(date).toLocaleDateString('vi-VN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
}

export function getEmotionColor(emotion: string): string {
  const colors: Record<string, string> = {
    'Hạnh phúc': 'text-yellow-600',
    'Yêu thương': 'text-pink-600',
    'Quan tâm': 'text-blue-600',
    'Buồn': 'text-gray-600',
    'Giận dữ': 'text-red-600',
  };
  
  return colors[emotion] || 'text-gray-600';
}

export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength) + '...';
}
