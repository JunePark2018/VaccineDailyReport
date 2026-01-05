import React from 'react';
import { useNavigate } from 'react-router-dom';
import Sources from '../components/Sources';
import LeftSideBar from '../components/LeftSideBar';
import RightSideBar from '../components/RightSideBar';
import NewsText from '../components/NewsText';
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
      <div className="page-content" style={{flex: 1}}>

        {/* 상단 */}
        <Header
          leftChild={<Logo />}
          midChild={<Searchbar maxWidth="400px" />}
          rightChild={<Button text={'로그인'} color="LightSeaGreen" textColor="white" onClick={() => {
          }} />}
        />

        {/* 하단 */}
        <main className="main-content">
          <div className='article-section'>
            <NewsText title="TEST 기사 제목" contents="AI가 쓴 TEST 기사 본문입니다."/>
            <Sources articles={[{ title: "원본 기사 제목", company_name: "언론사명", url: "https://example.com" }]}/>
          </div>
          <div className="additional-section">
            워드 포그<br/>
            어쩌구저쩌구<br/>
            123123123<br/>
          </div>
        </main>

        {/* 오른쪽 사이드바 */}
        <RightSideBar isOpen={true} />
      </div>
    </div>
  );
}

export default ArticlePage;