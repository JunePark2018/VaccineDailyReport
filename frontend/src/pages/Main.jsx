import './Main.css';

function Main() {
  return (
    <div className="Main">
      {/* 1. 왼쪽: 사이드바 (전체 높이) */}
      {/* <Sidebar /> */}

      {/* 2. 오른쪽: 헤더 + 본문 영역을 감싸는 컨테이너 */}
      <div className="page-content">
        
        {/* 우측 상단 */}
        {/* <Header /> */}

        {/* 우측 하단 (나머지 영역) */}
        <main className="main-content">
          {/* 1. 상단: 메인 슬라이드 (캐러셀) */}
          <section className="slide-section">
            {/* <MainSlide /> */}
          </section>

          {/* 2. 하단: 오늘의 소식 리스트 */}
          <section className="news-section">
            <h2 className="section-title">오늘의 소식</h2>
            
            <div className="article-grid">
              {/* 기사 컴포넌트를 여러 개 배치 */}
              {/*
              articles.map((item, index) => (
                <Article key={index} />
              ))
              */}
            </div>
          </section>
        </main>
        
      </div>
    </div>
  );
}

export default Main;