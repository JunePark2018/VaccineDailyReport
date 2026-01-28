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

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
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

  // [수정 3] 언론사 이름 목록 상태 추가 (비교분석 하이라이팅용)
  const [mediaNames, setMediaNames] = useState([]);

  // [추가] 비교분석 섹션 더보기 상태
  const [isExpanded, setIsExpanded] = useState(false);

  // 좋아요 관련 상태
  const [likeCount, setLikeCount] = useState(0);
  const [isLiked, setIsLiked] = useState(false);

  // [추가] 근거 자료(Evidence) 상태 관리 { [index]: { loading: bool, data: [] } }
  const [evidenceMap, setEvidenceMap] = useState({});

  // [추가] 근거 자료 가져오기 함수
  const fetchEvidence = async (index, text) => {
    // 1. 텍스트에서 언급된 언론사 찾기
    // mediaNames state를 활용
    const targetMedia = mediaNames.filter(name => text.includes(name));

    if (targetMedia.length === 0) {
      // 언급된 언론사가 없으면 스킵 (혹은 전체 검색?) -> 일단 스킵
      setEvidenceMap(prev => ({ ...prev, [index]: { loading: false, data: null, noTarget: true } }));
      return;
    }

    // 2. 로딩 시작
    setEvidenceMap(prev => ({ ...prev, [index]: { loading: true, data: null } }));

    try {
      const response = await axios.post('http://localhost:8000/generated-news/claim-evidence', {
        cluster_id: article.cluster_id,
        claim_text: text,
        target_media: targetMedia
      });

      if (response.data.match_found) {
        setEvidenceMap(prev => ({ ...prev, [index]: { loading: false, data: response.data.evidence } }));
      } else {
        setEvidenceMap(prev => ({ ...prev, [index]: { loading: false, data: null } }));
      }
    } catch (error) {
      console.error("근거 찾기 실패:", error);
      setEvidenceMap(prev => ({ ...prev, [index]: { loading: false, error: true } }));
    }
  };

  // [Effect] 펼쳐졌을 때 자동으로 근거 찾기 시작
  useEffect(() => {
    if (isExpanded && article?.analysis_result?.media_comparison_bullets) {
      article.analysis_result.media_comparison_bullets.forEach((text, idx) => {
        // 아직 데이터가 없고, 로딩중도 아닐 때만 요청
        if (!evidenceMap[idx]) {
          fetchEvidence(idx, text);
        }
      });
    }
  }, [isExpanded, article]);

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

  // [추가] 텍스트에서 언론사 이름을 찾아 하이라이트하는 함수
  const highlightMediaText = (text) => {
    if (!text || mediaNames.length === 0) return text;

    // 언론사 이름들을 이용해 정규식 생성 (긴 이름부터 매칭되도록 정렬)
    const sortedNames = [...mediaNames].sort((a, b) => b.length - a.length);
    const regex = new RegExp(`(${sortedNames.join('|')})`, 'g');

    // split하여 매칭된 부분만 스타일링
    const parts = text.split(regex);

    return parts.map((part, index) => {
      if (mediaNames.includes(part)) {
        return (
          <span key={index} style={{ color: '#d32f2f', fontWeight: 'bold' }}>
            {part}
          </span>
        );
      }
      return part;
    });
  };

  useEffect(() => {
    // [추가] 페이지 진입 시 스크롤 최상단으로 이동
    window.scrollTo(0, 0);

    const fetchInfo = async () => {
      try {
        // AI 생성 기사 가져오기
        const ai_news_response = await axios.get(`${API_BASE_URL}/generated-news/${id}`);
        const article = ai_news_response.data;
        console.log(article);
        setArticle(article);

        // 좋아요 수 설정
        setLikeCount(article.like_count || 0);

        // 사용자의 좋아요 상태 확인 (로그인 시)
        const login_id = localStorage.getItem('login_id');
        if (login_id) {
          try {
            const reactionResponse = await axios.get(
              `${API_BASE_URL}/users/${login_id}/reactions/${id}`
            );
            console.log('좋아요 상태 응답:', reactionResponse.data);
            const userLiked = reactionResponse.data.value === 1;
            console.log('사용자 좋아요 상태:', userLiked);
            setIsLiked(userLiked);
          } catch (err) {
            // 반응 없으면 false
            console.log('좋아요 상태 조회 실패 (반응 없음):', err.message);
            setIsLiked(false);
          }
        } else {
          console.log('로그인 안됨 - 좋아요 상태 false');
        }

        // 키워드 가져오기
        const filteredKeywords = JSON.parse(article.keywords).filter(
          item => item.value > 20
        );
        setKeywords(filteredKeywords);

        // 사용된 기사들 가져와서 랜덤하게 사진 고르기
        const img_url_response = await axios.get(`${API_BASE_URL}/generated-news/clusters/${article.cluster_id}/news`);
        const newsList = img_url_response.data;

        // 언론사 이름 추출 (중복 제거)
        const companies = [...new Set(newsList.map(n => n.company_name).filter(Boolean))];
        setMediaNames(companies);

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



  return (
    <div className={`ArticlePage ${isSidebarOpen ? 'sidebar-open' : ''}`}>
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
          <div className="article-content-wrapper">
            <div className='article-section'>
              <div className='article-img'>
                <img src={imgURL} onLoad={(e) => { if (!e.target.src.includes(logoImg)) e.target.style.objectFit = 'cover'; }} onError={(e) => { e.target.onerror = null; e.target.src = logoImg; e.target.style.objectFit = 'contain'; }} />
              </div>

              <div style={{ padding: '0 20px' }}>
                <h1 className="article-head-title">{article.title}</h1>

                {/* [추가] 생성일자 표시 */}
                {article.created_at && (
                  <div style={{
                    display: 'flex', alignItems: 'center', gap: '10px', marginTop: '12px', marginBottom: '8px', fontSize: '0.9rem', color: '#999', fontWeight: 'normal'
                  }}>
                    <span style={{ padding: '4px 10px', backgroundColor: '#f0f0f0', borderRadius: '4px', fontSize: '0.85rem', color: '#666', fontWeight: '500' }}>
                      AI 생성
                    </span>
                    <span>
                      {new Date(article.created_at).getFullYear()}.
                      {String(new Date(article.created_at).getMonth() + 1).padStart(2, '0')}.
                      {String(new Date(article.created_at).getDate()).padStart(2, '0')}
                    </span>
                  </div>
                )}

                <hr className="article-head-divider" />

                <div className="article-comparer" style={{ marginTop: '10px', marginBottom: '40px', borderTop: 'none' }}>
                  <h3 className="section-title">비교분석</h3>
                  <div className={`comparison-container ${isExpanded ? 'expanded' : 'collapsed'}`}>
                    <ul className="comparison-list">
                      {article?.analysis_result?.media_comparison_bullets?.map((text, idx) => (
                        <li key={idx} className="comparison-item">
                          {highlightMediaText(text.replace(/^- /, ''))}
                          {isExpanded && (
                            <div className="evidence-container" style={{ marginTop: '10px', fontSize: '0.9rem' }}>
                              {evidenceMap[idx]?.loading && <div style={{ color: '#888' }}>🔍 관련 기사에서 근거를 찾는 중...</div>}
                              {evidenceMap[idx]?.data && (
                                <div className="evidence-list" style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '8px' }}>
                                  {evidenceMap[idx].data.map((ev, i) => (
                                    <div key={i} className="evidence-item" style={{ background: '#f1f3f4', padding: '8px 12px', borderRadius: '6px', borderLeft: '4px solid #007bff' }}>
                                      <span style={{ fontWeight: 'bold', marginRight: '6px', color: '#333' }}>[{ev.company}]</span>
                                      <a href={ev.url} target="_blank" rel="noopener noreferrer" style={{ color: '#555', textDecoration: 'none' }}>"{ev.text}"</a>
                                    </div>
                                  ))}
                                </div>
                              )}
                            </div>
                          )}
                        </li>
                      ))}
                    </ul>
                  </div>
                  {article?.analysis_result?.media_comparison_bullets?.length > 0 && (
                    <div className="show-more-button-wrapper">
                      <button className="show-more-button link-style" onClick={() => setIsExpanded(!isExpanded)}>
                        {isExpanded ? '접기' : '펼쳐보기'}
                      </button>
                    </div>
                  )}
                </div>
              </div>

              <NewsText
                contents={article.contents}
                onSentenceClick={handleSentenceClick}
                articleId={id}
                likeCount={likeCount}
                isLiked={isLiked}
                onLikeUpdate={(newCount, newIsLiked) => {
                  setLikeCount(newCount);
                  setIsLiked(newIsLiked);
                }}
              />

              <div className="wordcloud-section" style={{ marginTop: '60px', padding: '20px', backgroundColor: '#f9f9f9', borderRadius: '12px' }}>
                <h3 className="section-title" style={{ textAlign: 'center', marginBottom: '30px' }}>기사 핵심 키워드</h3>
                <div style={{ display: 'flex', justifyContent: 'center', width: '400px', maxWidth: '100%', margin: '0 auto', aspectRatio: '1/1' }}>
                  <WordCloudComponent keywords={keywords} width={400} height={400} />
                </div>
              </div>

              {/* [Restored] Sources Section */}
              <Sources clusterId={article.cluster_id} />
            </div>

            {/* No sidebar inside here */}
          </div>

          <AI_News_Recommendation articleId={id} number_of_article={3} />
        </main>

        <RightSideBar
          isOpen={isSidebarOpen}
          onClose={closeSidebar}
          searchKeyword={selectedSentence}
          clusterId={article.cluster_id}
        />
      </div>
    </div>
  );
}

export default ArticlePage;