import React, { useMemo, useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import Sources from '../components/Sources';
import RightSideBar from '../components/RightSideBar';
import NewsText from '../components/NewsText';
import Header from '../components/Header';
import Searchbar from '../components/Searchbar';
import Logo from '../components/Logo';
import logoImg from '../components/Logo.png';
import UserMenu from '../components/UserMenu';
import './ArticlePage.css';
import axios from 'axios';
import WordCloudComponent from '../components/WordCloud';
import AI_News_Recommendation from '../components/AI_News_Recommendation';

function ArticlePage() {

  const { id } = useParams();

  const [article, setArticle] = useState({
    title: "기사를 찾을 수 없습니다.",
    contents: "기사 내용을 찾을 수 없습니다."
  });

  const [keywords, setKeywords] = useState([]);

  const [imgURL, setImgURL] = useState("");

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
    // [추가] 페이지 진입 시 스크롤 최상단으로 이동
    window.scrollTo(0, 0);

    const fetchInfo = async () => {
      try {
        // AI 생성 기사 가져오기
        const ai_news_response = await axios.get(`http://localhost:8000/generated-news/${id}`);
        const article = ai_news_response.data;
        console.log(article);
        setArticle(article);

        // 키워드 가져오기
        const filteredKeywords = JSON.parse(article.keywords).filter(
          item => item.value > 20
        );
        setKeywords(filteredKeywords);

        // 사용된 기사들 가져와서 랜덤하게 사진 고르기
        const img_url_response = await axios.get(`http://localhost:8000/generated-news/clusters/${article.cluster_id}/news`);
        const newsList = img_url_response.data;

        // 1모든 기사에서 img_urls만 모아서 평탄화
        const allImgUrls = newsList
          .flatMap(news => news.img_urls ?? [])
          .filter(Boolean);

        // 이미지가 하나도 없으면 중단
        if (allImgUrls.length === 0) {
          console.warn("이미지 URL이 없습니다");
          return;
        }

        // 랜덤 선택
        const img_number = Math.floor(Math.random() * allImgUrls.length);
        setImgURL(allImgUrls[img_number]);
      } catch (error) {
        console.error('DB 데이터를 불러올 수 없습니다:', error);
      }
    };

    // [추가] 읽음 처리 (로그인 시)
    const login_id = localStorage.getItem('login_id');
    if (login_id) {
      axios.post(`http://localhost:8000/users/${login_id}/read/${id}`)
        .then(() => console.log("Read recorded"))
        .catch(err => console.error("Failed to record read:", err));
    }

    fetchInfo();
  }, [id]); // id가 바뀔 때마다 다시 불러오도록 의존성 배열 추가

  // 워드 클라우드 (재렌더링 방지)
  const wordCloud = useMemo(() => {
    return (
      <WordCloudComponent
        keywords={keywords}
        width={400}
        height={400}
      />
    );
  }, [keywords]);

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

        {/* [추가] 생성일자 표시 */}
        <div style={{ textAlign: 'center', marginTop: '20px', color: '#000000ff', fontSize: '1.5rem', fontWeight: 'bold' }}>
          {article.created_at ? (
            `${new Date(article.created_at).getFullYear()}년 ${new Date(article.created_at).getMonth() + 1}월 ${new Date(article.created_at).getDate()}일에 생성된 AI 뉴스 기사 입니다.`
          ) : null}
        </div>

        {/* 하단 */}
        <main className="main-content">
          <div className="article-content-wrapper">
            <div className='article-section'>
              <div className='article-img'>
                <img src={imgURL} onLoad={(e) => { if (!e.target.src.includes(logoImg)) e.target.style.objectFit = 'cover'; }} onError={(e) => { e.target.onerror = null; e.target.src = logoImg; e.target.style.objectFit = 'contain'; }} />
              </div>
              <NewsText
                title={article.title}
                contents={article.contents}
                onSentenceClick={handleSentenceClick}
              />
              <div className="article-comparer">
                <h3 className="section-title">비교분석</h3>
                <ul className="comparison-list">
                  {article?.analysis_result?.media_comparison_bullets?.map((text, idx) => (
                    <li key={idx} className="comparison-item">{text.replace(/^- /, '')}</li>
                  ))}
                </ul>
              </div>
              <Sources clusterId={article.cluster_id} />
            </div>
            <div className="additional-section">
              <h3 className="section-title">키워드</h3>
              {wordCloud}
            </div>

            {/* [수정 4] RightSideBar에 '선택된 문장' 전달 */}
            <RightSideBar
              isOpen={isSidebarOpen}
              onClose={closeSidebar}
              searchKeyword={selectedSentence} // 사이드바가 검색할 키워드(문장)
              clusterId={article.cluster_id}   // [추가] 리얼 데이터 조회를 위한 clusterId 전달
            />
          </div>

          {/* [추가] AI 뉴스 추천 컴포넌트 */}
          <AI_News_Recommendation articleId={id} number_of_article={3} />
        </main>
      </div>
    </div>
  );
}

export default ArticlePage;