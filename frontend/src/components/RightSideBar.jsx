import React, { useState, useEffect } from 'react';
import './RightSideBar.css';

import axios from 'axios'; // axios 임포트 확인

export default function RightSideBar({ isOpen, onClose, searchKeyword, clusterId }) {
  const [isLoading, setIsLoading] = useState(false);
  const [sourceList, setSourceList] = useState(null);

  useEffect(() => {
    // 사이드바가 열려있고, clusterId가 있을 때만 데이터 로드
    if (isOpen && clusterId) {
      const fetchArticles = async () => {
        setIsLoading(true);
        setSourceList(null);

        try {
          console.log(`[RightSideBar] Fetching news for cluster: ${clusterId}`);
          const response = await axios.get(`http://localhost:8000/generated-news/clusters/${clusterId}/news`);

          // API 응답 매핑: Sources.jsx의 구조와 RightSideBar가 기대하는 구조를 맞춤
          // API: { company_name, title, contents, created_at, url, ... }
          // Sidebar UI: { company, title, content, date, url ... }
          const mappedData = response.data.map(item => ({
            id: item.id,
            company: item.company_name,
            title: item.title,
            content: item.contents, // 본문
            date: item.created_at ? item.created_at.substring(0, 10) : "", // 날짜 포맷팅 단순화
            url: item.url
          }));

          setSourceList(mappedData);

        } catch (error) {
          console.error("Failed to fetch sidebar articles:", error);
          setSourceList([]); // 에러 시 빈 배열
        } finally {
          setIsLoading(false);
        }
      };

      fetchArticles();
    }
  }, [isOpen, clusterId]); // searchKeyword는 데이터 로딩 조건에서 제외 (필요 시 필터링에 사용 가능)

  return (
    <aside className={`right-sidebar ${isOpen ? 'open' : ''}`}>

      {/* 헤더: 텍스트 부분을 div로 감싸 왼쪽 정렬을 명확히 함 */}
      <div className="sidebar-header">
        <div className="header-text">
          <h3 style={{ margin: 0, fontSize: '18px', fontWeight: 'bold' }}>참조된 원본 기사</h3>
          <p style={{ margin: '5px 0 0', fontSize: '12px', color: '#666' }}>
            선택한 문장은 아래 기사들을 바탕으로 생성되었습니다.
          </p>
        </div>
        <button onClick={onClose} className="close-btn" title="닫기">✕</button>
      </div>

      <div className="sidebar-content">
        {isLoading && (
          <div className="loading-container">
            <div className="loader"></div>
            <p>관련 기사를 분석하고 있습니다...</p>
          </div>
        )}

        {!isLoading && sourceList && (
          <div className="fade-in">
            <div className="selected-sentence-box">
              <span className="label">선택된 문장</span>
              <p>"{searchKeyword}"</p>
            </div>

            <div className="article-list">
              {sourceList.map((article) => (
                <a
                  key={article.id}
                  href={article.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="article-card"
                >
                  <div className="card-header">
                    <span className="company-badge">{article.company}</span>
                    <span className="article-date">{article.date}</span>
                  </div>
                  <h4 className="article-title">{article.title}</h4>

                  {/* [추가] 본문 내용 표시 (CSS로 말줄임표 처리됨) */}
                  <p className="article-summary">{article.content}</p>

                  <div className="card-footer">
                    원문 보러가기 &rarr;
                  </div>
                </a>
              ))}
            </div>
          </div>
        )}

        {!isLoading && !sourceList && (
          <div className="empty-state">
            <p>왼쪽 본문에서 문장을 클릭해주세요.</p>
          </div>
        )}
      </div>
    </aside>
  );
}