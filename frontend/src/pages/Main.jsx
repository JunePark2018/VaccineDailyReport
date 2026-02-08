import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import Logo from '../components/Logo';
import logoImg from '../components/Logo.png';
import Searchbar from '../components/Searchbar';
import UserMenu from '../components/UserMenu';
import SkeletonNews from '../components/SkeletonNews';


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
  const [loading, setLoading] = useState(true); // Loading state
  const itemsPerPage = 5;

  // Check login status
  useEffect(() => {
    const loggedIn = localStorage.getItem('isLoggedIn') === 'true';
    const storedUserName = localStorage.getItem('username');

    setIsLoggedIn(loggedIn);
    if (storedUserName) {
      setUserName(storedUserName);
    }
  }, []);

  useEffect(() => {
    setCurrentPage(1);

    const loadData = async () => {
      setLoading(true);
      try {
        // 1. Fetch AI Generated News (Limit 50 for main page coverage)
        const response = await axios.get(`${API_BASE_URL}/reports?limit=100`); // Fetch enough to cover all sections
        const realArticles = response.data;

        // 2. Map Backend Data to Frontend Structure
        const formattedArticles = realArticles.map(art => ({
          ...art,
          id: art.report_id, // [Fix] Map native ID to 'id' for widespread usage
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
            const imgRes = await axios.get(`${API_BASE_URL}/reports/clusters/${art.cluster_id}/news`);
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
        setImageMap({});
      } finally {
        // Delay slightly for smooth transition if data loads too fast, or just set false
        setLoading(false);
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

  // --- Deduplication Logic ---
  // Pre-calculate lists to ensure no duplicates across sections
  const usedIds = new Set();

  // 1. Carousel (Top 3)
  const carouselArticles = displayArticles.slice(0, 3);
  carouselArticles.forEach(a => usedIds.add(a.id));

  // Helper to get unique articles for a category
  const getUniqueArticles = (cat, limit) => {
    return displayArticles.filter(a => {
      const match = a.category === cat || (Array.isArray(a.category) && a.category.includes(cat));
      if (match && !usedIds.has(a.id)) {
        usedIds.add(a.id);
        return true;
      }
      return false;
    }).slice(0, limit);
  };

  const politicsArticles = getUniqueArticles('정치', 6);
  const economyArticles = getUniqueArticles('경제', 3);
  const societyArticles = getUniqueArticles('사회', 1);
  const scienceArticles = getUniqueArticles('IT/과학', 1);

  // Function to render the main content block (Slideshow)
  const renderMainContent = () => {
    if (!carouselArticles || carouselArticles.length === 0) return null;

    const slideArticles = carouselArticles;
    const activeArticle = slideArticles[currentSlideIndex];
    const activeImage = activeArticle ? (imageMap[activeArticle.image] || activeArticle.image) : null;
    const relatedNews = articleDetailsMap[activeArticle?.image] || [];

    // Parse 'media_comparison_bullets' for highlights
    const bullets = activeArticle?.analysis_result?.media_comparison_bullets || [];

    let highlights = [];
    if (bullets.length > 0) {
      // 1. Map & Filter strict matches only
      const parsedBullets = bullets.map(text => {
        const cleanText = text.replace(/^- /, '');
        let match = cleanText.match(/^\[(.*?)\]\s*(.*)/);
        if (!match) match = cleanText.match(/^([^:]+):\s*(.*)/);
        if (!match) match = cleanText.match(/^([^-]+)\s-\s*(.*)/);

        if (match) {
          let kw = match[1].trim().replace(/(은|는)$/, '');
          return { keyword: `"${kw}"`, content: match[2].trim() };
        }
        return null;
      }).filter(Boolean);

      // 2. Deduplicate by keyword (media name)
      const seenKeywords = new Set();
      const uniqueHighlights = [];

      for (const item of parsedBullets) {
        if (!seenKeywords.has(item.keyword)) {
          seenKeywords.add(item.keyword);
          uniqueHighlights.push(item);
        }
        if (uniqueHighlights.length >= 4) break; // Limit to 4
      }

      highlights = uniqueHighlights;
    }

    if (highlights.length === 0 && relatedNews.length > 0) {
      highlights = relatedNews.slice(0, 4).map(news => ({
        keyword: news.company_name || '언론사',
        content: news.contents ? (news.contents.substring(0, 80) + '...') : '내용 없음'
      }));
    }

    return (
      <React.Fragment>
        <h2 className="cat-box-header ai-news-header">AI 뉴스</h2>
        <section className="main-article-section">
          <div className="article-info-side">
            {slideArticles.map((art, idx) => {
              const isActive = idx === currentSlideIndex;
              return (
                <React.Fragment key={art.id || idx}>
                  <div
                    className={`analysis-block ${isActive ? 'active' : ''}`}
                    onClick={() => setCurrentSlideIndex(idx)}
                  >
                    <h2 className="analysis-title">{art.title}</h2>
                    <p className="analysis-desc">{art.short_text || "AI 생성 기사 내용"}</p>
                  </div>
                </React.Fragment>
              );
            })}
          </div>
          <div className="main-image-column">
            <div
              className="article-image-center"
              onTouchStart={handleTouchStart}
              onTouchEnd={handleTouchEnd}
            >
              <div
                className="carousel-track"
                style={{ '--slide-transform': `translateX(-${currentSlideIndex * 100}%)` }}
              >
                {slideArticles.map((art, idx) => {
                  const imgUrl = imageMap[art.image] || art.image;
                  const isActive = idx === currentSlideIndex;
                  return (
                    <div
                      key={art.id || idx}
                      className={`carousel-slide ${isActive ? 'active' : ''}`}
                      onClick={() => navigate(`/article/${art.report_id}`)}
                    >
                      <img
                        src={imgUrl}
                        alt={art.title}
                        onLoad={(e) => { if (!e.target.src.includes(logoImg)) e.target.style.objectFit = 'cover'; }}
                        onError={(e) => { e.target.onerror = null; e.target.src = logoImg; e.target.style.objectFit = 'contain'; }}
                      />
                    </div>
                  );
                })}
              </div>
              <button className="carousel-arrow prev-arrow" onClick={(e) => { e.stopPropagation(); setCurrentSlideIndex(prev => (prev - 1 + 3) % 3); }}>&#10094;</button>
              <button className="carousel-arrow next-arrow" onClick={(e) => { e.stopPropagation(); setCurrentSlideIndex(prev => (prev + 1) % 3); }}>&#10095;</button>
            </div>
            <div className="carousel-dots-mobile">
              {[0, 1, 2].map(dotIdx => (
                <span key={dotIdx} className={`carousel-dot ${dotIdx === currentSlideIndex ? 'active' : ''}`} onClick={() => setCurrentSlideIndex(dotIdx)} />
              ))}
            </div>
            <div className="carousel-highlights-mobile">
              {highlights.slice(0, 2).map((item, midx) => (
                <div key={midx} className="highlight-item-mobile">
                  <span className="hl-keyword">{item.keyword}</span>
                  <span className="hl-content">{item.content}</span>
                </div>
              ))}
            </div>
          </div>
          <div className="highlights-side">
            <h3 className="highlights-title">언론사 비교분석</h3>
            <div
              key={`hl-${currentSlideIndex}`}
              className="highlight-list fade-animate"
            >
              {highlights.slice(0, 3).map((item, hIndex) => (
                <React.Fragment key={hIndex}>
                  <div className="highlight-item">
                    <span className="highlight-keyword">{item.keyword}</span>
                    <span className="highlight-content">{item.content}</span>
                  </div>
                </React.Fragment>
              ))}
            </div>
          </div>
        </section>
      </React.Fragment>
    );
  };

  const renderPoliticsEconomy = () => {
    const renderPoliticsSection = () => (
      <div className="politics-section">
        <h2 className="cat-box-header" onClick={() => navigate('/politics')}>정치</h2>
        <div className="politics-grid">
          {politicsArticles.map((art, i) => (
            <div key={i} className="politics-card" onClick={() => navigate(`/article/${art.id}`)}>
              <div className="politics-img">
                <img
                  src={imageMap[art.image] || art.image}
                  alt={art.title}
                  onLoad={(e) => { if (!e.target.src.includes(logoImg)) e.target.style.objectFit = 'cover'; }}
                  onError={(e) => { e.target.onerror = null; e.target.src = logoImg; e.target.style.objectFit = 'contain'; }}
                />
              </div>
              <div className="politics-info">
                <h3 className="politics-title">{art.title}</h3>
                <p className="politics-desc">{art.short_text}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    );

    const renderEconomySection = () => (
      <div className="economy-section">
        <h2 className="cat-box-header" onClick={() => navigate('/economics')}>경제</h2>
        <div className="economy-column-list">
          {economyArticles.map((art, i) => (
            <div key={i} className="economy-card" onClick={() => navigate(`/article/${art.id}`)}>
              <div className="economy-img">
                <img
                  src={imageMap[art.image] || art.image}
                  alt={art.title}
                  onLoad={(e) => { if (!e.target.src.includes(logoImg)) e.target.style.objectFit = 'cover'; }}
                  onError={(e) => { e.target.onerror = null; e.target.src = logoImg; e.target.style.objectFit = 'contain'; }}
                />
              </div>
              <h3 className="economy-title">{art.title}</h3>
            </div>
          ))}
        </div>
      </div>
    );

    const renderSocietyLargeSection = () => {
      const art = societyArticles[0];
      if (!art) return null;
      return (
        <div className="society-large-section">
          <h2 className="cat-box-header" onClick={() => navigate('/society')}>사회</h2>
          <div className="society-large-card" onClick={() => navigate(`/article/${art.id}`)}>
            <div className="society-large-img">
              <img
                src={imageMap[art.image] || art.image}
                alt={art.title}
                onLoad={(e) => { if (!e.target.src.includes(logoImg)) e.target.style.objectFit = 'cover'; }}
                onError={(e) => { e.target.onerror = null; e.target.src = logoImg; e.target.style.objectFit = 'contain'; }}
              />
            </div>
            <div className="society-large-info">
              <h3 className="society-large-title">{art.title}</h3>
              <p className="society-large-desc">{art.short_text}</p>
            </div>
          </div>
        </div>
      );
    };

    return (
      <section className="complex-grid-section">
        <div className="complex-left-col">
          {renderPoliticsSection()}
          <div className="complex-inner-divider"></div>
          {renderSocietyLargeSection()}
          <div className="complex-inner-divider"></div>
          {renderScienceSection()}
        </div>
        <div className="complex-right-col">
          {renderEconomySection()}
        </div>
      </section>
    );
  };



  const renderScienceSection = () => {
    const science = scienceArticles;
    if (science.length === 0) return null;

    return (
      <section className="category-detailed-section science-section">
        <div className="cat-global-row">
          <h2 className="cat-box-header" onClick={() => navigate('/science')}>IT/과학</h2>
          <div className="global-grid science-grid">
            {science.map((art, i) => (
              <div key={i} className="global-card science-card" onClick={() => navigate(`/article/${art.id}`)}>
                <div className="global-img">
                  <img src={imageMap[art.image] || art.image} alt={art.title} onLoad={(e) => { if (!e.target.src.includes(logoImg)) e.target.style.objectFit = 'cover'; }} onError={(e) => { e.target.onerror = null; e.target.src = logoImg; e.target.style.objectFit = 'contain'; }} />
                </div>
                <div className="science-info">
                  <h5>{art.title}</h5>
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
        leftChild={null}
        midChild={<Logo />}
        rightChild={
          <div className="header-right-wrapper">
            <div className="search-input-wrapper">
              <Searchbar className="always-open rounded-search" />
            </div>
            <UserMenu className="rounded-user-menu" />
          </div>
        }
        headerTop="on"
        headerMain="on"
        headerBottom="on"
      />

      <main className="category-content">
        {loading ? (
          <div className="main-skeleton-container skeleton-wrapper">
            <SkeletonNews type="main" />
            <div className="skeleton-grid-row">
              <div style={{ flex: 1 }}><SkeletonNews type="grid" /></div>
              <div style={{ flex: 1 }}><SkeletonNews type="grid" /></div>
            </div>
          </div>
        ) : (
          <>
            <div className="main-content-split">
              <div className="main-full-col">
                {displayArticles.length > 0 ? (
                  <React.Fragment>
                    {renderMainContent()}
                    <div className="complex-layout-wrapper">
                      {renderPoliticsEconomy()}
                    </div>
                  </React.Fragment>
                ) : (
                  <div className="empty-category">
                    <p>해당 카테고리에 표시할 기사가 없습니다.</p>
                  </div>
                )}
              </div>
            </div>
            <div className="full-width-divider mobile-only-divider"></div>
          </>
        )}
      </main >
    </div >
  );
};