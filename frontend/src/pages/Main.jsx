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
  // This is repeated 5 times as requested by the user
  /* Main Content Section (Categories + Main Image) */
  const renderMainContent = (index) => {
    if (!displayArticles || displayArticles.length === 0) return null;

    // Use 1 article for main image per loop
    const baseIndex = (index * 1) % displayArticles.length;
    const mainArticle = displayArticles[baseIndex];

    const mainData = {
      title: mainArticle?.title || "AI 생성 기사 제목",
      description: mainArticle?.short_text || "AI 생성 기사 내용 (추후 데이터 연동 예정)",
      image: mainArticle ? (imageMap[mainArticle.image] || mainArticle.image) : null
    };

    // Calculate Grid Articles for Left Side (Next 3 articles)
    const gridArticles = [
      displayArticles[(baseIndex + 1) % displayArticles.length],
      displayArticles[(baseIndex + 2) % displayArticles.length],
      displayArticles[(baseIndex + 3) % displayArticles.length],
    ];

    // Helper to format article data
    const getArticleData = (article) => ({
      title: article?.title || "AI 생성 기사 제목",
      description: article?.short_text || "AI 생성 기사 내용"
    });

    const leftArticles = [
      getArticleData(gridArticles[0]),
      getArticleData(gridArticles[1]),
      getArticleData(gridArticles[2])
    ];

    const highlights = [
      { keyword: '중점으로 둔 키워드', content: '"해당 키워드에 대한 요약한 내용"' },
      { keyword: '중점으로 둔 키워드', content: '"해당 키워드에 대한 요약한 내용"' }
    ];

    return (
      <React.Fragment key={index}>
        {/* Main Section: Left (Articles) + Center (Main Image) */}
        <section className="main-article-section">
          {/* Left Column: 3 Articles */}
          <div className="article-info-side" onClick={() => navigate('/article')} style={{ cursor: 'pointer' }}>
            <div className="analysis-block">
              <h2>{leftArticles[0].title}</h2>
              <p>{leftArticles[0].description}</p>
            </div>
            <div className="info-divider"></div>
            <div className="analysis-block">
              <h2>{leftArticles[1].title}</h2>
              <p>{leftArticles[1].description}</p>
            </div>
            <div className="info-divider"></div>
            <div className="analysis-block">
              <h2>{leftArticles[2].title}</h2>
              <p>{leftArticles[2].description}</p>
            </div>
          </div>

          {/* Center Column (Image) */}
          <div className="main-image-column">
            <div className="ai-news-badge">AI 뉴스</div>
            <div className="article-image-center" onClick={() => navigate('/article')} style={{ cursor: 'pointer' }}>
              <img src={mainData.image} alt="Main" />
              <div className="main-image-text">
                <h3>{mainData.title || "AI 생성 기사 제목"}</h3>
                <p>{mainData.description || "AI 생성 기사 내용"}</p>
              </div>
            </div>
          </div>
        </section>

        {/* Highlights Section (Full Width below Image & Left Articles) */}
        <div className="highlights-container" style={{ marginTop: '20px', borderTop: '1px solid #eee', paddingTop: '20px', display: 'flex', gap: '16px' }}>

          {/* Left: Title (Aligns with Article Info) */}
          <div style={{ flex: 1, display: 'flex', alignItems: 'center' }}>
            <div className="highlight-title" style={{ fontWeight: '800', fontSize: '16px', color: '#000' }}>AI가 분석한 핵심 내용</div>
          </div>

          {/* Right: Divider & Keywords (Aligns with Image) */}
          <div style={{ flex: 2.7, display: 'flex', alignItems: 'center', gap: '30px' }}>
            <div className="highlight-divider"></div>
            {/* Map Keywords */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '30px', flex: 1 }}>
              {highlights.map((item, hIndex) => (
                <React.Fragment key={hIndex}>
                  <div className="highlight-item">
                    <span className="highlight-keyword">{item.keyword}</span>
                    <span className="highlight-content">{item.content}</span>
                  </div>
                  {hIndex < highlights.length - 1 && <div className="highlight-divider"></div>}
                </React.Fragment>
              ))}
            </div>
          </div>
        </div>
      </React.Fragment>
    );
  };

  const renderAIRecommendedNews = (mainBaseIndex) => {
    if (!displayArticles || displayArticles.length === 0) return null;

    // Use an offset from the articles displayed in the main section (which uses 7 articles)
    const offset = 7;
    const aiBaseIndex = (mainBaseIndex + offset) % displayArticles.length;

    // Pick 5 articles for AI recommendation
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
            {/* Left: List of 4 related articles (Text only) */}
            <div className="ai-related-list">
              <h3>AI 추천 뉴스</h3>
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

            {/* Right: One large image */}
            <div className="ai-main-image-container">
              <img src={mainImage} alt="AI Main" />
            </div>
          </div>
        </div>
      </section>
    );
  };

  /* TOP 10 News Section */
  const renderTop10News = () => {
    if (!displayArticles || displayArticles.length === 0) return null;

    const top10Articles = displayArticles.slice(0, 10);

    return (
      <section className="top10-section">
        <h3>TOP 10 뉴스</h3>
        <div className="top10-grid">
          {top10Articles.map((article, index) => {
            const imgPath = imageMap[article.image] || article.image;
            return (
              <div key={index} className="top10-item" onClick={() => navigate('/article')} style={{ cursor: 'pointer' }}>
                <div className="top10-rank">{index + 1}</div>
                <div className="top10-image-wrapper">
                  <img src={imgPath} alt={article.title} />
                </div>
                <div className="top10-info">
                  <h4 className="top10-title">{article.title}</h4>
                </div>
              </div>
            );
          })}
        </div>
      </section>
    );
  };

  /* Politics & Economy Section (Left Column) */
  const renderPoliticsEconomy = () => {
    if (!displayArticles || displayArticles.length === 0) return null;

    const getCatArticles = (cat) => displayArticles.filter(a => a.category === cat || (Array.isArray(a.category) && a.category.includes(cat)));
    const politics = getCatArticles('정치').slice(0, 4);
    const economy = getCatArticles('경제').slice(0, 4);

    const renderBox = (title, articles) => (
      <div className="cat-box-column">
        <h3 className="cat-box-header" onClick={() => {
          if (title === '정치') navigate('/politics');
          else if (title === '경제') navigate('/economy');
        }} style={{ cursor: 'pointer' }}>{title}</h3>
        {articles.length > 0 && (
          <div className="cat-box-content">
            {/* Main Image Article */}
            <div className="cat-box-main" onClick={() => navigate('/article')} style={{ cursor: 'pointer' }}>
              <div className="cat-box-img">
                <img src={imageMap[articles[0].image] || articles[0].image} alt={articles[0].title} />
              </div>
              <h4 className="cat-box-title">{articles[0].title}</h4>
            </div>
            {/* List Articles */}
            <div className="cat-box-list">
              {articles.slice(1).map((art, i) => (
                <div key={i} className="cat-box-list-item" onClick={() => navigate('/article')} style={{ cursor: 'pointer' }}>
                  <h5>{art.title}</h5>
                  <p>{art.short_text}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );

    return (
      <section className="category-detailed-section">
        <div className="cat-split-row" style={{ marginBottom: 0 }}>
          {renderBox('정치', politics)}
          {renderBox('경제', economy)}
        </div>
      </section>
    );
  };

  /* Society Section (Full Width) */
  const renderSocietySection = () => {
    if (!displayArticles || displayArticles.length === 0) return null;
    const society = displayArticles.filter(a => a.category === '사회' || (Array.isArray(a.category) && a.category.includes('사회'))).slice(0, 3);

    return (
      <section className="category-detailed-section" style={{ borderTop: 'none', marginTop: '25px' }}>
        <div className="cat-global-row">
          <h3 className="cat-box-header" onClick={() => navigate('/society')} style={{ cursor: 'pointer' }}>사회</h3>
          <div className="global-grid">
            {society.map((art, i) => (
              <div key={i} className="global-card" onClick={() => navigate('/article')} style={{ cursor: 'pointer' }}>
                <div className="global-img">
                  <img src={imageMap[art.image] || art.image} alt={art.title} />
                </div>
                <h4>{art.title}</h4>
              </div>
            ))}
          </div>
        </div>
      </section>
    );
  };

  /* Living/Culture Section (Full Width, Duplicate of Society) */
  const renderLivingCultureSection = () => {
    if (!displayArticles || displayArticles.length === 0) return null;
    const livingCulture = displayArticles.filter(a => a.category === '생활/문화' || (Array.isArray(a.category) && a.category.includes('생활/문화'))).slice(0, 2);

    return (
      <section className="category-detailed-section" style={{ borderTop: 'none' }}>
        <div className="cat-global-row">
          <h3 className="cat-box-header" onClick={() => navigate('/living-culture')} style={{ cursor: 'pointer' }}>생활/문화</h3>
          <div className="global-grid" style={{ gridTemplateColumns: 'repeat(2, 1fr)' }}>
            {livingCulture.map((art, i) => (
              <div key={i} className="global-card" onClick={() => navigate('/article')} style={{ cursor: 'pointer' }}>
                <div className="global-img">
                  <img src={imageMap[art.image] || art.image} alt={art.title} />
                </div>
                <h4>{art.title}</h4>
              </div>
            ))}
          </div>
        </div>
      </section>
    );
  };

  /* Science Section (Below AI News) */
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

  const totalPages = 5; // Fixed to 5 pages as requested for the loop

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
          {/* Left Column (70%) */}
          <div className="main-left-col">
            {/* Repeat the main content 5 times, offset by current page */}
            {displayArticles.length > 0 ? (
              <React.Fragment>
                {renderMainContent(0 + (currentPage - 1) * 4)}
                {renderPoliticsEconomy()}
              </React.Fragment>
            ) : (
              <div className="empty-category">
                <p>해당 카테고리에 표시할 기사가 없습니다.</p>
              </div>
            )}
          </div>

          <div className="vertical-divider"></div>

          {/* Right Column (30%) */}
          <div className="main-right-col">
            {renderTop10News()}
          </div>
        </div>

        <div className="full-width-divider"></div>
        {renderSocietySection()}
        <div className="full-width-divider"></div>
        {renderLivingCultureSection()}

        {renderAIRecommendedNews(0 + (currentPage - 1) * 4)}

        <div className="full-width-divider"></div>
        {renderScienceSection()}

      </main>
    </div>
  );
};


