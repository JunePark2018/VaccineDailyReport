import React from 'react';
import LikeButton from './LikeButton';
import './NewsText.css';

/**
 * NewsText 컴포넌트
 * props:
 * - title: 기사 제목
 * - contents: 기사 본문 (긴 텍스트)
 * - onSentenceClick: 문장 클릭 시 실행할 부모 함수 [핵심!]
 */
const NewsText = ({ title, contents, onSentenceClick }) => {

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

    // [수정된 부분] alert 대신 부모가 준 함수를 실행합니다.
    if (onSentenceClick) {
      onSentenceClick(cleanSentence);
    }
  };

  // [렌더링 로직] 줄바꿈(\n) -> 마침표(.) 순서로 텍스트 분리
  const formatContent = (text) => {
    if (!text) return null;

    // 1. 줄바꿈(\n)으로 문단 분리
    const lines = text.split('\n');
    return lines.map((line, lineIndex) => {
      if (line.trim() === '') return null;

      // 2. 마침표(.)로 문장 분리
      const sentences = line.split('. ');
      const isLastParagraph = lineIndex === lines.length - 1;

      return (
        <p key={lineIndex} className="news-paragraph">
          {sentences.map((sentence, sentenceIndex) => {
            const s = sentence.trim();
            if (!s) return null;

            const punctRe = /[.!?…]$/;
            const endsWithPunct = punctRe.test(s);

            return (
              <span
                key={sentenceIndex}
                className="clickable-sentence"
                onClick={() => handleSentenceClick(s)}
              >
                {s}{endsWithPunct ? '' : '.'}{' '}
              </span>
            );
          })}
          {isLastParagraph && (
            <span className="news-inline-like">
              <LikeButton initialLiked={false} initialCount={120} />
            </span>
          )}
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