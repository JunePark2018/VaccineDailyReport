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
import UserMenu from '../components/UserMenu';

function Main() {
  const navigate = useNavigate();

  // 슬라이드 데이터 예시
  const slideData = [
    {
      id: 1,
      image: "https://img.freepik.com/free-photo/downtown-cityscape-night-seoul-south-korea_335224-272.jpg?t=st=1767758567~exp=1767762167~hmac=e4ba534e5c105b48886e453f789bb90395bd99e130b545bd3dda7a37f52f1f55&w=2000", // 실제 이미지 URL
      title: "의대 증원 극적 타결 조짐?",
      description: "정부와 의료계 5차 협상... 입장차 좁혀",
      analysis: { /* 분석 데이터 객체 */ }
    },
    {
      id: 2,
      image: "https://img.freepik.com/free-photo/banghwa-bridge-night-korea_335224-492.jpg?t=st=1767758818~exp=1767762418~hmac=155ead384e649570fd2cf9e64236f7a64ab7cf9a668b785df37138b3229373da&w=2000",
      title: "국산 1호 AI 신약 탄생 임박",
      description: "임상 3상 성공적 완료... 주가 급등",
      analysis: { /* ... */ }
    },
    // ... 더 많은 슬라이드
  ];

  return (
    <div className="Main">
      <div className="page-content">

        {/* 상단 */}
        <Header
          leftChild={<Logo />}
          midChild={<Searchbar fontSize="16px" />}
          rightChild={<UserMenu />}
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
