import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import Sources from '../components/Sources';
import RightSideBar from '../components/RightSideBar';
import NewsText from '../components/NewsText';
import Header from '../components/Header';
import Searchbar from '../components/Searchbar';
import Logo from '../components/Logo';
import UserMenu from '../components/UserMenu';
import './ArticlePage.css';
import axios from 'axios';

function ArticlePage() {

  const { id } = useParams();

  const [article, setArticle] = useState({
    title: "기사를 찾을 수 없습니다.",
    contents: "기사 내용을 찾을 수 없습니다."
  });

  // [수정 1] 사이드바 열림 상태 + '어떤 문장'이 선택되었는지 저장하는 상태 추가
  const [isSidebarOpen, setSidebarOpen] = useState(false);
  const [selectedSentence, setSelectedSentence] = useState(null);

  // [수정 2] 문장 클릭 시 실행될 함수 (NewsText에서 호출됨)
  const handleSentenceClick = (sentence) => {
    console.log("부모(ArticlePage)가 받은 문장:", sentence);
    setSelectedSentence(sentence); // 1. 선택된 문장 저장
    setSidebarOpen(true);          // 2. 사이드바 열기
  };

  // 사이드바 닫기 함수
  const closeSidebar = () => {
    setSidebarOpen(false);
  };

  useEffect(() => {
    const fetchArticle = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/generated-news/${id}`);
        const article = response.data;
        console.log(article);
        setArticle(article);
      } catch (error) {
        console.error('DB 데이터를 불러올 수 없습니다:', error);
      }
    };
    fetchArticle();
  }, [id]); // id가 바뀔 때마다 다시 불러오도록 의존성 배열 추가

  return (
    <div className="ArticlePage">
      <div className="page-content">

        {/* 상단 */}
        <Header
          leftChild={<div />}
          midChild={<Logo />}
          rightChild={
            <div style={{ display: 'flex', alignItems: 'center', gap: '0', justifyContent: 'flex-end', width: 'auto' }}>
              <div style={{ position: 'relative' }}>
                <Searchbar />
              </div>
              <UserMenu />
            </div>
          }
          headerTop="on"
          headerMain="on"
          headerBottom="on"
        />

        {/* 하단 */}
        <main className="main-content">
          <div className='article-section'>
            {/* [수정 3] NewsText에 handleSentenceClick 함수 전달 */}
            <NewsText 
                title={article.title} 
                contents={article.contents} 
                onSentenceClick={handleSentenceClick} 
            />
            <Sources articles={[{ title: "원본 기사 제목", company_name: "언론사명", url: "https://example.com" }]} />
          </div>
          <div className="additional-section">
            추가 섹션
          </div>
          
          {/* [수정 4] RightSideBar에 '선택된 문장' 전달 */}
          <RightSideBar 
            isOpen={isSidebarOpen} 
            onClose={closeSidebar} 
            searchKeyword={selectedSentence} // 사이드바가 검색할 키워드(문장)
          />
        </main>
      </div>
    </div>
  );
}

export default ArticlePage;