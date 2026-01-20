import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import Header from '../components/Header';
import Logo from '../components/Logo';
import Searchbar from '../components/Searchbar';
import UserMenu from '../components/UserMenu';
import './PoliticsPage.css';

const PoliticsPage = () => {
    const name = '정치';
    const navigate = useNavigate();
    const location = useLocation();
    const [currentPage, setCurrentPage] = useState(1);
    const [displayArticles, setDisplayArticles] = useState([]);
    const [imageMap, setImageMap] = useState({});

    useEffect(() => {
        setCurrentPage(1);

        const loadData = async () => {
            try {
                const [articlesModule, imagesModule] = await Promise.all([
                    import('../sample_/sampleArticle.json').catch(() => ({ default: [] })),
                    import('../sample_/imageAssets').catch(() => ({ default: {} }))
                ]);

                const articles = articlesModule.default || [];
                const images = imagesModule.default || {};
                setImageMap(images);

                const filtered = articles.filter(a => {
                    if (!a.category) return false;
                    if (Array.isArray(a.category)) {
                        return a.category.includes(name);
                    }
                    return a.category === name;
                });

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
    }, []);

    const renderMainContent = (index) => {
        if (!displayArticles || displayArticles.length === 0) return null;
        const baseIndex = (index * 4) % displayArticles.length;
        const mainArticle = displayArticles[baseIndex];
        const gridArticles = [
            displayArticles[(baseIndex + 1) % displayArticles.length],
            displayArticles[(baseIndex + 2) % displayArticles.length],
            displayArticles[(baseIndex + 3) % displayArticles.length],
        ];

        const mainData = {
            title: mainArticle?.title || "News Title Text Sample",
            description: mainArticle?.short_text || "text sample...",
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
                <section className="main-article-section">
                    <div className="article-info-side" onClick={() => navigate('/article')} style={{ cursor: 'pointer' }}>
                        <div className="analysis-box-large">
                            <div className="analysis-placeholder">
                                <div className="analysis-x"></div>
                                <span className="analysis-text">분석</span>
                            </div>
                        </div>
                    </div>

                    <div className="article-image-center" onClick={() => navigate('/article')} style={{ cursor: 'pointer' }}>
                        <img src={mainData.image} alt="Main" />
                        <div className="main-image-text">
                            <h3>{mainData.title}</h3>
                            <p>{mainData.description}</p>
                        </div>
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




    const totalPages = 5;

    return (
        <div className="category-page">
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
                <div className="category-header">
                    <h1>{name}</h1>
                </div>

                {displayArticles.length > 0 ? (
                    [...Array(5)].map((_, i) => renderMainContent(i + (currentPage - 1) * 5))
                ) : (
                    <div className="empty-category">
                        <p>해당 카테고리에 표시할 기사가 없습니다.</p>
                    </div>
                )}




                <div className="pagination">
                    <span onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))} style={{ cursor: 'pointer' }}>{"<"}</span>
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
                    <span onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))} style={{ cursor: 'pointer' }}>{">"}</span>
                </div>
            </main>
        </div>
    );
};

export default PoliticsPage;
