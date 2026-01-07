import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Sources from '../components/Sources';
import RightSideBar from '../components/RightSideBar';
import NewsText from '../components/NewsText';
import Header from '../components/Header';
import Searchbar from '../components/Searchbar';
import Button from '../components/Button';
import Logo from '../components/Logo';
import './ArticlePage.css';
import loginIcon from '../login_icon/login.png';

function ArticlePage() {

  const navigate = useNavigate();

  const [isLoggedIn, setIsLoggedIn] = useState(false);
  useEffect(() => {
    // 2. 컴포넌트가 로드될 때나 다시 그려질 때 토큰 확인
    const token = localStorage.getItem('token');
    setIsLoggedIn(!!token);
  }, []); // []는 페이지 처음 로드 시 실행

  const [isSidebarOpen, setSidebarOpen] = useState(true);

  // 2. 사이드바를 여는 함수 (문장 클릭 시 실행)
  const openSidebar = () => {
    setSidebarOpen(true);
  };

  // 3. 사이드바를 닫는 함수 (X 버튼 클릭 시 실행)
  // 사용자님이 원하시는 "저절로 닫히게" 하는 마법의 함수입니다.
  const closeSidebar = () => {
    setSidebarOpen(false);
  };

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
    <div className="ArticlePage" style={{ display: 'flex' }}>
      {/* 2. 오른쪽: 헤더 + 본문 영역을 감싸는 컨테이너 */}
      <div className="page-content" style={{ flex: 1 }}>

        {/* 상단 */}
        <Header
          leftChild={<Logo />}
          midChild={<Searchbar />}
          rightChild={RightHeaderIcon}
        />

        {/* 하단 */}
        <main className="main-content">
          <div className='article-section'>
            <NewsText title="TEST 기사 제목" contents="AI가 쓴 TEST 기사 본문입니다." />
            <Sources articles={[{ title: "원본 기사 제목", company_name: "언론사명", url: "https://example.com" }]} />
          </div>
          <div className="additional-section">
            추가 섹션
          </div>
          {/* 오른쪽 사이드바 */}
          <RightSideBar isOpen={isSidebarOpen} onClose={closeSidebar} />
        </main>
      </div>
    </div>
  );
}

export default ArticlePage;
