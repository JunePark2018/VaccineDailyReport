import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import Header from '../components/Header';
import Logo from '../components/Logo';
import Searchbar from '../components/Searchbar';
import UserMenu from '../components/UserMenu';
import './TotalMenuPage.css';

const TotalMenuPage = () => {
    const name = '전체메뉴';
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

                // For '전체메뉴', show all articles
                const filtered = articles;

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

    const articlesPerBlock = 5;
    const blocksPerPage = 1;
    const articlesPerPage = articlesPerBlock * blocksPerPage;

    const renderMainContent = (blockArticles, blockIndex) => {
        if (!blockArticles || blockArticles.length === 0) return null;

        const mainArticle = blockArticles[0];
        const gridArticles = blockArticles.slice(1, 5);

        const mainData = {
            title: mainArticle?.title || "News Title Text Sample",
            description: mainArticle?.short_text || "text sample...",
            image: mainArticle ? (imageMap[mainArticle.image] || mainArticle.image) : null
        };

        const grid = gridArticles.map((art, i) => ({
            id: i,
            title: art?.title || "Title Sample Text",
            content: art?.short_text || "text sample...",
            image: art ? (imageMap[art.image] || art.image) : null
        }));

        return (
            <React.Fragment key={blockIndex}>
                <section className="main-article-section">
                    {/* Left: Article Title */}
                    <div className="politics-title-side" onClick={() => navigate('/article')}>
                        <h2>
                            {mainData.title}
                        </h2>
                        <p>
                            {mainData.description}
                        </p>
                    </div>

                    {/* Right: Article Photo */}
                    <div className="politics-image-side" onClick={() => navigate('/article')}>
                        <div className="article-image-center">
                            <img src={mainData.image} alt="Main" />
                        </div>
                    </div>
                </section>
                <div className="section-divider"></div>

                {grid.length > 0 && (
                    <>
                        <section className="bottom-grid-section">
                            {grid.map((news) => (
                                <div key={news.id} className="grid-item" onClick={() => navigate('/article')}>
                                    <div className="grid-image">
                                        <img src={news.image} alt={news.title} />
                                    </div>
                                    <div className="grid-info">
                                        <h3>{news.title}</h3>
                                        <p>
                                            {news.content}
                                        </p>
                                    </div>
                                </div>
                            ))}
                        </section>
                    </>
                )}
            </React.Fragment>
        );
    };

    const totalPages = Math.max(1, Math.ceil(displayArticles.length / articlesPerPage));

    // Group articles for current page
    const startIndex = (currentPage - 1) * articlesPerPage;
    const pageArticles = displayArticles.slice(startIndex, startIndex + articlesPerPage);
    const articleBlocks = [];
    for (let i = 0; i < pageArticles.length; i += articlesPerBlock) {
        articleBlocks.push(pageArticles.slice(i, i + articlesPerBlock));
    }

    return (
        <div className="category-page total-menu-page">
            <Header
                leftChild={null}
                midChild={<Logo />}
                rightChild={
                    <div className="header-right-group">
                        <div className="header-search-wrapper">
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
                <div className="category-header">
                    <h1>{name}</h1>
                </div>

                {articleBlocks.length > 0 ? (
                    articleBlocks.map((block, i) => renderMainContent(block, i))
                ) : (
                    <div className="empty-category">
                        <p>해당 카테고리에 표시할 기사가 없습니다.</p>
                    </div>
                )}

                <div className="pagination">
                    <span onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))} className="pagination-arrow">{"<"}</span>
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
                    <span onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))} className="pagination-arrow">{">"}</span>
                </div>
            </main>
        </div>
    );
};

export default TotalMenuPage;
