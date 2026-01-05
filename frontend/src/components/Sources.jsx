import React, { useState } from 'react';
import './Sources.css';

const Sources = ({ articles = [] }) => {
  const [visibleCount, setVisibleCount] = useState(5);

  const handleLoadMore = () => {
    setVisibleCount((prevCount) => prevCount + 10);
  };

  const handleShowAll = () => {
    setVisibleCount(articles.length);
  };

  if (!articles || articles.length === 0) return null;

  const currentArticles = articles.slice(0, visibleCount);
  const remainingCount = articles.length - visibleCount;

  return (
    <div className="Sources">
      <h1 className="sources-header">
        원본 기사 
        {/* 타이틀 옆에 작게 전체 개수 표시 */}
        <span className="article-count">( {articles.length}개 )</span>
      </h1>
      
      <ul className="sources-list">
        {currentArticles.map(({ title, company_name, url }, index) => (
          <li key={index} className="source-item">
            <span className="company-name">{company_name}</span>
            <span className="separator">-</span>
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

      {remainingCount > 0 && (
        <div className="load-more-container">
          {/* ▼ 10개 더 보기 */}
          <button className="load-more-button" onClick={handleLoadMore}>
            <span className="arrow">▼</span> 10개 더 보기
          </button>
          
          {/* ▼ 전체보기 (개수 표기 제거) */}
          <button className="load-more-button" onClick={handleShowAll}>
            <span className="arrow">▼</span> 전체보기
          </button>
        </div>
      )}
    </div>
  );
};

export default Sources;