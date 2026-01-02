import CarouselNewsAnalyzer from '../components/CarouselNewsAnalyzer';
import Carousel from '../components/Carousel';
import './Main.css';

function Main() {

  // 슬라이드 데이터 예시
  const slideData = [
    { id: 1, img: "...", title: "의대 증원 이슈", desc: "정부와 의료계..." },
    { id: 2, img: "...", title: "백신 개발", desc: "임상 3상 돌입..." },
    { id: 3, img: "...", title: "환절기 건강", desc: "면역력 강화..." },
  ];

  return (
    <div className="Main">
      {/* 1. 왼쪽: 사이드바 (전체 높이) */}
      {/* <Sidebar /> */}

      {/* 2. 오른쪽: 헤더 + 본문 영역을 감싸는 컨테이너 */}
      <div className="page-content">
        
        {/* 상단 */}
        {/* <Header /> */}

        {/* 하단 */}
        <main className="main-content">
          {/* 상단 배너 영역: 캐러셀 + 비교분석 */}
          <section className="top-banner-section">

            {/* 캐러셀 */}
            <div className="carousel-container">
               <Carousel height="100%">                
                {slideData.map(data => (
                  <div key={data.id} className="my-slide-content">
                    <img src={data.img} alt={data.title} />
                    <div className="caption">
                      <h2>{data.title}</h2>
                      <p>{data.desc}</p>
                    </div>
                    <div className="analysis-container">
                      <CarouselNewsAnalyzer width="100%" height="100%" fontSize="14px" />
                    </div>
                  </div>
                ))}
              </Carousel>
            </div>

          </section>
        </main>
        
      </div>
    </div>
  );
}

export default Main;