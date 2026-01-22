import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import Header from '../components/Header';
import Logo from '../components/Logo';
import Searchbar from '../components/Searchbar';
import UserMenu from '../components/UserMenu';
import './SciencePage.css';

const SciencePage = () => {
    const name = 'IT/과학';
    const navigate = useNavigate();
    const location = useLocation();
    const [currentPage, setCurrentPage] = useState(1);
    const [displayArticles, setDisplayArticles] = useState([]);
    const [imageMap, setImageMap] = useState({});
    const [feedPage, setFeedPage] = useState(1);

    useEffect(() => {
        setCurrentPage(1);
        setFeedPage(1);

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
                    let expanded = [...filtered];
                    // Ensure at least 31 items (11 static + 20 feed) for testing
                    while (expanded.length < 31) {
                        expanded = [...expanded, ...filtered];
                    }
                    // Shuffle and slice to exactly 31 for this test
                    const shuffled = expanded.sort(() => Math.random() - 0.5).slice(0, 31);
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

    // 11 fixed + 20 feed items (4 pages * 5) = 31 items total
    const articlesPerBlock = 31;
    const blocksPerPage = 1;
    const articlesPerPage = articlesPerBlock * blocksPerPage;

    const renderMainContent = (blockArticles, blockIndex) => {
        if (!blockArticles || blockArticles.length === 0) return null;

        const mainArticle = blockArticles[0];
        const gridArticles = blockArticles.slice(1, 3);
        const listArticles = blockArticles.slice(3, 11);

        // Feed Logic
        const allFeedArticles = blockArticles.slice(11);
        const feedPageSize = 5;
        const totalFeedPages = Math.ceil(allFeedArticles.length / feedPageSize);
        const currentFeedArticles = allFeedArticles.slice((feedPage - 1) * feedPageSize, feedPage * feedPageSize);

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

        const list = listArticles.map((art, i) => ({
            id: i,
            title: art?.title || "Title Sample Text",
            content: art?.short_text || "text sample...",
            image: art ? (imageMap[art.image] || art.image) : null
        }));

        const feed = currentFeedArticles.map((art, i) => ({
            id: i,
            title: art?.title || "Title Sample Text",
            content: art?.short_text || "text sample...",
            image: art ? (imageMap[art.image] || art.image) : null
        }));

        return (
            <React.Fragment key={blockIndex}>
                <section className="main-article-section" style={{ display: 'flex', alignItems: 'center', gap: '40px', marginBottom: '30px', minHeight: '300px', textAlign: 'left' }}>

                    {/* Left: Article Title */}
                    <div className="politics-title-side" onClick={() => navigate('/article')} style={{ flex: 1.47, cursor: 'pointer' }}>
                        <h2 style={{ fontSize: '36px', fontWeight: 'bold', lineHeight: '1.3', color: '#000', margin: 0 }}>
                            {mainData.title}
                        </h2>
                        <p style={{ fontSize: '16px', color: '#666', marginTop: '15px', lineHeight: '1.6' }}>
                            {mainData.description}
                        </p>
                    </div>

                    {/* Right: Article Photo */}
                    <div className="politics-image-side" onClick={() => navigate('/article')} style={{ flex: 1.53, cursor: 'pointer' }}>
                        <div className="article-image-center" style={{ width: '100%', aspectRatio: '2.4 / 1', borderRadius: '1px' }}>
                            <img src={mainData.image} alt="Main" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                        </div>
                    </div>
                </section>
                <div className="section-divider"></div>

                {/* Grid Section (2 items) */}
                {grid.length > 0 && (
                    <>
                        <section className="bottom-grid-section" style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '40px', marginBottom: '50px', textAlign: 'left' }}>
                            {grid.map((news) => (
                                <div key={news.id} className="grid-item" onClick={() => navigate('/article')} style={{ cursor: 'pointer', display: 'flex', flexDirection: 'column', gap: '10px' }}>
                                    <div className="grid-image" style={{ width: '100%', aspectRatio: '1.5/1', border: '1px solid #eee', position: 'relative', overflow: 'hidden' }}>
                                        <img src={news.image} alt={news.title} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                                    </div>
                                    <div className="grid-info">
                                        <h3 style={{ fontSize: '16px', fontWeight: 'bold', margin: '0 0 5px 0', lineHeight: '1.4' }}>{news.title}</h3>
                                        <p style={{ fontSize: '13px', color: '#666', margin: 0, lineHeight: '1.4', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                                            {news.content}
                                        </p>
                                    </div>
                                </div>
                            ))}
                        </section>
                    </>
                )}

                {/* List Section (8 items, 2 cols x 4 rows) */}
                {list.length > 0 && (
                    <>
                        <div className="section-divider"></div>
                        <section className="bottom-list-section" style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', columnGap: '40px', rowGap: '30px', textAlign: 'left' }}>
                            {list.map((news) => (
                                <div key={news.id} className="list-item" onClick={() => navigate('/article')} style={{ cursor: 'pointer', display: 'flex', gap: '20px', alignItems: 'flex-start' }}>
                                    <div className="list-image" style={{ width: '120px', height: '76px', flexShrink: 0, border: '1px solid #eee', overflow: 'hidden' }}>
                                        <img src={news.image} alt={news.title} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                                    </div>
                                    <div className="list-info" style={{ flex: 1 }}>
                                        <h3 style={{ fontSize: '16px', fontWeight: 'bold', margin: '0 0 8px 0', lineHeight: '1.3' }}>{news.title}</h3>
                                        <p style={{ fontSize: '13px', color: '#666', margin: 0, lineHeight: '1.4', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                                            {news.content}
                                        </p>
                                    </div>
                                </div>
                            ))}
                        </section>
                    </>
                )}

                {/* Feed Section (Pagination) */}
                {feed.length > 0 && (
                    <>
                        <div className="section-divider"></div>
                        <section className="bottom-feed-section" style={{ display: 'flex', flexDirection: 'column', gap: '30px', textAlign: 'left', marginTop: '30px', padding: '0 120px' }}>
                            {feed.map((news) => (
                                <div key={news.id} className="feed-item" onClick={() => navigate('/article')} style={{ cursor: 'pointer', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', borderBottom: '1px solid #eee', paddingBottom: '20px' }}>

                                    {/* Left Container: Like + Text */}
                                    <div style={{ display: 'flex', flex: 1, paddingRight: '0px' }}>
                                        {/* Like Button (Display Only) */}
                                        <div className="like-icon" style={{
                                            marginRight: '50px',
                                            paddingRight: '15px',
                                            borderRight: '1px solid #ddd',
                                            marginTop: '5px',
                                            display: 'flex',
                                            flexDirection: 'row', // Horizontal
                                            alignItems: 'center',
                                            justifyContent: 'center', // Center content in fixed width
                                            color: '#999',
                                            minWidth: '100px', // Reserve space for 6 digits
                                            gap: '8px' // Gap between icon and number
                                        }}>
                                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                                <path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3" />
                                            </svg>
                                            <span style={{ fontSize: '14px', fontWeight: '500' }}>{120 + news.id}</span>
                                        </div>

                                        {/* Text Info */}
                                        <div className="feed-info">
                                            <h3 style={{ fontSize: '20px', fontWeight: 'bold', margin: '0 0 12px 0', lineHeight: '1.3' }}>{news.title}</h3>
                                            <p style={{ fontSize: '15px', color: '#666', margin: 0, lineHeight: '1.6', display: '-webkit-box', WebkitLineClamp: 3, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                                                {news.content}
                                            </p>
                                        </div>
                                    </div>

                                    {/* Image Right (Reduced Height: aspect-ratio 1.8/1) */}
                                    <div className="feed-image" style={{ width: '312px', aspectRatio: '1.8/1', flexShrink: 0, overflow: 'hidden', borderRadius: '4px', marginLeft: '-20px' }}>
                                        <img src={news.image} alt={news.title} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                                    </div>
                                </div>
                            ))}
                        </section>

                        {/* Pagination Numbers (Box Style) */}
                        {totalFeedPages > 1 && (
                            <div style={{ textAlign: 'center', marginTop: '40px', marginBottom: '100px', display: 'flex', justifyContent: 'center', gap: '10px' }}>
                                {Array.from({ length: totalFeedPages }, (_, i) => i + 1).map((pageNum) => (
                                    <button
                                        key={pageNum}
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            setFeedPage(pageNum);
                                        }}
                                        style={{
                                            width: '36px',
                                            height: '36px',
                                            display: 'flex',
                                            justifyContent: 'center',
                                            alignItems: 'center',
                                            fontSize: '14px',
                                            border: feedPage === pageNum ? '1px solid #333' : '1px solid #eee',
                                            backgroundColor: feedPage === pageNum ? '#333' : '#fff',
                                            color: feedPage === pageNum ? '#fff' : '#666',
                                            cursor: 'pointer',
                                            fontWeight: feedPage === pageNum ? 'bold' : 'normal',
                                            borderRadius: '0px'
                                        }}
                                    >
                                        {pageNum}
                                    </button>
                                ))}
                            </div>
                        )}
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

                {articleBlocks.length > 0 ? (
                    articleBlocks.map((block, i) => renderMainContent(block, i))
                ) : (
                    <div className="empty-category">
                        <p>해당 카테고리에 표시할 기사가 없습니다.</p>
                    </div>
                )}

                {/* Pagination Removed */}
            </main>
        </div>
    );
};

export default SciencePage;
