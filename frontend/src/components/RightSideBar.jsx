import React, { useState, useEffect } from 'react';
import './RightSideBar.css';

export default function RightSideBar({ isOpen, onClose, searchKeyword }) {
  const [isLoading, setIsLoading] = useState(false);
  const [sourceList, setSourceList] = useState(null);

  useEffect(() => {
    if (isOpen && searchKeyword) {
      setIsLoading(true);
      setSourceList(null);

      const timer = setTimeout(() => {
        // [수정] 가짜 데이터에 'content' (본문 요약) 필드 추가
        const mockResponse = [
          {
            id: 1,
            company: "테크 타임즈",
            title: "생성형 AI, 2026년에는 감정까지 읽는다",
            // 긴 본문 내용 예시
            content: "최근 개발된 생성형 AI 모델은 텍스트의 맥락뿐만 아니라 작성자의 미묘한 감정 상태까지 파악할 수 있는 단계에 이르렀습니다. 이는 고객 서비스, 심리 상담 등 다양한 분야에서 혁신적인 변화를 가져올 것으로 기대됩니다. 특히 인간의 공감 능력을 모방하는 기술은...",
            date: "2026-01-20",
            url: "https://example.com/news/1"
          },
          {
            id: 2,
            company: "AI 일보",
            title: "의료 AI 진단 정확도 99% 달성... 전문의 보조",
            content: "국내 연구진이 개발한 의료 영상 판독 AI가 전문의 수준을 뛰어넘는 99%의 진단 정확도를 기록했습니다. 이 AI는 엑스레이, MRI 등의 영상을 분석하여 암, 폐렴 등의 질병을 조기에 발견하는 데 큰 도움을 줄 예정입니다. 의료 현장에서의 활용도가 매우 높을 것으로...",
            date: "2026-01-18",
            url: "https://example.com/news/2"
          },
          {
            id: 3,
            company: "퓨처 모빌리티",
            title: "자율주행 레벨5 상용화 임박, 교통사고 제로 도전",
            content: "완전 자율주행을 의미하는 레벨5 기술 상용화가 눈앞으로 다가왔습니다. 주요 자동차 제조사들은 내년 초 레벨5 기능을 탑재한 차량을 출시할 계획이라고 밝혔습니다. 이는 교통체증 해소와 함께 교통사고 발생률을 획기적으로 낮출 수 있는 계기가 될 것입니다. 다만 법적...",
            date: "2026-01-15",
            url: "https://example.com/news/3"
          }
        ];
        
        setSourceList(mockResponse);
        setIsLoading(false);
      }, 800);

      return () => clearTimeout(timer);
    }
  }, [searchKeyword, isOpen]);

  return (
    <aside className={`right-sidebar ${isOpen ? 'open' : ''}`}>
      
      {/* 헤더: 텍스트 부분을 div로 감싸 왼쪽 정렬을 명확히 함 */}
      <div className="sidebar-header">
        <div className="header-text">
            <h3 style={{ margin: 0, fontSize: '18px', fontWeight: 'bold' }}>참조된 원본 기사</h3>
            <p style={{ margin: '5px 0 0', fontSize: '12px', color: '#666'}}>
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