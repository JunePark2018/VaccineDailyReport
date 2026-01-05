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
import NewsText from './components/NewsText.jsx';

function App() {
  const articleData = {
    title: "의대증원으로 '강대강' 충돌... 의료계 비상사태 선포",
    contents: `정부의 의대 정원 확대 방침에 반발하여 의료계가 강력한 투쟁을 예고했습니다.\n
    대한의사협회는 오늘 긴급 회의를 열고 비상대책위원회 체제로 전환하기로 결의했습니다. 이에 따라 현 지도부는 총사퇴하고, 즉각적인 파업 찬반 투표에 돌입할 예정입니다.\n
    정부는 이에 대해 "국민의 생명과 건강을 볼모로 한 집단행동에는 법과 원칙에 따라 엄정하게 대응하겠다"는 입장을 재확인했습니다. 보건복지부는 보건의료 위기 단계를 '경계'로 상향 조정하고 비상진료대책본부를 가동했습니다.\n
    양측의 입장이 팽팽하게 맞서면서 의료 대란 우려가 커지고 있습니다. 시민들은 불안감을 감추지 못하고 있으며, 조속한 대화와 타협을 촉구하고 있습니다.`
  };

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
        {/* <Sources articles={mockArticles} /> */}
        <NewsText 
          title={articleData.title}
          contents={articleData.contents}
        />
      </div>
    </BrowserRouter>
  );
}

export default App;
