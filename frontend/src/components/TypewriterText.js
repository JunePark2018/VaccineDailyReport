
import React, { useState, useEffect } from 'react';

const TypewriterText = ({ text, delay = 50, infinite = false }) => {
  const [currentText, setCurrentText] = useState('');
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    if (currentIndex < text.length) {
      const timeout = setTimeout(() => {
        setCurrentText(prevText => prevText + text[currentIndex]);
        setCurrentIndex(prevIndex => prevIndex + 1);
      }, delay); // delay 시간마다 한 글자씩 추가

      return () => clearTimeout(timeout); // 컴포넌트 언마운트 시 타이머 정리
    } else if (infinite) { // 무한 반복 옵션
      const resetTimeout = setTimeout(() => {
        setCurrentIndex(0);
        setCurrentText('');
      }, 2000); // 전체 텍스트 출력 후 2초 뒤 리셋

      return () => clearTimeout(resetTimeout);
    }
  }, [currentIndex, delay, infinite, text]);

  return <p>{currentText}</p>;
};

export default TypewriterText;