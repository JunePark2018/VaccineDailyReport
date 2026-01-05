import React, { useState } from 'react';
import './Sources.css';

/**
 * Sources 컴포넌트
 * 뉴스 기사 목록을 보여주고, '더 보기' 및 '전체보기' 기능을 제공합니다.
 * @param {Array} articles - { title, company_name, url } 형태의 기사 데이터 리스트
 */
const Sources = ({ articles = [] }) => {
  // [상태 관리] 처음에 보여줄 기사의 개수 (초기값: 5개)
  const [visibleCount, setVisibleCount] = useState(5);

  // [이벤트 핸들러] '10개 더 보기' 버튼 클릭 시 실행
  const handleLoadMore = () => {
    setVisibleCount((prevCount) => prevCount + 10);
  };

  // [이벤트 핸들러] '전체보기' 버튼 클릭 시 실행 (전체 길이로 설정)
  const handleShowAll = () => {
    setVisibleCount(articles.length);
  };

  // 데이터가 없거나 비어있으면 아무것도 렌더링하지 않음 (보호 코드)
  if (!articles || articles.length === 0) return null;

  // [데이터 가공]
  // 1. 현재 보여줄 개수만큼 배열을 자름
  const currentArticles = articles.slice(0, visibleCount);
  // 2. 보여주지 않은 남은 기사 개수 계산
  const remainingCount = articles.length - visibleCount;

  return (
    <div className="Sources">
      {/* --- 상단 타이틀 영역 --- */}
      <h1 className="sources-header">
        원본 기사 
        {/* 타이틀 옆에 전체 기사 개수를 괄호와 함께 표시 */}
        <span className="article-count">( {articles.length}개 )</span>
      </h1>
      
      {/* --- 기사 리스트 영역 --- */}
      <ul className="sources-list">
        {currentArticles.map(({ title, company_name, url }, index) => (
          <li key={index} className="source-item">
            {/* 언론사명 */}
            <span className="company-name">{company_name}</span>
            {/* 구분선 (-) */}
            <span className="separator">-</span>
            {/* 기사 제목 (클릭 시 새 창으로 이동) */}
            <a 
              href={url} 
              target="_blank" 
              rel="noopener noreferrer" 
              className="article-link"
            >
              {title}
            </a>
          </li>
        ))}
      </ul>

      {/* --- 하단 버튼 영역 (남은 기사가 있을 때만 표시) --- */}
      {remainingCount > 0 && (
        <div className="load-more-container">
          {/* 버튼 1: 10개씩 더 불러오기 */}
          <button className="load-more-button" onClick={handleLoadMore}>
            <span className="arrow">▼</span> 10개 더 보기
          </button>
          
          {/* 버튼 2: 한 번에 모두 펼치기 */}
          <button className="load-more-button" onClick={handleShowAll}>
            <span className="arrow">▼</span> 전체보기
          </button>
        </div>
      )}
    </div>
  );
};

export default Sources;