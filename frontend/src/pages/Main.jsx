import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import Logo from '../components/Logo';
import logoImg from '../components/Logo.png';
import checkImg from '../components/check.png';
import lineImg from '../components/line.png';
import Searchbar from '../components/Searchbar';
import UserMenu from '../components/UserMenu';
import SkeletonNews from '../components/SkeletonNews';


import './Main.css';
import MobileBottomNav from '../components/MobileBottomNav';
import '../components/MobileBottomNav.css';
import RecommendedNews from '../components/RecommendedNews'; // [New]

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
        const response = await axios.get(`${API_BASE_URL}/reports?limit=1000`); // Fetch enough to cover all sections
        const realArticles = response.data;

        // 2. Map Backend Data to Frontend Structure
        const formattedArticles = realArticles.map(art => ({
          ...art,
          id: art.report_id, // [Fix] Map native ID to 'id' for widespread usage
          category: art.category_name, // Map category_name ('정치', '경제'...) to category
          image: `cluster_${art.cluster_id}`, // Placeholder ID for image map
          short_text: art.contents ? (art.contents.substring(0, 150) + "···") : "내용 없음"
        }));

        // 3. Filter by category (if name param exists)
        const decodedName = decodeURIComponent(name || '');
        let filtered = !decodedName

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
              const selectedImg = allImgUrls[1] || allImgUrls[0]; // Use 2nd image if available, else 1st
              newImageMap[`cluster_${art.cluster_id}`] = selectedImg;
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
  const [currentComparisonIndex, setCurrentComparisonIndex] = useState(0); // [New] Rotate comparison
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
  // Auto-rotate slideshow (Disabled as per request)
  // Auto-rotate comparison items every 10s
  useEffect(() => {
    // Reset comparison index when slide changes
    setCurrentComparisonIndex(0);
  }, [currentSlideIndex]);

  useEffect(() => {
    const slideArticles = displayArticles.slice(0, 3);
    const activeArticle = slideArticles[currentSlideIndex];
    if (!activeArticle) return;

    const interval = setInterval(() => {
      setCurrentComparisonIndex(prev => {
        const bullets = activeArticle?.analysis_result?.media_comparison_bullets || [];
        if (bullets.length <= 1) return 0;
        return (prev + 1) % bullets.length;
      });
    }, 10000); // 10 seconds

    return () => clearInterval(interval);
  }, [currentSlideIndex, displayArticles]);

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

    // Helper: Highlight media names in text
    const highlightMediaText = (text, mediaNames) => {
      if (!text || !mediaNames || mediaNames.length === 0) return text;
      // Sort by length desc to match longest first
      const sortedNames = [...mediaNames].sort((a, b) => b.length - a.length);
      const regex = new RegExp(`(${sortedNames.join('|')})`, 'g');
      const parts = text.split(regex);
      return parts.map((part, index) => {
        if (mediaNames.includes(part)) {
          return (
            <span key={index} className="highlighted-media"><img src={lineImg} alt="line" className="highlight-line-icon" />{part}</span>
          );
        }
        return part;
      });
    };

    const slideArticles = carouselArticles;
    const activeArticle = slideArticles[currentSlideIndex];

    // Get media names for the active article for highlighting
    const activeRelatedNews = articleDetailsMap[`cluster_${activeArticle?.cluster_id}`] || [];
    const activeMediaNames = [...new Set(activeRelatedNews.map(n => n.company_name).filter(Boolean))];

    // Prepare bullets for the active article (Desktop)
    const activeBullets = activeArticle?.analysis_result?.media_comparison_bullets || [];

    return (
      <React.Fragment>
        <h2 className="cat-box-header ai-news-header desktop-only-section">AI 분석 뉴스</h2>

        {/* --- DESKTOP VIEW --- */}
        <section className="main-article-section desktop-only-section">
          <div className="main-image-column">
            <button className="carousel-arrow prev-arrow" onClick={(e) => { e.stopPropagation(); setCurrentSlideIndex(prev => (prev - 1 + 3) % 3); }}>&#x2039;</button>
            <div className="article-image-center">
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
                      <div className="main-image-text"><h3>{art.title}</h3></div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
          <div className="main-right-col">
            <div className="article-info-side">
              {slideArticles.map((art, idx) => {
                const isActive = idx === currentSlideIndex;
                if (!isActive) return null;
                return (
                  <div
                    key={art.id || idx}
                    className={`analysis-block ${isActive ? 'active fade-animate' : ''}`}
                    onClick={() => navigate(`/article/${art.report_id}`)}
                  >
                    <h2 className="analysis-title">{art.title}</h2>
                    <p className="analysis-desc">{art.short_text || "AI 생성 기사 내용"}</p>
                  </div>
                );
              })}
            </div>
            <div className="highlights-side">
              <h3 className="highlights-title">언론사별 비교분석</h3>
              <div key={`hl-${currentSlideIndex}`} className="highlight-list fade-animate">
                <div className="main-comparison-container">
                  <ul className="main-comparison-list">
                    {activeBullets.slice(currentComparisonIndex, currentComparisonIndex + 1).map((item, idx) => {
                      const isString = typeof item === 'string';

                      let content = "";
                      let hashtags = [];

                      if (isString) content = item;
                      else if (item.summary) {
                        content = item.summary;
                        hashtags = item.hashtags || [];
                      }
                      else if (item.analysis) content = item.analysis;

                      return (
                        <li key={`${idx}-${currentComparisonIndex}`} className="main-comparison-item fade-slide-up">
                          <div className="main-analysis-text">
                            {!isString && item.company && (
                              <div className="main-company-header" style={{ display: 'flex', alignItems: 'center', gap: '5px', marginBottom: '4px' }}>
                                <span style={{ fontWeight: 'bold', color: '#1a73e8' }}>{item.company}</span>
                                {hashtags.slice(0, 2).map((tag, tIdx) => (
                                  <span key={tIdx} style={{ fontSize: '0.75rem', backgroundColor: '#e8f0fe', color: '#1967d2', padding: '2px 6px', borderRadius: '10px' }}>{tag}</span>
                                ))}
                              </div>
                            )}
                            {highlightMediaText((content || "").replace(/^- /, '').replace(/\[/g, '').replace(/\]/g, ''), activeMediaNames)}
                            {item.evidence && (
                              <p className="main-comparison-evidence">
                                {item.evidence}
                              </p>
                            )}
                          </div>
                        </li>
                      );
                    })}
                    {activeBullets.length === 0 && (
                      <li className="main-comparison-item">분석된 결과가 없습니다.</li>
                    )}
                  </ul>
                </div>
              </div>
            </div>
          </div>
          <button className="carousel-arrow next-arrow" onClick={(e) => { e.stopPropagation(); setCurrentSlideIndex(prev => (prev + 1) % 3); }}>&#x203A;</button>
        </section>

        {/* --- MOBILE VIEW (Whole Section Slide) --- */}
        <section className="main-article-section-mobile mobile-only-section">
          {/* Duplicate Header Removed */}
          <div
            className="mobile-full-slider"
            onTouchStart={handleTouchStart}
            onTouchEnd={handleTouchEnd}
          >
            <div
              className="mobile-slide-track"
              style={{ transform: `translateX(-${currentSlideIndex * 100}%)` }}
            >
              {slideArticles.map((art, idx) => {
                const imgUrl = imageMap[art.image] || art.image;
                // const hls = getHighlights(art); // Unused now
                return (
                  <div key={idx} className="mobile-whole-slide">
                    {/* Image + Title + Nav Buttons Part */}
                    <div className="mobile-slide-top" onClick={() => navigate(`/article/${art.report_id}`)}>
                      <img
                        src={imgUrl}
                        alt={art.title}
                        onError={(e) => { e.target.onerror = null; e.target.src = logoImg; e.target.style.objectFit = 'contain'; }}
                      />
                      <div className="main-image-text"><h3>{art.title}</h3></div>
                      <button
                        className="mobile-slide-nav prev"
                        onClick={(e) => { e.stopPropagation(); setCurrentSlideIndex(prev => (prev - 1 + 3) % 3); }}
                      >&#x2039;</button>
                      <button
                        className="mobile-slide-nav next"
                        onClick={(e) => { e.stopPropagation(); setCurrentSlideIndex(prev => (prev + 1) % 3); }}
                      >&#x203A;</button>
                    </div>
                    {/* Highlights Part */}
                    <div className="mobile-slide-bottom">
                      <h3 className="highlights-title">언론사별 비교분석</h3>
                      <div className="main-comparison-container">
                        <ul className="main-comparison-list">
                          {(art?.analysis_result?.media_comparison_bullets || []).slice(currentComparisonIndex, currentComparisonIndex + 1).map((item, idx) => {
                            const relatedNews = articleDetailsMap[`cluster_${art.cluster_id}`] || [];
                            const articleMediaNames = [...new Set(relatedNews.map(n => n.company_name).filter(Boolean))];

                            const isString = typeof item === 'string';
                            let content = "";
                            let hashtags = [];

                            if (isString) content = item;
                            else if (item.summary) {
                              content = item.summary;
                              hashtags = item.hashtags || [];
                            }
                            else if (item.analysis) content = item.analysis;

                            return (
                              <li key={`${idx}-${currentComparisonIndex}`} className="main-comparison-item fade-slide-up">
                                <div className="main-analysis-text">
                                  {!isString && item.company && (
                                    <div className="main-company-header" style={{ display: 'flex', alignItems: 'center', gap: '5px', marginBottom: '4px' }}>
                                      <span style={{ fontWeight: 'bold', color: '#1a73e8' }}>{item.company}</span>
                                      {hashtags.slice(0, 2).map((tag, tIdx) => (
                                        <span key={tIdx} style={{ fontSize: '0.75rem', backgroundColor: '#e8f0fe', color: '#1967d2', padding: '2px 6px', borderRadius: '10px' }}>{tag}</span>
                                      ))}
                                    </div>
                                  )}
                                  {highlightMediaText((content || "").replace(/^- /, '').replace(/\[/g, '').replace(/\]/g, ''), articleMediaNames)}
                                  {item.evidence && (
                                    <p className="main-comparison-evidence">
                                      {item.evidence}
                                    </p>
                                  )}
                                </div>
                              </li>
                            );
                          })}
                          {(!art?.analysis_result?.media_comparison_bullets || art.analysis_result.media_comparison_bullets.length === 0) && (
                            <li className="main-comparison-item">분석된 결과가 없습니다.</li>
                          )}
                        </ul>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="carousel-dots-mobile">
            {[0, 1, 2].map(dotIdx => (
              <span key={dotIdx} className={`carousel-dot ${dotIdx === currentSlideIndex ? 'active' : ''}`} onClick={() => setCurrentSlideIndex(dotIdx)} />
            ))}
          </div>



        </section>
      </React.Fragment >
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

      {/* Main Content (Carousel) - Outside Category Content for Full Bleed */}
      {!loading && displayArticles.length > 0 && (
        <div className="main-carousel-outer">
          {renderMainContent()}
          {/* [New] Recommended News (YouTube Style) */}
          <RecommendedNews allArticles={displayArticles} userName={userName} imageMap={imageMap} />
        </div>
      )}

      <main className="category-content">
        {loading ? (
          <div className="main-skeleton-container skeleton-wrapper">
            <SkeletonNews type="main" />
            <div className="skeleton-grid-row">
              <div className="skeleton-grid-item"><SkeletonNews type="grid" /></div>
              <div className="skeleton-grid-item"><SkeletonNews type="grid" /></div>
            </div>
          </div>
        ) : (
          <>
            <div className="main-content-split">
              <div className="main-full-col">
                {displayArticles.length > 0 ? (
                  <React.Fragment>
                    {/* Carousel moved out */}
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
      <MobileBottomNav />
    </div >
  );
};