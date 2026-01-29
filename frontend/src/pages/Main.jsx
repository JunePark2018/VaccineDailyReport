import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import Logo from '../components/Logo';
import logoImg from '../components/Logo.png';
import Searchbar from '../components/Searchbar';
import UserMenu from '../components/UserMenu';


import './Main.css';

import axios from 'axios'; // axios imported

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
export const Main = () => {
  const { name } = useParams();
  const navigate = useNavigate();
  const [currentPage, setCurrentPage] = useState(1);
  const [displayArticles, setDisplayArticles] = useState([]);
  const [imageMap, setImageMap] = useState({});
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userName, setUserName] = useState('');
  const itemsPerPage = 5;

  // Check login status
  useEffect(() => {
    const loggedIn = localStorage.getItem('isLoggedIn') === 'true';
    const storedUserName = localStorage.getItem('user_real_name');

    setIsLoggedIn(loggedIn);
    if (storedUserName) {
      setUserName(storedUserName);
    }
  }, []);

  useEffect(() => {
    setCurrentPage(1);

    const loadData = async () => {
      try {
        // 1. Fetch AI Generated News (Limit 50 for main page coverage)
        const response = await axios.get(`${API_BASE_URL}/generated-news?limit=100`); // Fetch enough to cover all sections
        const realArticles = response.data;

        // 2. Map Backend Data to Frontend Structure
        const formattedArticles = realArticles.map(art => ({
          ...art,
          id: art.ai_generated_news_id, // [Fix] Map native ID to 'id' for widespread usage
          category: art.category_name, // Map category_name ('정치', '경제'...) to category
          image: `cluster_${art.cluster_id}`, // Placeholder ID for image map
          short_text: art.contents ? (art.contents.substring(0, 100) + "...") : "내용 없음"
        }));

        // 3. Filter by category (if name param exists)
        const decodedName = decodeURIComponent(name || '');
        let filtered = (decodedName === '전체메뉴' || !decodedName)
          ? formattedArticles
          : formattedArticles.filter(a => {
            if (!a.category) return false;
            return a.category === decodedName;
          });

        // [추가] 구독 키워드 우선 정렬 (로그인 시)
        const loginId = localStorage.getItem('login_id');
        if (loginId) {
          try {
            const userRes = await axios.get(`${API_BASE_URL}/users/${loginId}/dashboard`);
            const subKeywords = userRes.data.subscribed_keywords || [];

            if (subKeywords.length > 0) {
              // 겹치는 키워드가 있는지 확인하는 함수
              const hasKeyword = (article) => {
                if (!article.keywords) return false;
                // article.keywords가 JSON string일 수도 있고 list일 수도 있음 (backend settings)
                // schema상 List[str]로 올 것으로 예상되나, DB에 문자열로 저장된 경우 파싱 필요할 수 있음
                let kws = article.keywords;
                if (typeof kws === 'string') {
                  try { kws = JSON.parse(kws); } catch (e) { kws = []; }
                }
                if (!Array.isArray(kws)) return false;

                // 단순 포함 여부 체크 (부분 일치 등 더 복잡하게 할 수도 있음)
                return subKeywords.some(sk => kws.some(ak => ak.includes(sk) || sk.includes(ak)));
              };

              // 정렬: 키워드 있는 것이 먼저
              filtered.sort((a, b) => {
                const aHas = hasKeyword(a);
                const bHas = hasKeyword(b);
                if (aHas && !bHas) return -1;
                if (!aHas && bHas) return 1;
                return 0; // 원래 순서 유지 (최신순)
              });
            }
          } catch (e) {
            console.warn("구독 키워드 로딩 실패", e);
          }
        }

        setDisplayArticles(filtered);

        // 4. Fetch Images and Detail News for each article
        const newImageMap = {};
        const newDetailsMap = {};

        // Use Promise.allSettled to fetch images/details in parallel
        await Promise.allSettled(filtered.map(async (art) => {
          try {
            const imgRes = await axios.get(`${API_BASE_URL}/generated-news/clusters/${art.cluster_id}/news`);
            const newsList = imgRes.data;

            // Store detailed news list for highlights
            newDetailsMap[`cluster_${art.cluster_id}`] = newsList;

            // Extract all img_urls and pick one
            const allImgUrls = newsList
              .flatMap(news => news.img_urls ?? [])
              .filter(Boolean);

            if (allImgUrls.length > 0) {
              const randomImg = allImgUrls[Math.floor(Math.random() * allImgUrls.length)];
              newImageMap[`cluster_${art.cluster_id}`] = randomImg;
            }
          } catch (err) {
            console.warn(`Failed to fetch image/details for cluster ${art.cluster_id}`, err);
          }
        }));

        setImageMap(prev => ({ ...prev, ...newImageMap }));
        setArticleDetailsMap(prev => ({ ...prev, ...newDetailsMap }));

      } catch (error) {
        console.error('Failed to load real data:', error);
        setDisplayArticles([]);
        setImageMap({});
      }
    };

    loadData();
  }, [name]);



  // Slideshow State
  const [currentSlideIndex, setCurrentSlideIndex] = useState(0);
  const [articleDetailsMap, setArticleDetailsMap] = useState({});
  const [touchStart, setTouchStart] = useState(0);

  const handleTouchStart = (e) => {
    setTouchStart(e.targetTouches[0].clientX);
  };

  const handleTouchEnd = (e) => {
    const touchEnd = e.changedTouches[0].clientX;
    const distance = touchStart - touchEnd;

    // Swipe threshold (e.g., 50px)
    if (distance > 50) {
      // Swipe Left -> Next
      setCurrentSlideIndex(prev => (prev + 1) % 3);
    } else if (distance < -50) {
      // Swipe Right -> Prev
      setCurrentSlideIndex(prev => (prev - 1 + 3) % 3);
    }
  };

  // Auto-rotate slideshow
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentSlideIndex(prev => (prev + 1) % 3);
    }, 10000); // 10 seconds per slide
    return () => clearInterval(interval);
  }, []);

  // Function to render the main content block (Slideshow)
  const renderMainContent = () => {
    if (!displayArticles || displayArticles.length === 0) return null;

    // Pick top 3 articles for the slideshow list
    const slideArticles = displayArticles.slice(0, 3);
    if (slideArticles.length === 0) return null;

    const activeArticle = slideArticles[currentSlideIndex];
    const activeImage = activeArticle ? (imageMap[activeArticle.image] || activeArticle.image) : null;
    const relatedNews = articleDetailsMap[activeArticle?.image] || [];

    // Parse 'media_comparison_bullets' for highlights
    // Format expected: "- [PressName] Content" or "[PressName] Content"
    const bullets = activeArticle?.analysis_result?.media_comparison_bullets || [];

    let highlights = [];
    if (bullets.length > 0) {
      highlights = bullets.slice(0, 4).map(text => {
        // Remove leading "- " if present
        const cleanText = text.replace(/^- /, '');
        // Regex strategies to find Press Name
        // 1. [PressName] Content
        let match = cleanText.match(/^\[(.*?)\]\s*(.*)/);
        if (!match) {
          // 2. PressName: Content
          match = cleanText.match(/^([^:]+):\s*(.*)/);
        }
        if (!match) {
          // 3. PressName - Content
          match = cleanText.match(/^([^-]+)\s-\s*(.*)/);
        }

        if (match) {
          let kw = match[1].trim();
          // Remove '은' or '는' from the end of the keyword if present
          kw = kw.replace(/(은|는)$/, '');
          return { keyword: `"${kw}"`, content: match[2].trim() };
        } else {
          // Fallback: Use first word as keyword if reasonable length
          const firstSpace = cleanText.indexOf(' ');
          if (firstSpace > 0 && firstSpace < 15) {
            let kw = cleanText.substring(0, firstSpace);
            // Remove '은' or '는' from range
            kw = kw.replace(/(은|는)$/, '');
            return {
              keyword: `"${kw}"`,
              content: cleanText.substring(firstSpace + 1)
            };
          }
          return { keyword: '분석', content: cleanText };
        }
      });
    }

    // If no bullets, fall back to relatedNews
    if (highlights.length === 0 && relatedNews.length > 0) {
      highlights = relatedNews.slice(0, 4).map(news => ({
        keyword: news.company_name || '언론사',
        content: news.contents ? (news.contents.substring(0, 80) + '...') : '내용 없음'
      }));
    }

    console.log(activeArticle);

    return (
      <React.Fragment>
        <section className="main-article-section" style={{ display: 'flex', gap: '40px', marginBottom: '30px' }}>

          {/* Left: List of 4 Articles */}
          <div className="article-info-side" style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
            {slideArticles.map((art, idx) => {
              const isActive = idx === currentSlideIndex;
              return (
                <React.Fragment key={art.id || idx}>
                  <div
                    className={`analysis-block ${isActive ? 'active' : ''}`}
                    onClick={() => setCurrentSlideIndex(idx)}
                    style={{ cursor: 'pointer' }}
                  >
                    <h2 style={{ fontSize: '18px', marginBottom: '5px' }}>
                      {art.title}
                    </h2>
                    <p style={{ fontSize: '12px', lineHeight: '1.4' }}>
                      {art.short_text || "AI 생성 기사 내용"}
                    </p>
                  </div>
                </React.Fragment>
              );
            })}
          </div>

          {/* Center Column (Image) - Synced with Active Item */}
          <div className="main-image-column" style={{ flex: 1.6, display: 'flex', flexDirection: 'column', position: 'relative' }}>
            <div
              className="article-image-center"
              onClick={() => activeArticle && navigate(`/article/${activeArticle.ai_generated_news_id}`)}
              onTouchStart={handleTouchStart}
              onTouchEnd={handleTouchEnd}
              style={{ cursor: 'pointer', width: '100%', aspectRatio: '1.5/1' }}
            >
              <img src={activeImage} alt="Main" onLoad={(e) => { if (!e.target.src.includes(logoImg)) e.target.style.objectFit = 'cover'; }} onError={(e) => { e.target.onerror = null; e.target.src = logoImg; e.target.style.objectFit = 'contain'; }} />

              {/* Mobile Carousel Arrows */}
              <button
                className="carousel-arrow prev-arrow"
                onClick={(e) => { e.stopPropagation(); setCurrentSlideIndex(prev => (prev - 1 + 3) % 3); }}
              >
                &#10094;
              </button>
              <button
                className="carousel-arrow next-arrow"
                onClick={(e) => { e.stopPropagation(); setCurrentSlideIndex(prev => (prev + 1) % 3); }}
              >
                &#10095;
              </button>

              <div className="main-image-text">
                {/* Title Overlay matches Active Item */}
                <h3>{activeArticle?.title}</h3>
                <p className="mobile-carousel-desc">{activeArticle?.short_text}</p>
              </div>
            </div>

            {/* Mobile Carousel Dots */}
            <div className="carousel-dots-mobile">
              {[0, 1, 2].map(dotIdx => (
                <span
                  key={dotIdx}
                  className={`carousel-dot ${dotIdx === currentSlideIndex ? 'active' : ''}`}
                  onClick={() => setCurrentSlideIndex(dotIdx)}
                />
              ))}
            </div>

            {/* Mobile-Only Highlights Section (Directly below dots) */}
            <div className="carousel-highlights-mobile">
              {highlights.slice(0, 2).map((item, midx) => (
                <div key={midx} className="highlight-item-mobile">
                  <span className="hl-keyword">{item.keyword}</span>
                  <span className="hl-content">{item.content}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Right: Highlights (Real Analysis Data) */}
          <div className="highlights-side" style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
            <div className="highlight-list" style={{ display: 'flex', flexDirection: 'column', height: '100%', justifyContent: 'space-between' }}>
              {highlights.map((item, hIndex) => (
                <React.Fragment key={hIndex}>
                  <div className="highlight-item" style={{ alignItems: 'flex-start', textAlign: 'left' }}>
                    <span className="highlight-keyword" style={{ color: '#ff4d4d', fontWeight: 'bold', fontSize: '16px', marginBottom: '5px' }}>{item.keyword}</span>
                    <span className="highlight-content" style={{ fontSize: '13px', lineHeight: '1.5', color: '#444', display: '-webkit-box', overflow: 'hidden', WebkitBoxOrient: 'vertical', WebkitLineClamp: 2 }}>{item.content}</span>
                  </div>
                </React.Fragment>
              ))}
            </div>
          </div>

        </section>
      </React.Fragment>
    );
  };

  const renderAIRecommendedNews = (mainBaseIndex) => {
    if (!displayArticles || displayArticles.length === 0) return null;

    const offset = 7;
    const aiBaseIndex = (mainBaseIndex + offset) % displayArticles.length;

    const aiMainArticle = displayArticles[aiBaseIndex];
    const aiRelatedArticles = [
      displayArticles[(aiBaseIndex + 1) % displayArticles.length],
      displayArticles[(aiBaseIndex + 2) % displayArticles.length]
    ];

    const mainImage = aiMainArticle ? (imageMap[aiMainArticle.image] || aiMainArticle.image) : null;

    return (
      <section className="ai-recommended-section">
        <div className="ai-content-wrapper">
          <div className="ai-layout-split">
            <div className="ai-related-list">
              <h3 style={{ borderLeft: 'none', paddingLeft: '0' }}>AI 추천 뉴스</h3>
              {aiRelatedArticles.map((art, i) => (
                <div key={i} className="ai-related-item-wrapper">
                  <div className="ai-related-item" onClick={() => navigate(`/article/${art.id}`)} style={{ cursor: 'pointer' }}>
                    <h4>{art?.title || "Title Text Sample"}</h4>
                    <p>{art?.short_text || "TEXT SAMPLE content description..."}</p>
                  </div>
                  {i < aiRelatedArticles.length - 1 && <div className="ai-divider"></div>}
                </div>
              ))}
            </div>
            <div className="ai-main-image-container">
              <img src={mainImage} alt="AI Main" onLoad={(e) => { if (!e.target.src.includes(logoImg)) e.target.style.objectFit = 'cover'; }} onError={(e) => { e.target.onerror = null; e.target.src = logoImg; e.target.style.objectFit = 'contain'; }} />
            </div>
          </div>
        </div>
      </section>
    );
  };

  const renderTop10News = () => {
    if (!displayArticles || displayArticles.length === 0) return null;

    const top5Articles = displayArticles.slice(0, 5);

    return (
      <div className="top10-section" style={{ height: 'auto', padding: '37px 0 0 0', border: 'none', background: 'transparent' }}>

        <div className="top10-grid" style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '20px' }}>
          {top5Articles.map((article, index) => {
            const imgPath = imageMap[article.image] || article.image;
            return (
              <div key={index} className="top10-item" onClick={() => navigate(`/article/${article.id}`)} style={{ display: 'flex', flexDirection: 'row', gap: '20px', cursor: 'pointer', alignItems: 'center' }}>
                <span className="top10-rank" style={{ fontSize: '36px', fontWeight: '900', fontStyle: 'italic', color: index < 3 ? '#cc0000' : '#333', lineHeight: '1', minWidth: '30px' }}>
                  {index + 1}
                </span>
                <div style={{ width: '180px', height: '100px', borderRadius: '1px', overflow: 'hidden', flex: 'none' }}>
                  <img src={imgPath} alt={article.title} style={{ width: '100%', height: '100%', objectFit: 'cover' }} onLoad={(e) => { if (!e.target.src.includes(logoImg)) e.target.style.objectFit = 'cover'; }} onError={(e) => { e.target.onerror = null; e.target.src = logoImg; e.target.style.objectFit = 'contain'; }} />
                </div>
                <div style={{ width: '100%' }}>
                  <h4 className="top10-title" style={{ fontSize: '18px', margin: 0, lineHeight: '1.4', wordBreak: 'keep-all' }}>
                    {article.title}
                  </h4>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  const renderPoliticsEconomy = (isSidebar = false, hideBorder = false) => {
    if (!displayArticles || displayArticles.length === 0) return null;
    const getCatArticles = (cat) => displayArticles.filter(a => a.category === cat || (Array.isArray(a.category) && a.category.includes(cat)));
    const politics = getCatArticles('정치').slice(0, 3);
    const economy = getCatArticles('경제').slice(0, 3);

    const renderBox = (title, articles, link) => (
      <div className="cat-box-column">
        <h2 className="cat-box-header" onClick={() => navigate(link)} style={{ cursor: 'pointer' }}>{title}</h2>
        {articles.length > 0 && (
          <div className="cat-box-content">
            <div className="cat-box-main">
              <div className="cat-box-img" onClick={() => navigate(`/article/${articles[0].id}`)} style={{ cursor: 'pointer', aspectRatio: '16/9' }}>
                <img src={imageMap[articles[0].image] || articles[0].image} alt={articles[0].title} style={{ width: '100%', height: '100%', objectFit: 'cover' }} onLoad={(e) => { if (!e.target.src.includes(logoImg)) e.target.style.objectFit = 'cover'; }} onError={(e) => { e.target.onerror = null; e.target.src = logoImg; e.target.style.objectFit = 'contain'; }} />
              </div>
              <div className="cat-box-info">
                {/* Wrapped Title and Desc in a group for isolated hover */}
                <div className="cat-box-text-group" onClick={() => navigate(`/article/${articles[0].id}`)} style={{ cursor: 'pointer' }}>
                  <h3 className="cat-box-title">{articles[0].title}</h3>
                  <p className="cat-box-desc">{articles[0].short_text}</p>
                </div>

                {articles.length > 1 && (
                  <div className="cat-box-list">
                    {articles.slice(1).map((art, i) => (
                      <div key={i} className="cat-box-list-item" onClick={(e) => { e.stopPropagation(); navigate(`/article/${art.id}`); }} style={{ cursor: 'pointer' }}>
                        <h3>"{art.title}"</h3>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    );

    return (
      <section className="category-detailed-section" style={{ marginTop: 0, borderTop: (isSidebar || hideBorder) ? 'none' : '1px solid #eee' }}>
        <div className="cat-split-row" style={{ flexDirection: isSidebar ? 'column' : 'row', gap: '90px' }}>
          {renderBox('정치', politics, '/politics')}
          {renderBox('경제', economy, '/economics')}
        </div>
      </section>
    );
  };

  const renderSocietySection = () => {
    if (!displayArticles || displayArticles.length === 0) return null;
    const society = displayArticles.filter(a => a.category === '사회' || (Array.isArray(a.category) && a.category.includes('사회'))).slice(0, 3);
    return (
      <section className="category-detailed-section" style={{ borderTop: 'none', marginTop: '25px' }}>
        <div className="cat-global-row">
          <h2 className="cat-box-header" onClick={() => navigate('/society')} style={{ cursor: 'pointer', borderLeft: '5px solid #000', paddingLeft: '10px', paddingBottom: '2px', lineHeight: '1' }}>사회</h2>
          <div className="global-grid society-mobile-grid" style={{ gridTemplateColumns: 'repeat(3, 1fr)' }}>
            {society.map((art, i) => (
              <div key={i} className="global-card" onClick={() => navigate(`/article/${art.id}`)} style={{ cursor: 'pointer' }}>
                <div className="global-img">
                  <img src={imageMap[art.image] || art.image} alt={art.title} onLoad={(e) => { if (!e.target.src.includes(logoImg)) e.target.style.objectFit = 'cover'; }} onError={(e) => { e.target.onerror = null; e.target.src = logoImg; e.target.style.objectFit = 'contain'; }} />
                </div>
                <h4 style={{ fontSize: '16px' }}>{art.title}</h4>
              </div>
            ))}
          </div>
        </div>
      </section>
    );
  };

  const renderLivingCultureSection = () => {
    if (!displayArticles || displayArticles.length === 0) return null;
    const culture = displayArticles.filter(a => a.category === '생활/문화' || (Array.isArray(a.category) && a.category.includes('생활/문화'))).slice(0, 2);
    return (
      <section className="category-detailed-section" style={{ borderTop: 'none' }}>
        <div className="cat-global-row">
          <h2 className="cat-box-header" onClick={() => navigate('/culture')} style={{ cursor: 'pointer', borderLeft: '5px solid #000', paddingLeft: '10px', paddingBottom: '2px', lineHeight: '1' }}>생활/문화</h2>
          <div className="global-grid" style={{ gridTemplateColumns: 'repeat(2, 1fr)' }}>
            {culture.map((art, i) => (
              <div key={i} className="global-card" onClick={() => navigate(`/article/${art.id}`)} style={{ cursor: 'pointer' }}>
                <div className="global-img">
                  <img src={imageMap[art.image] || art.image} alt={art.title} onLoad={(e) => { if (!e.target.src.includes(logoImg)) e.target.style.objectFit = 'cover'; }} onError={(e) => { e.target.onerror = null; e.target.src = logoImg; e.target.style.objectFit = 'contain'; }} />
                </div>
                <h4 style={{ fontSize: '16px' }}>{art.title}</h4>
              </div>
            ))}
          </div>
        </div>
      </section>
    );
  };

  const renderScienceSection = () => {
    if (!displayArticles || displayArticles.length === 0) return null;
    const science = displayArticles.filter(a => a.category === 'IT/과학' || (Array.isArray(a.category) && a.category.includes('IT/과학'))).slice(0, 1);
    return (
      <section className="category-detailed-section" style={{ borderTop: 'none' }}>
        <div className="cat-global-row">
          <h2 className="cat-box-header" onClick={() => navigate('/science')} style={{ cursor: 'pointer' }}>IT/과학</h2>
          <div className="global-grid" style={{ gridTemplateColumns: '1fr' }}>
            {science.map((art, i) => (
              <div key={i} className="global-card" onClick={() => navigate(`/article/${art.id}`)} style={{ cursor: 'pointer', flexDirection: 'row', alignItems: 'center', gap: '30px' }}>
                <div className="global-img" style={{ width: 'calc(60% - 90px)', aspectRatio: '16/9', flex: 'none' }}>
                  <img src={imageMap[art.image] || art.image} alt={art.title} style={{ objectFit: 'cover', width: '100%', height: '100%' }} onLoad={(e) => { if (!e.target.src.includes(logoImg)) e.target.style.objectFit = 'cover'; }} onError={(e) => { e.target.onerror = null; e.target.src = logoImg; e.target.style.objectFit = 'contain'; }} />
                </div>
                <div style={{ flex: 1, textAlign: 'left' }}>
                  <h4 style={{ fontSize: '30px', margin: 0 }}>{art.title}</h4>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    );
  };

  const totalPages = 5;

  return (
    <div className="main-page">
      <Header
        leftChild={<Logo />}
        midChild={null}
        rightChild={
          <div style={{ display: 'flex', alignItems: 'center', gap: '0', justifyContent: 'flex-end', width: 'auto' }}>
            <div style={{ position: 'relative' }}>
              <Searchbar className="always-open" />
            </div>
            <UserMenu />
          </div>
        }
        headerTop="on"
        headerMain="on"
        headerBottom="on"
      />

      <main className="category-content">
        <div className="main-content-split">
          <div className="main-full-col" style={{ width: '100%' }}>
            {displayArticles.length > 0 ? (
              <React.Fragment>
                {[...Array(1)].map((_, i) => renderMainContent(i + (currentPage - 1) * 1))}

                <div className="full-width-divider"></div>

                <div className="pol-eco-top5-row" style={{ display: 'flex', gap: '0', marginTop: '40px' }}>
                  <div style={{ flex: 1, borderRight: 'none', paddingRight: '0' }}>
                    {renderPoliticsEconomy(false, true)}
                  </div>
                </div>
              </React.Fragment>
            ) : (
              <div className="empty-category">
                <p>해당 카테고리에 표시할 기사가 없습니다.</p>
              </div>
            )}
          </div>
        </div>

        <div className="full-width-divider"></div>
        {renderSocietySection()}
        <div className="full-width-divider"></div>
        {renderLivingCultureSection()}
        <div className="full-width-divider mobile-only-divider"></div>

        {renderAIRecommendedNews(0 + (currentPage - 1) * 5)}

        {renderScienceSection()}
      </main>
    </div>
  );
};
