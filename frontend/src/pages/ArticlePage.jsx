import React from 'react';
import { useNavigate } from 'react-router-dom';
import Carousel from '../components/Carousel';
import TodayNews from '../components/TodayNews';
import SlideItem from '../components/SlideItem';
import LeftSideBar from '../components/LeftSideBar';
import Header from '../components/Header';
import Searchbar from '../components/Searchbar';
import Button from '../components/Button';
import Logo from '../components/Logo';
import './ArticlePage.css';


function ArticlePage() {
  const navigate = useNavigate();   


  return (
    <div className="ArticlePage" style={{ display: 'flex'}}>
      {/* 1. 왼쪽: 사이드바 (전체 높이) */}
      <LeftSideBar />

      {/* 2. 오른쪽: 헤더 + 본문 영역을 감싸는 컨테이너 */}
      <div className="page-content" style={{flex: 1, marginLeft: '72px'}}>

        {/* 상단 */}
        <Header
          leftChild={<Logo />}
          midChild={<Searchbar maxWidth="400px" />}
          rightChild={<Button text={'로그인'} color="LightSeaGreen" textColor="white" onClick={() => {
          }} />}
        />

        {/* 하단 */}
        <main className="main-content" style={{ backgroundColor: '#222', minHeight: 'calc(100vh - 64px)' }}>
           <div className="article-layout-container">
              <h2 style={{color: 'white', padding: '20px'}}>의대 증원 타결 기사 상세</h2>

           </div>
        </main>

      </div>
    </div>
  );
}

export default ArticlePage;