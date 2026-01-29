import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import Header from '../components/Header';
import Logo from '../components/Logo';
import logoImg from '../components/Logo.png';
import Searchbar from '../components/Searchbar';
import UserMenu from '../components/UserMenu';
import './PoliticsPage.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const PoliticsPage = () => {
    const name = '정치';
    const navigate = useNavigate();
    const [currentPage, setCurrentPage] = useState(1);
    const [displayArticles, setDisplayArticles] = useState([]);
    const [imageMap, setImageMap] = useState({});
    const [feedPage, setFeedPage] = useState(1);
    const [topFocusIndex, setTopFocusIndex] = useState(0); // State for slideshow focus

    useEffect(() => {
        setCurrentPage(1);
        setFeedPage(1);

        const loadData = async () => {
            try {
                // 1. Fetch AI Generated News (Limit 100 to ensure coverage)
                const response = await axios.get(`${API_BASE_URL}/generated-news?limit=100`);
                const realArticles = response.data;

                // 2. Map Backend Data to Frontend Structure
                const formattedArticles = realArticles.map(art => ({
                    ...art,
                    id: art.ai_generated_news_id, // [Fix] Map native ID to 'id'
                    category: art.category_name, // Map category_name to category
                    image: `cluster_${art.cluster_id}`, // Placeholder ID for image map
                    short_text: art.contents ? (art.contents.substring(0, 100) + "...") : "내용 없음"
                }));

                // 3. Filter by category
                const filtered = formattedArticles.filter(a => {
                    if (!a.category) return false;
                    return a.category === name;
                });

                if (filtered.length > 0) {
                    let expanded = [...filtered];
                    // Ensure at least 33 items (1 Main + 4 Grid + 8 List + 20 Feed) for testing layout
                    // If real data is too small, duplicate it to fill the layout
                    while (expanded.length < 33) {
                        expanded = [...expanded, ...filtered];
                    }
                    // Shuffle and slice to exactly 33
                    const shuffled = expanded.sort(() => Math.random() - 0.5).slice(0, 33);
                    setDisplayArticles(shuffled);

                    // 4. Fetch Images for the filtered set (N+1 pattern)
                    // Only need to fetch for unique cluster IDs in the filtered set
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

    // 1 Main + 4 Grid + 8 List + 20 Feed items (4 pages * 5) = 33 items total
    const articlesPerBlock = 33;
    const blocksPerPage = 1;
    const articlesPerPage = articlesPerBlock * blocksPerPage;

    const renderMainContent = (blockArticles, blockIndex) => {
        if (!blockArticles || blockArticles.length === 0) return null;

        const slideArticles = blockArticles.slice(0, 4); // Top 4 for Slideshow

        // Ensure Grid articles DO NOT duplicate any Slide articles
        const slideIds = new Set(slideArticles.map(a => a.id));
        const remainingArticles = blockArticles.slice(4).filter(art => !slideIds.has(art.id));

        const gridArticles = remainingArticles.slice(0, 4); // Next 4 for Grid
        const listArticles = remainingArticles.slice(4, 12); // Next 8 for List

        // Feed Logic
        const allFeedArticles = blockArticles; // Show ALL articles in Feed
        const feedPageSize = 5;
        const totalFeedPages = Math.ceil(allFeedArticles.length / 5);
        const currentFeedArticles = allFeedArticles.slice((feedPage - 1) * 5, feedPage * 5);

        // Slideshow Data Preparation
        const slideData = slideArticles.map((art, i) => ({
            id: art?.id,
            title: art?.title || "뉴스 제목 예시",
            description: art?.short_text || "내용 예시...",
            image: art ? (imageMap[art.image] || art.image) : null
        }));

        const activeSlide = slideData[topFocusIndex] || slideData[0];

        const grid = gridArticles.map((art, i) => ({
            id: art?.id,
            title: art?.title || "제목 예시",
            content: art?.short_text || "내용 예시...",
            image: art ? (imageMap[art.image] || art.image) : null,
            // Simple grid item without related links for now, as user requested "layout" primarily. 
            // If related links are needed, we need more data slices.
        }));



        const list = listArticles.map((art, i) => ({
            id: art?.id,
            title: art?.title || "제목 예시",
            content: art?.short_text || "내용 예시...",
            image: art ? (imageMap[art.image] || art.image) : null
        }));

        const feed = currentFeedArticles.map((art, i) => ({
            id: art?.id,
            title: art?.title || "제목 예시",
            content: art?.short_text || "내용 예시...",
            image: art ? (imageMap[art.image] || art.image) : null
        }));

        return (
            <React.Fragment key={blockIndex}>
                <section className="politics-main-section" style={{ display: 'flex', gap: '40px', marginBottom: '30px', alignItems: 'flex-start', textAlign: 'left', minHeight: '350px' }}>

                    {/* Left Column: Interactive List (4 Items) */}
                    <div className="politics-content-side" style={{ flex: 1.4, display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                        {slideData.slice(0, 4).map((item, idx) => {
                            const isActive = idx === topFocusIndex;
                            return (
                                <div
                                    key={idx}
                                    className={`politics-slide-item ${isActive ? 'active' : ''}`}
                                    onClick={() => setTopFocusIndex(idx)}
                                    style={{
                                        cursor: 'pointer',
                                        padding: '15px 0',
                                        borderBottom: idx < 3 ? '1px solid #eee' : 'none',
                                        backgroundColor: isActive ? '#f9f9f9' : 'transparent', // Highlight active
                                        paddingLeft: isActive ? '10px' : '0', // Indent active
                                        transition: 'all 0.2s ease'
                                    }}
                                >
                                    <h2 style={{
                                        fontSize: isActive ? '20px' : '18px',
                                        fontWeight: isActive ? 'bold' : 'normal',
                                        lineHeight: '1.3',
                                        color: isActive ? '#000' : '#444',
                                        margin: '0 0 5px 0'
                                    }}>
                                        {item.title}
                                    </h2>
                                    {isActive && (
                                        <p style={{ fontSize: '14px', color: '#666', lineHeight: '1.5', margin: 0, display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                                            {item.description}
                                        </p>
                                    )}
                                </div>
                            );
                        })}

                        {/* Divider */}
                        <div style={{ width: '100%', height: '1px', backgroundColor: '#333', marginTop: '10px' }}></div>
                    </div>

                    {/* Right Column: Active Image Display */}
                    <div className="politics-image-side" onClick={() => activeSlide && navigate(`/article/${activeSlide.id}`)} style={{ flex: 1.6, cursor: 'pointer' }}>
                        <div className="article-image-center" style={{ width: '100%', aspectRatio: '16/9', borderRadius: '1px', overflow: 'hidden', position: 'relative' }}>
                            <img src={activeSlide?.image} alt="Main" style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                                onLoad={(e) => { if (!e.target.src.includes(logoImg)) e.target.style.objectFit = 'cover'; }}
                                onError={(e) => { e.target.onerror = null; e.target.src = logoImg; e.target.style.objectFit = 'contain'; }} />

                            {/* Optional Overlay Title on Image if desired, but user just asked for interaction */}
                        </div>
                    </div>

                </section>




                <div className="section-divider"></div>

                {/* Grid Section (4 items) */}
                {grid.length > 0 && (
                    <section className="bottom-grid-section" style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '20px', marginBottom: '50px', textAlign: 'left' }}>
                        {grid.map((news, i) => (
                            <div key={i} className="grid-item" onClick={() => navigate(`/article/${news.id}`)} style={{ cursor: 'pointer', display: 'flex', flexDirection: 'column', gap: '10px' }}>
                                <div className="grid-image" style={{ width: '100%', aspectRatio: '1.5/1', border: '1px solid #eee', position: 'relative', overflow: 'hidden' }}>
                                    <img src={news.image} alt={news.title} style={{ width: '100%', height: '100%', objectFit: 'cover' }} onLoad={(e) => { if (!e.target.src.includes(logoImg)) e.target.style.objectFit = 'cover'; }} onError={(e) => { e.target.onerror = null; e.target.src = logoImg; e.target.style.objectFit = 'contain'; }} />
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
                )}

                {/* Feed Section (Pagination) */}
                {feed.length > 0 && (
                    <>
                        <div className="section-divider"></div>
                        <section className="bottom-feed-section" style={{ display: 'flex', flexDirection: 'column', gap: '30px', textAlign: 'left', marginTop: '30px', padding: '0 120px' }}>
                            {feed.slice(0, 5).map((news, i) => (
                                <div key={i} className="feed-item" onClick={() => navigate(`/article/${news.id}`)} style={{ cursor: 'pointer', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', borderBottom: '1px solid #eee', paddingBottom: '20px', gap: '20px' }}>

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
                                            <span style={{ fontSize: '14px', fontWeight: '500' }}>{120 + (news.id || 0)}</span>
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
                                    <div className="feed-image" style={{ width: '312px', aspectRatio: '1.8/1', flexShrink: 0, overflow: 'hidden', borderRadius: '4px' }}>
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

export default PoliticsPage;
