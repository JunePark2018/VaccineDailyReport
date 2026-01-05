import React, { useState } from 'react';
import RightSideBar from './RightSideBar';



//백엔드 API로부터 받아올 데이터 아래는 샘플
const AI_GENERATED_NEWS = {
  keyword: "인공지능",
  title: "AI가 바꾸는 2026년의 일상",
  paragraphs: [
    {
      id: 1,
      text: "최근 생성형 AI는 단순한 텍스트 생성을 넘어 감정 분석과 복합 추론 단계로 진입했습니다.",
      source: { title: "테크 타임즈 - AI의 진화", url: "https://example.com/1", date: "2026-01-02" }
    },
    {
      id: 2,
      text: "특히 의료 분야에서의 진단 정확도는 전문의의 판단을 보조할 만큼 수준이 높아졌습니다.",
      source: { title: "메디컬 뉴스 - 스마트 의료 시스템", url: "https://example.com/2", date: "2026-01-04" }
    }
  ]
};




export default function RightSideBarParent() {
    const [isSidebarOpen, setIsSidebarOpen] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [selectedSource, setSelectedSource] = useState(null);

    // AI가 생성한 기사 데이터 (실제로는 벡터?값)
    const newsData = AI_GENERATED_NEWS; 

    // 문단 클릭 시 실행
    const handleParagraphClick = (source) => {
        
        //현재 사이드바에 보여줄 출처 데이터 
        setSelectedSource(source);

        //사이드바 열림/닫힘 상태
        setIsSidebarOpen(true);

        //사이드바 내 로딩 애니메이션 표시 여부
        setIsLoading(true);

        // 가짜 비동기 처리
        setTimeout(() => {
            setIsLoading(false);
        }, 600);
    };

    return (
        <div style={{ padding: "50px", maxWidth: "800px", margin: "0 auto", fontFamily: "sans-serif" }}>
            <header style={{ marginBottom: '40px', borderBottom: '1.5px solid #eee', paddingBottom: '20px' }}>
                <h1 style={{ fontSize: '28px', marginTop: '8px' }}>{newsData.title}</h1>
            </header>

            <main>
                {newsData.paragraphs.map((p) => (
                    <p 
                        key={p.id}
                        onClick={() => handleParagraphClick(p.source)}
                        style={paragraphStyle}
                    >
                        {p.text}
                    </p>
                ))}
            </main>

            {/* 사이드바: 참조 출처 정보 표시 */}
            <RightSideBar 
                isOpen={isSidebarOpen}
                isLoading={isLoading}
                source={selectedSource}
                
                // X 버튼 누르면 닫기
                onClose={() => setIsSidebarOpen(false)}
            />
        </div>
    );
}
const paragraphStyle = {
    fontSize: '14px',
    marginBottom: '7px',
    padding: '5px',
    cursor: 'pointer',
};