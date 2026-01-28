import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import axios from 'axios';
import Header from '../components/Header';
import Logo from '../components/Logo';
import logoImg from '../components/Logo.png';
import Searchbar from '../components/Searchbar';
import UserMenu from '../components/UserMenu';
import './LivingCulturePage.css';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const LivingCulturePage = () => {
    const name = '생활/문화';
    const navigate = useNavigate();
    const location = useLocation();
    const [currentPage, setCurrentPage] = useState(1);
    const [displayArticles, setDisplayArticles] = useState([]);
    const [imageMap, setImageMap] = useState({});
    const [feedPage, setFeedPage] = useState(1);
    const [isMobile, setIsMobile] = useState(window.innerWidth <= 768);

    useEffect(() => {
        const handleResize = () => {
            setIsMobile(window.innerWidth <= 768);
        };
        window.addEventListener('resize', handleResize);
        return () => window.removeEventListener('resize', handleResize);
    }, []);

    useEffect(() => {
        setCurrentPage(1);
        setFeedPage(1);

        const loadData = async () => {
            try {
                // 1. Fetch AI Generated News
                const response = await axios.get(`${API_BASE_URL}/generated-news?limit=100`);
                const realArticles = response.data;

                // 2. Map Backend Data to Frontend Structure
                const formattedArticles = realArticles.map(art => ({
                    ...art,
                    id: art.ai_generated_news_id, // [Fix] Map native ID to 'id'
                    category: art.category_name,
                    image: `cluster_${art.cluster_id}`,
                    short_text: art.contents ? (art.contents.substring(0, 100) + "...") : "내용 없음"
                }));

                // 3. Filter by category
                const filtered = formattedArticles.filter(a => {
                    if (!a.category) return false;
                    return a.category === name;
                });

                if (filtered.length > 0) {
                    let expanded = [...filtered];
                    // Ensure at least 24 items for LivingCulturePage layout
                    while (expanded.length < 24) {
                        expanded = [...expanded, ...filtered];
                    }
                    // Shuffle and slice to exactly 24
                    const shuffled = expanded.sort(() => Math.random() - 0.5).slice(0, 24);
                    setDisplayArticles(shuffled);

                    // 4. Fetch Images
                    const uniqueClusters = [...new Set(filtered.map(a => a.cluster_id))];
                    const newImageMap = {};

                    await Promise.allSettled(uniqueClusters.map(async (clusterId) => {
                        try {
                            const imgRes = await axios.get(`${API_BASE_URL}/generated-news/clusters/${clusterId}/news`);
                            const newsList = imgRes.data;
                            const allImgUrls = newsList.flatMap(news => news.img_urls ?? []).filter(Boolean);

                            if (allImgUrls.length > 0) {
                                const randomImg = allImgUrls[Math.floor(Math.random() * allImgUrls.length)];
                                newImageMap[`cluster_${clusterId}`] = randomImg;
                            }
                        } catch (err) {
                            console.warn(`Failed to fetch image for cluster ${clusterId}`, err);
                        }
                    }));

                    setImageMap(prev => ({ ...prev, ...newImageMap }));
                } else {
                    setDisplayArticles([]);
                }
            } catch (error) {
                console.error('Failed to load real data:', error);
                setDisplayArticles([]);
                setImageMap({});
            }
        };

        loadData();
    }, []);

    // 1 Main + 3 Grid + 20 Feed = 24 items total
    const articlesPerBlock = 24;
    const blocksPerPage = 1;
    const articlesPerPage = articlesPerBlock * blocksPerPage;

    const renderMainContent = (blockArticles, blockIndex) => {
        if (!blockArticles || blockArticles.length === 0) return null;

        const mainArticle = blockArticles[0];
        const gridArticles = blockArticles.slice(1, 4); // 3 items (1 to 3)
        // List removed

        // Feed Logic
        const allFeedArticles = blockArticles; // Show ALL articles in Feed // 20 items (4 to 23)
        const feedPageSize = 5;
        const totalFeedPages = Math.ceil(allFeedArticles.length / feedPageSize);
        const currentFeedArticles = allFeedArticles.slice((feedPage - 1) * feedPageSize, feedPage * feedPageSize);

        const mainData = {
            id: mainArticle?.id,
            title: mainArticle?.title || "News Title Text Sample",
            description: mainArticle?.short_text || "text sample...",
            image: mainArticle ? (imageMap[mainArticle.image] || mainArticle.image) : null
        };



        const grid = gridArticles.map((art, i) => ({
            id: art?.id,
            title: art?.title || "Title Sample Text",
            content: art?.short_text || "text sample...",
            image: art ? (imageMap[art.image] || art.image) : null
        }));



        const feed = currentFeedArticles.map((art, i) => ({
            id: art?.id,
            title: art?.title || "Title Sample Text",
            content: art?.short_text || "text sample...",
            image: art ? (imageMap[art.image] || art.image) : null
        }));

        return (
            <React.Fragment key={blockIndex}>


                <div style={{ padding: isMobile ? '0 20px' : '0 40px' }}>
                    {/* Main Article Section */}
                    <section className="main-article-section" style={{ marginBottom: isMobile ? '30px' : '50px', position: 'relative' }}>
                        <div className="main-image" style={{ width: '100%', aspectRatio: isMobile ? '1.5/1' : '2.5/1', position: 'relative', overflow: 'hidden', borderRadius: '4px' }}>
                            <img src={mainData.image} alt={mainData.title} style={{ width: '100%', height: '100%', objectFit: 'cover' }} onLoad={(e) => { if (!e.target.src.includes(logoImg)) e.target.style.objectFit = 'cover'; }} onError={(e) => { e.target.onerror = null; e.target.src = logoImg; e.target.style.objectFit = 'contain'; }} />
                            <div style={{
                                position: 'absolute',
                                bottom: 0,
                                left: 0,
                                right: 0,
                                background: 'linear-gradient(to top, rgba(0,0,0,0.8), transparent)',
                                padding: isMobile ? '20px' : '30px',
                                textAlign: 'left'
                            }}>
                                <h2 style={{ fontSize: isMobile ? '24px' : '32px', fontWeight: 'bold', color: '#fff', margin: '0 0 10px 0' }}>{mainData.title}</h2>
                                {!isMobile && <p style={{ fontSize: '16px', color: '#ddd', margin: 0, maxWidth: '80%' }}>{mainData.description}</p>}
                            </div>
                        </div>
                    </section>
                    <div className="section-divider"></div>

                    {/* Grid Section (3 items, Vertical Portrait, Title Overlay) */}
                    {grid.length > 0 && (
                        <>
                            <section className="bottom-grid-section" style={{ display: 'grid', gridTemplateColumns: isMobile ? '1fr' : 'repeat(3, 1fr)', gap: isMobile ? '20px' : '40px', marginBottom: '50px', textAlign: 'left' }}>
                                {grid.map((news) => (
                                    <div key={news.id} className="grid-item" onClick={() => navigate(`/article/${news.id}`)} style={{ cursor: 'pointer', position: 'relative', overflow: 'hidden', borderRadius: '4px' }}>
                                        {/* Image Container (Vertical Aspect Ratio 3:4) */}
                                        <div className="grid-image" style={{ width: '100%', aspectRatio: isMobile ? '2/1' : '3/4', position: 'relative', border: 'none' }}>
                                            <img src={news.image} alt={news.title} style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }} onLoad={(e) => { if (!e.target.src.includes(logoImg)) e.target.style.objectFit = 'cover'; }} onError={(e) => { e.target.onerror = null; e.target.src = logoImg; e.target.style.objectFit = 'contain'; }} />

                                            {/* Gradient Overlay */}
                                            <div style={{
                                                position: 'absolute',
                                                bottom: 0,
                                                left: 0,
                                                width: '100%',
                                                height: '60%',
                                                background: 'linear-gradient(to top, #000 0%, rgba(0,0,0,0) 100%)',
                                                pointerEvents: 'none',
                                                zIndex: 3
                                            }}></div>

                                            {/* Title Overlay */}
                                            <div style={{
                                                position: 'absolute',
                                                bottom: isMobile ? '15px' : '20px',
                                                left: isMobile ? '15px' : '20px',
                                                right: isMobile ? '15px' : '20px',
                                                zIndex: 4,
                                                textAlign: 'center'
                                            }}>
                                                <h3 style={{
                                                    fontSize: isMobile ? '20px' : '30px',
                                                    fontWeight: 'bold',
                                                    color: '#fff',
                                                    margin: 0,
                                                    lineHeight: '1.4',
                                                    textShadow: '0px 1px 3px rgba(0,0,0,0.5)'
                                                }}>
                                                    {news.title}
                                                </h3>
                                            </div>
                                        </div>
                                        {/* Description Hidden */}
                                    </div>
                                ))}
                            </section>
                        </>
                    )}
                </div>

                {/* Feed Section (Pagination) */}
                {feed.length > 0 && (
                    <>
                        <div className="section-divider"></div>
                        <section className="bottom-feed-section" style={{ display: 'flex', flexDirection: 'column', gap: '30px', textAlign: 'left', marginTop: '30px', padding: isMobile ? '0 20px' : '0 120px' }}>
                            {feed.map((news) => (
                                <div key={news.id} className="feed-item" onClick={() => navigate(`/article/${news.id}`)} style={{ cursor: 'pointer', display: 'flex', flexDirection: isMobile ? 'column-reverse' : 'row', justifyContent: 'space-between', alignItems: isMobile ? 'flex-start' : 'flex-start', borderBottom: '1px solid #eee', paddingBottom: '20px', gap: '20px' }}>

                                    {/* Left Container: Like + Text */}
                                    <div style={{ display: 'flex', flex: 1, paddingRight: isMobile ? '0' : '0px', width: '100%' }}>
                                        {/* Like Button (Display Only) */}
                                        {!isMobile &&
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
                                                    <path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 0 0 1-2-2v-7a2 0 0 1 2-2h3" />
                                                </svg>
                                                <span style={{ fontSize: '14px', fontWeight: '500' }}>{120 + news.id}</span>
                                            </div>
                                        }

                                        {/* Text Info */}
                                        <div className="feed-info">
                                            <h3 style={{ fontSize: isMobile ? '18px' : '20px', fontWeight: 'bold', margin: '0 0 12px 0', lineHeight: '1.3' }}>{news.title}</h3>
                                            <p style={{ fontSize: '15px', color: '#666', margin: 0, lineHeight: '1.6', display: '-webkit-box', WebkitLineClamp: 3, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                                                {news.content}
                                            </p>
                                        </div>
                                    </div>

                                    {/* Image Right (Reduced Height: aspect-ratio 1.8/1) */}
                                    <div className="feed-image" style={{ width: isMobile ? '100%' : '312px', aspectRatio: isMobile ? '1.8/1' : '1.8/1', flexShrink: 0, overflow: 'hidden', borderRadius: '4px' }}>
                                        <img src={news.image} alt={news.title} style={{ width: '100%', height: '100%', objectFit: 'cover' }} onLoad={(e) => { if (!e.target.src.includes(logoImg)) e.target.style.objectFit = 'cover'; }} onError={(e) => { e.target.onerror = null; e.target.src = logoImg; e.target.style.objectFit = 'contain'; }} />
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

export default LivingCulturePage;
