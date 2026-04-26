'use client';

import Button from '@/components/common/Button';

export default function AnalyzeButton() {
  const handleAnalyze = () => {
    console.log('Analyzing...');
  };

  return (
    <Button onClick={handleAnalyze}>
      Phân tích cảm xúc
    </Button>
  );
}
