import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import Logo from '../components/Logo';
import Searchbar from '../components/Searchbar';
import loginIcon from '../login_icon/login.png';
import './Issues.css';

const Issues = () => {
  const navigate = useNavigate();
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('token');
    setIsLoggedIn(!!token);
  }, []);

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
    <div className="Issues">
      <Header 
        leftChild={<Logo />}
        midChild={<Searchbar />}
        rightChild={RightHeaderIcon}
        headerTop="on" 
        headerMain="on" 
        headerBottom="on" 
      />
      <main className="Issues-Main">
        {/* Blank page content as requested */}
      </main>
    </div>
  );
};

export default Issues;
