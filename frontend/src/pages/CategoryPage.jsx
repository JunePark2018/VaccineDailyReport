import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import Logo from '../components/Logo';
import Searchbar from '../components/Searchbar';
import UserMenu from '../components/UserMenu';
import './CategoryPage.css';

const CategoryPage = () => {
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
    const renderMainContent = (index) => {
        if (!displayArticles || displayArticles.length === 0) return null;

        // Use 4 articles per loop to match the new layout (1 main + 3 grid)
        const baseIndex = (index * 4) % displayArticles.length;
        
        const mainArticle = displayArticles[baseIndex];
        const gridArticles = [
            displayArticles[(baseIndex + 1) % displayArticles.length],
            displayArticles[(baseIndex + 2) % displayArticles.length],
            displayArticles[(baseIndex + 3) % displayArticles.length],
        ];

        const mainData = {
            title: mainArticle?.title || "News Title Text Sample",
            description: mainArticle?.short_text || "text sample text sample text sample text sample text sample text sample text sample text sample text sample text sample text sample text sample text sample text sample text sample text sample text sample text sample text sample text sample text sample text sample text sample",
            image: mainArticle ? (imageMap[mainArticle.image] || mainArticle.image) : null
        };

        const grid = gridArticles.map((art, i) => ({
            id: i,
            title: art?.title || "Title Sample Text",
            image: art ? (imageMap[art.image] || art.image) : null
        }));

        const highlights = [
            { keyword: '중점으로 둔 키워드', content: '"해당 키워드에 대한 요약한 내용"' },
            { keyword: '중점으로 둔 키워드', content: '"해당 키워드에 대한 요약한 내용"' },
            { keyword: '중점으로 둔 키워드', content: '"해당 키워드에 대한 요약한 내용"' },
            { keyword: '중점으로 둔 키워드', content: '"해당 키워드에 대한 요약한 내용"' }
        ];

        return (
            <React.Fragment key={index}>
                {/* Main 3-Column Section */}
                <section className="main-article-section">
                    <div className="article-info-side" onClick={() => navigate('/article')} style={{ cursor: 'pointer' }}>
                        <h2>{mainData.title}</h2>
                        <h3>"TEXT SAMPLE"</h3>
                        <p>{mainData.description}</p>
                        <div className="analysis-box-large">
                            <div className="analysis-placeholder">
                                <div className="analysis-x"></div>
                                <span className="analysis-text">분석</span>
                            </div>
                        </div>
                    </div>
                    
                    <div className="article-image-center" onClick={() => navigate('/article')} style={{ cursor: 'pointer' }}>
                        <img src={mainData.image} alt="Main" />
                        <div className="image-placeholder-text">IMAGE</div>
                    </div>
                    
                    <div className="highlights-side">
                        {highlights.map((item, hIndex) => (
                            <div key={hIndex} className="highlight-item">
                                <span className="highlight-keyword">{item.keyword}</span>
                                <span className="highlight-content">{item.content}</span>
                            </div>
                        ))}
                    </div>
                </section>

                <div className="section-divider"></div>

                {/* Grid Section (3 items) */}
                <section className="bottom-grid-section">
                    {grid.map((news) => (
                        <div key={news.id} className="grid-item" onClick={() => navigate('/article')} style={{ cursor: 'pointer' }}>
                            <div className="grid-image">
                                <img src={news.image} alt={news.title} />
                                <div className="image-placeholder-text">IMAGE</div>
                                <div className="grid-title-overlay">
                                    <h3>{news.title}</h3>
                                </div>
                            </div>
                        </div>
                    ))}
                </section>

                <div className="divider"></div>
            </React.Fragment>
        );
    };

    const renderAIRecommendedNews = () => {
        if (!displayArticles || displayArticles.length < 2) return null;

        // Pick two articles for AI recommendation
        const aiArticles = [
            displayArticles[displayArticles.length % displayArticles.length],
            displayArticles[(displayArticles.length + 1) % displayArticles.length]
        ];

        return (
            <section className="ai-recommended-section">
                <h3>AI 추천 뉴스</h3>
                <div className="ai-articles-container">
                    {aiArticles.map((art, i) => (
                        <div key={i} className="ai-article-item" onClick={() => navigate('/article')} style={{ cursor: 'pointer' }}>
                            <div className="ai-article-text">
                                <h4>{art?.title || "Title Text Sample"}</h4>
                                <p>{art?.short_text || "TEXT SAMPLE"}</p>
                            </div>
                            <div className="ai-article-image">
                                <img src={art ? (imageMap[art.image] || art.image) : null} alt="AI Recommended" />
                                <div className="image-placeholder-text" style={{ fontSize: '12px' }}>IMAGE</div>
                            </div>
                        </div>
                    ))}
                </div>
            </section>
        );
    };

    const totalPages = 5; // Fixed to 5 pages as requested for the loop

    return (
        <div className="category-page">
            <Header
                leftChild={<Logo />}
                midChild={<Searchbar />}
                rightChild={<UserMenu />}
                headerTop="on"
                headerMain="on"
                headerBottom="on"
            />
            
            <main className="category-content">
                <div className="category-header">
                    <h1>{decodeURIComponent(name || '경제')}</h1>
                </div>

                {/* Repeat the main content 5 times, offset by current page */}
                {displayArticles.length > 0 ? (
                    [...Array(5)].map((_, i) => renderMainContent(i + (currentPage - 1) * 5))
                ) : (
                    <div className="empty-category">
                        <p>해당 카테고리에 표시할 기사가 없습니다.</p>
                    </div>
                )}

                {renderAIRecommendedNews()}

                {/* Pagination */}
                <div className="pagination">
                    <span 
                        onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                        style={{ cursor: 'pointer' }}
                    >
                        {"<"}
                    </span>
                    {[...Array(totalPages)].map((_, i) => (
                        <React.Fragment key={i + 1}>
                            <span 
                                className={`page-num ${currentPage === i + 1 ? 'active' : ''}`}
                                onClick={() => setCurrentPage(i + 1)}
                            >
                                {i + 1}
                            </span>
                            {i < totalPages - 1 && <span className="separator">|</span>}
                        </React.Fragment>
                    ))}
                    <span 
                        onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
                        style={{ cursor: 'pointer' }}
                    >
                        {">"}
                    </span>
                </div>
            </main>
        </div>
    );
};

export default CategoryPage;
