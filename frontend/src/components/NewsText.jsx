import React from 'react';
import './NewsText.css';

/**
 * NewsText 컴포넌트
 * 외부에서 함수를 받지 않고 내부에서 클릭 이벤트를 처리합니다.
 */
const NewsText = ({ title, contents }) => {
  
  // [내부 함수] 문장 클릭 시 실행될 로직
  const handleSentenceClick = (sentence) => {
    // 1. 현재 브라우저에서 선택(드래그)된 텍스트 가져오기
    const selection = window.getSelection();

    // 2. 선택된 텍스트가 있다면? -> 사용자가 드래그 중인 것임 -> 클릭 이벤트 무시
    if (selection.toString().length > 0) {
      return; 
    }

    // 3. 순수 클릭일 때만 아래 로직 실행
    const cleanSentence = sentence.trim();
    console.log("사용자가 선택한 문장:", cleanSentence);
    alert(`선택된 문장: \n${cleanSentence}`);
  };

  // [렌더링 로직] 줄바꿈(\n) -> 마침표(.) 순서로 텍스트 분리
  const formatContent = (text) => {
    if (!text) return null;

    // 1. 줄바꿈(\n)으로 문단 분리
    return text.split('\n').map((line, lineIndex) => {
      if (line.trim() === '') return null; 

      // 2. 마침표(.)로 문장 분리
      const sentences = line.split('.');

      return (
        <p key={lineIndex} className="news-paragraph">
          {sentences.map((sentence, sentenceIndex) => {
            // 빈 문장은 렌더링하지 않음
            if (sentence.trim() === '') return null;

            return (
              <span 
                key={sentenceIndex} 
                className="clickable-sentence"
                onClick={() => handleSentenceClick(sentence)}
              >
                {/* 문장 내용 + 마침표 복구 + 띄어쓰기 */}
                {sentence}.{' '}
              </span>
            );
          })}
        </p>
      );
    });
  };

  return (
    <div className="NewsText">
      <h1 className="news-title">{title}</h1>
      <hr className="news-divider" />
      <div className="news-body">
        {formatContent(contents)}
      </div>
    </div>
  );
};

export default NewsText;