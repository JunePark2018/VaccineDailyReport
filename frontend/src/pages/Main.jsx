import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import Logo from '../components/Logo';
import Searchbar from '../components/Searchbar';
import UserMenu from '../components/UserMenu';



import './Main.css';

export const Main = () => {
  // Main page doesn't use useParams for category usually, but keeping structure similar
  // We can simulate 'name' being undefined or empty to show all articles
  const { name } = useParams();
  const navigate = useNavigate();
  const [currentPage, setCurrentPage] = useState(1);
  const [displayArticles, setDisplayArticles] = useState([]);
  const [imageMap, setImageMap] = useState({});
  const itemsPerPage = 5;

  useEffect(() => {
    setCurrentPage(1);

    const loadData = async () => {
      try {
        // Dynamically import sample data to allow the app to run even if the folder is missing
        const [articlesModule, imagesModule] = await Promise.all([
          import('../sample_/sampleArticle.json').catch(() => ({ default: [] })),
          import('../sample_/imageAssets').catch(() => ({ default: {} }))
        ]);

        const articles = articlesModule.default || [];
        const images = imagesModule.default || {};

        setImageMap(images);

        // Filter articles by category name
        // If category is '전체메뉴', show all articles
        // For Main page, name is likely undefined, so it behaves like '전체메뉴'
        const decodedName = decodeURIComponent(name || '');
        const filtered = (decodedName === '전체메뉴' || !decodedName)
          ? articles
          : articles.filter(a => {
            if (!a.category) return false;
            if (Array.isArray(a.category)) {
              return a.category.includes(decodedName);
            }
            return a.category === decodedName;
          });

        // Randomly shuffle filtered articles when category changes
        if (filtered.length > 0) {
          const shuffled = [...filtered].sort(() => Math.random() - 0.5);
          setDisplayArticles(shuffled);
        } else {
          setDisplayArticles([]);
        }
      } catch (error) {
        console.warn('Sample data could not be loaded:', error);
        setDisplayArticles([]);
        setImageMap({});
      }
    };

    loadData();
  }, [name]);



  // Function to render the main content block (Featured, Highlights, Grid)
  const renderMainContent = (index) => {
    if (!displayArticles || displayArticles.length === 0) return null;

    // Use 5 articles per loop to match the layout (1 main + 4 grid)
    const baseIndex = (index * 5) % displayArticles.length;
    const mainArticle = displayArticles[baseIndex];

    const mainData = {
      title: mainArticle?.title || "AI 생성 기사 제목",
      description: mainArticle?.short_text || "AI 생성 기사 내용 (추후 데이터 연동 예정)",
      image: mainArticle ? (imageMap[mainArticle.image] || mainArticle.image) : null
    };

    // Calculate Grid Articles for Right Side (Next 4 articles)
    const gridArticles = [
      displayArticles[(baseIndex + 1) % displayArticles.length],
      displayArticles[(baseIndex + 2) % displayArticles.length],
      displayArticles[(baseIndex + 3) % displayArticles.length],
      displayArticles[(baseIndex + 4) % displayArticles.length],
    ];

    // Helper to format article data
    const getArticleData = (article) => ({
      title: article?.title || "AI 생성 기사 제목",
      description: article?.short_text || "AI 생성 기사 내용"
    });

    const rightArticles = [
      getArticleData(gridArticles[0]),
      getArticleData(gridArticles[1]),
      getArticleData(gridArticles[2]),
      getArticleData(gridArticles[3])
    ];

    const highlights = [
      { keyword: 'TEST KEYWORD', content: 'ANALYSIS CONTENT SAMPLE TEXT FOR TESTING ANALYSIS CONTENT SAMPLE TEXT FOR TESTING' },
      { keyword: 'TEST KEYWORD', content: 'ANALYSIS CONTENT SAMPLE TEXT FOR TESTING ANALYSIS CONTENT SAMPLE TEXT FOR TESTING' },
      { keyword: 'TEST KEYWORD', content: 'ANALYSIS CONTENT SAMPLE TEXT FOR TESTING ANALYSIS CONTENT SAMPLE TEXT FOR TESTING' },
      { keyword: 'TEST KEYWORD', content: 'ANALYSIS CONTENT SAMPLE TEXT FOR TESTING ANALYSIS CONTENT SAMPLE TEXT FOR TESTING' }
    ];

    return (
      <React.Fragment key={index}>
        <section className="main-article-section" style={{ display: 'flex', gap: '40px', marginBottom: '30px' }}>

          {/* Left: 4 Articles (Restored to Left) */}
          <div className="article-info-side" onClick={() => navigate('/article')} style={{ flex: 1, cursor: 'pointer', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
            {rightArticles.map((art, artIdx) => (
              <React.Fragment key={artIdx}>
                <div className="analysis-block">
                  <h2>{art.title}</h2>
                  <p>{art.description}</p>
                </div>
                {artIdx < rightArticles.length - 1 && <div className="info-divider"></div>}
              </React.Fragment>
            ))}
          </div>

          {/* Center Column (Image) */}
          <div className="main-image-column" style={{ flex: 1.6, display: 'flex', flexDirection: 'column' }}>
            <div className="ai-news-badge" style={{ borderBottom: 'none', borderLeft: '5px solid #000', paddingLeft: '10px', paddingBottom: '2px', lineHeight: '1', marginLeft: '0', marginBottom: '10px' }}>AI 뉴스</div>
            <div className="article-image-center" onClick={() => navigate('/article')} style={{ cursor: 'pointer', width: '100%', aspectRatio: '1.5/1' }}>
              <img src={mainData.image} alt="Main" />
              <div className="main-image-text">
                <h3>{mainData.title || "AI 생성 기사 제목"}</h3>
              </div>
            </div>
          </div>

          {/* Right: Highlights (Restored to Right) */}
          <div className="highlights-side" style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
            <div className="highlight-list" style={{ display: 'flex', flexDirection: 'column', height: '100%', justifyContent: 'space-between' }}>
              {highlights.map((item, hIndex) => (
                <React.Fragment key={hIndex}>
                  <div className="highlight-item" style={{ alignItems: 'flex-start', textAlign: 'left' }}>
                    <span className="highlight-keyword" style={{ color: '#ff4d4d', fontWeight: 'bold', fontSize: '16px', marginBottom: '5px' }}>{item.keyword}</span>
                    <span className="highlight-content" style={{ fontSize: '13px', lineHeight: '1.5', color: '#444', display: '-webkit-box', overflow: 'hidden', WebkitBoxOrient: 'vertical', WebkitLineClamp: 2 }}>"{item.content}"</span>
                  </div>
                  {hIndex < highlights.length - 1 && <div className="info-divider" style={{ margin: '30px 0' }}></div>}
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
                  <div className="ai-related-item" onClick={() => navigate('/article')} style={{ cursor: 'pointer' }}>
                    <h4>{art?.title || "Title Text Sample"}</h4>
                    <p>{art?.short_text || "TEXT SAMPLE content description..."}</p>
                  </div>
                  {i < aiRelatedArticles.length - 1 && <div className="ai-divider"></div>}
                </div>
              ))}
            </div>
            <div className="ai-main-image-container">
              <img src={mainImage} alt="AI Main" />
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
        <h3 style={{ fontSize: '18px', fontWeight: '800', borderLeft: '5px solid #000', borderBottom: 'none', paddingLeft: '10px', paddingBottom: '3px', marginBottom: '20px', textAlign: 'left', width: 'fit-content', lineHeight: '1' }}>TOP 5 뉴스</h3>
        <div className="top10-grid" style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '20px' }}>
          {top5Articles.map((article, index) => {
            const imgPath = imageMap[article.image] || article.image;
            return (
              <div key={index} className="top10-item" onClick={() => navigate('/article')} style={{ display: 'flex', flexDirection: 'row', gap: '20px', cursor: 'pointer', alignItems: 'center' }}>
                <span className="top10-rank" style={{ fontSize: '36px', fontWeight: '900', fontStyle: 'italic', color: index < 3 ? '#cc0000' : '#333', lineHeight: '1', minWidth: '30px' }}>
                  {index + 1}
                </span>
                <div style={{ width: '180px', height: '100px', borderRadius: '1px', overflow: 'hidden', flex: 'none' }}>
                  <img src={imgPath} alt={article.title} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
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
        <h3 className="cat-box-header" onClick={() => navigate(link)} style={{ cursor: 'pointer' }}>{title}</h3>
        {articles.length > 0 && (
          <div className="cat-box-content">
            <div className="cat-box-main" onClick={() => navigate('/article')} style={{ cursor: 'pointer' }}>
              <div className="cat-box-img" style={{ aspectRatio: '16/9', width: '100%' }}>
                <img src={imageMap[articles[0].image] || articles[0].image} alt={articles[0].title} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
              </div>
              <h4 className="cat-box-title" style={{ fontSize: '16px', margin: '10px 0 5px 0' }}>{articles[0].title}</h4>
              <p style={{ fontSize: '12px', color: '#666', margin: 0 }}>{articles[0].short_text}</p>
            </div>
            {articles.length > 1 && (
              <div className="cat-box-list">
                {articles.slice(1).map((art, i) => (
                  <div key={i} className="cat-box-list-item" onClick={() => navigate('/article')} style={{ cursor: 'pointer' }}>
                    <h5>{art.title}</h5>
                    <p>{art.short_text}</p>
                  </div>
                ))}
              </div>
            )}
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
          <h3 className="cat-box-header" onClick={() => navigate('/society')} style={{ cursor: 'pointer', borderLeft: '5px solid #000', paddingLeft: '10px', paddingBottom: '2px', lineHeight: '1' }}>사회</h3>
          <div className="global-grid" style={{ gridTemplateColumns: 'repeat(3, 1fr)' }}>
            {society.map((art, i) => (
              <div key={i} className="global-card" onClick={() => navigate('/article')} style={{ cursor: 'pointer' }}>
                <div className="global-img">
                  <img src={imageMap[art.image] || art.image} alt={art.title} />
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
          <h3 className="cat-box-header" onClick={() => navigate('/culture')} style={{ cursor: 'pointer', borderLeft: '5px solid #000', paddingLeft: '10px', paddingBottom: '2px', lineHeight: '1' }}>생활/문화</h3>
          <div className="global-grid" style={{ gridTemplateColumns: 'repeat(2, 1fr)' }}>
            {culture.map((art, i) => (
              <div key={i} className="global-card" onClick={() => navigate('/article')} style={{ cursor: 'pointer' }}>
                <div className="global-img">
                  <img src={imageMap[art.image] || art.image} alt={art.title} />
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
          <h3 className="cat-box-header" onClick={() => navigate('/science')} style={{ cursor: 'pointer' }}>IT/과학</h3>
          <div className="global-grid" style={{ gridTemplateColumns: '1fr' }}>
            {science.map((art, i) => (
              <div key={i} className="global-card" onClick={() => navigate('/article')} style={{ cursor: 'pointer', flexDirection: 'row', alignItems: 'center', gap: '30px' }}>
                <div className="global-img" style={{ width: '60%', aspectRatio: '21/9', flex: 'none' }}>
                  <img src={imageMap[art.image] || art.image} alt={art.title} style={{ objectFit: 'cover', width: '100%', height: '100%' }} />
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

      <main className="category-content">
        <div className="main-content-split">
          <div className="main-full-col" style={{ width: '100%' }}>
            {displayArticles.length > 0 ? (
              <React.Fragment>
                {[...Array(1)].map((_, i) => renderMainContent(i + (currentPage - 1) * 1))}

                <div className="full-width-divider"></div>

                <div className="pol-eco-top5-row" style={{ display: 'flex', gap: '0', marginTop: '40px' }}>
                  <div style={{ flex: 6, borderRight: 'none', paddingRight: '60px' }}>
                    {renderPoliticsEconomy(false, true)}
                  </div>
                  <div style={{ flex: 4, borderLeft: 'none', paddingLeft: '60px' }}>
                    {renderTop10News()}
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

        {renderAIRecommendedNews(0 + (currentPage - 1) * 5)}

        {renderScienceSection()}
      </main>
    </div>
  );
};
