import React, { useState, useEffect } from 'react';
import './App.css';
import axios from 'axios';
import Main from './pages/Main.jsx';
import Header from './components/Header';
import Searchbar from './components/Searchbar';
import Button from './components/Button';
import Logo from './components/Logo.jsx';
import { BrowserRouter } from 'react-router-dom';
import Sources from './components/Sources.jsx';

function App() {
  const mockArticles = Array.from({ length: 20 }, (_, i) => ({
    title: `뉴스 크롤링 프로젝트 테스트 기사 제목입니다 - ${i + 1}`,
    company_name: i % 2 === 0 ? "한국경제" : "매일신문", // 짝수/홀수 번갈아가며 언론사 설정
    url: `https://example.com/article/${i + 1}`
  }));

  return (
    <BrowserRouter>
      <div className="App">
        {/* <Header
          leftChild={<Logo />}
          midChild={<Searchbar maxWidth="400px" />}
          rightChild={<Button text={'로그인'} onClick={() => {
          }} />}
        />
        <Main /> */}
        <Sources articles={mockArticles} />
      </div>
    </BrowserRouter>
  );
}

export default App;
