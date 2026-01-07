import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Carousel from '../components/Carousel';
import TodayNews from '../components/TodayNews';
import SlideItem from '../components/SlideItem';
import Header from '../components/Header';
import Searchbar from '../components/Searchbar';
import Button from '../components/Button';
import Logo from '../components/Logo';
import './Main.css';
import SubArticle from '../components/SubArticle';
import loginIcon from '../login_icon/login.png';

function Main() {
  const navigate = useNavigate(); 
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  useEffect(() => {
    // 2. 컴포넌트가 로드될 때나 다시 그려질 때 토큰 확인
    const token = localStorage.getItem('token');
    setIsLoggedIn(!!token);
  }, []); // []는 페이지 처음 로드 시 실행
  // 슬라이드 데이터 예시
  const slideData = [
    {
      id: 1,
      image: "https://mod-file.dn.nexoncdn.co.kr/game/a20196202add4dde8dfae7aebd05bfb7/1705021038279_409.png?s=892x500&t=crop&q=100&f=png", // 실제 이미지 URL
      title: "의대 증원 극적 타결 조짐?",
      description: "정부와 의료계 5차 협상... 입장차 좁혀",
      analysis: { /* 분석 데이터 객체 */ }
    },
    {
      id: 2,
      image: "https://mod-file.dn.nexoncdn.co.kr/game/a20196202add4dde8dfae7aebd05bfb7/1705021038279_409.png?s=892x500&t=crop&q=100&f=png",
      title: "국산 1호 AI 신약 탄생 임박",
      description: "임상 3상 성공적 완료... 주가 급등",
      analysis: { /* ... */ }
    },
    // ... 더 많은 슬라이드
  ];

  const RightHeaderIcon = (
    <img 
        src={loginIcon} 
        alt={isLoggedIn ? "마이페이지" : "로그인"} 
        width='35px' 
        onClick={() => navigate(isLoggedIn ? '/mypage' : '/login')} 
        style={{ cursor: 'pointer' }} 
    />
);

  return (
    <div className="Main">
      {/* 1. 왼쪽: 사이드바 (전체 높이) */}

      {/* 2. 오른쪽: 헤더 + 본문 영역을 감싸는 컨테이너 */}
      <div className="page-content">

        {/* 상단 */}
        <Header
          leftChild={<Logo />}
          midChild={<Searchbar />}
          rightChild={RightHeaderIcon}
        />

        {/* 하단 */}
        <main className="main-content">         
          {/* 상단 배너 영역: 캐러셀 + 비교분석 */}
          <section className="top-banner-section">

            {/* 캐러셀 */}
            <div className="carousel-container">
              <Carousel height="100%">
                {/* SlideItem 컴포넌트 반복 렌더링 */}
                {slideData.map(data => (
                  <SlideItem
                    key={data.id}
                    image={data.image}
                    title={data.title}
                    description={data.description}
                    analysisData={data.analysis} // 나중에 데이터 연동 시 사용
                  />
                ))}
              </Carousel>
            </div>
          </section>
            <section className="bottom-news-section">
              {[1, 2, 3].map((item) => (
                <div 
                  key={item} 
                  onClick={() => navigate('/article')} 
                  style={{ cursor: 'pointer' }}
                  className="sub-article-wrapper"
                >
                  <SubArticle 
                    title="의대 증원 극적 타결 조짐" 
                    height="200px" 
                    fontSize="24px" 
                    img_url="https://image.ichannela.com/images/channela/2026/01/02/000002924491/00000292449120260102113532802.webp" 
                  />
                </div>
              ))}
            </section>
        </main>

      </div>
    </div>
  );
}

export default Main;
