import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import axios from 'axios';
import Header from '../components/Header';
import Logo from '../components/Logo';
import logoImg from '../components/Logo.png';
import Searchbar from '../components/Searchbar';
import UserMenu from '../components/UserMenu';
import SkeletonNews from '../components/SkeletonNews';
import './SciencePage.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const SciencePage = () => {
    const name = 'IT/과학';
    const navigate = useNavigate();
    const location = useLocation();
    const [currentPage, setCurrentPage] = useState(1);
    const [displayArticles, setDisplayArticles] = useState([]);
    const [imageMap, setImageMap] = useState({});
    const [feedPage, setFeedPage] = useState(1);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        setCurrentPage(1);
        setFeedPage(1);

        const loadData = async () => {
            try {
                // 1. Fetch AI Generated News
                const response = await axios.get(`${API_BASE_URL}/reports?limit=100`);
                const realArticles = response.data;

                // 2. Map Backend Data to Frontend Structure
                const formattedArticles = realArticles.map(art => ({
                    ...art,
                    id: art.report_id, // [Fix] Map native ID to 'id'
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
                    // [Fix] Remove duplication loop to prevent duplicates
                    const shuffled = [...filtered].sort(() => Math.random() - 0.5);
                    setDisplayArticles(shuffled);

                    // 4. Fetch Images
                    const uniqueClusters = [...new Set(filtered.map(a => a.cluster_id))];
                    const newImageMap = {};

                    await Promise.allSettled(uniqueClusters.map(async (clusterId) => {
                        try {
                            const imgRes = await axios.get(`${API_BASE_URL}/reports/clusters/${clusterId}/news`);
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
            } finally {
                setLoading(false);
            }
        };

        setLoading(true);
        loadData();
    }, []);

    // 11 fixed + 20 feed items (4 pages * 5) = 31 items total
    const articlesPerBlock = 31;
    const blocksPerPage = 1;
    const articlesPerPage = articlesPerBlock * blocksPerPage;

    const renderMainContent = (blockArticles, blockIndex) => {
        if (!blockArticles || blockArticles.length === 0) return null;

        const mainArticle = blockArticles[0];

        // Ensure subsequent sections DO NOT contain the Main article
        const remainingArticles = blockArticles.slice(1).filter(art => art.id !== mainArticle.id);
        const gridArticles = remainingArticles.slice(0, 2);
        const listArticles = remainingArticles.slice(2, 10);

        // Feed Logic
        // Feed Logic: Exclude articles already shown in top sections (1 main, 2 grid, 8 list)
        const allFeedArticles = remainingArticles.slice(10);
        const feedPageSize = 5;
        const totalFeedPages = Math.ceil(allFeedArticles.length / 5);
        const currentFeedArticles = allFeedArticles.slice((feedPage - 1) * 5, feedPage * 5);

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

        const list = listArticles.map((art, i) => ({
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
                <section className="main-article-section">

                    {/* Left: Article Title */}
                    <div className="title-side" onClick={() => navigate(`/article/${mainData.id}`)}>
                        <h2>{mainData.title}</h2>
                        <p>{mainData.description}</p>
                    </div>

                    {/* Right: Article Photo */}
                    <div className="image-side" onClick={() => navigate(`/article/${mainData.id}`)}>
                        <div className="article-image-center">
                            <img src={mainData.image} alt="Main" onLoad={(e) => { if (!e.target.src.includes(logoImg)) e.target.style.objectFit = 'cover'; }} onError={(e) => { e.target.onerror = null; e.target.src = logoImg; e.target.style.objectFit = 'contain'; }} />
                        </div>
                    </div>
                </section>
                <div className="section-divider"></div>

                {/* Grid Section (2 items) */}
                {grid.length > 0 && (
                    <>
                        <section className="grid-section">
                            {grid.slice(0, 2).map((news, i) => (
                                <div key={i} className="grid-item" onClick={() => navigate(`/article/${news.id}`)}>
                                    <div className="grid-image">
                                        <img src={news.image} alt={news.title} onLoad={(e) => { if (!e.target.src.includes(logoImg)) e.target.style.objectFit = 'cover'; }} onError={(e) => { e.target.onerror = null; e.target.src = logoImg; e.target.style.objectFit = 'contain'; }} />
                                    </div>
                                    <div className="grid-info">
                                        <h3>{news.title}</h3>
                                        <p>{news.content}</p>
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
                        <section className="list-section">
                            {list.slice(0, 8).map((news, i) => (
                                <div key={i} className="list-item" onClick={() => navigate(`/article/${news.id}`)}>
                                    <div className="list-image">
                                        <img src={news.image} alt={news.title} onLoad={(e) => { if (!e.target.src.includes(logoImg)) e.target.style.objectFit = 'cover'; }} onError={(e) => { e.target.onerror = null; e.target.src = logoImg; e.target.style.objectFit = 'contain'; }} />
                                    </div>
                                    <div className="list-info">
                                        <h3>{news.title}</h3>
                                        <p>{news.content}</p>
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
                        <section className="feed-section">
                            {feed.slice(0, 5).map((news, i) => (
                                <div key={i} className="feed-item" onClick={() => navigate(`/article/${news.id}`)}>

                                    {/* Left Container: Like + Text */}
                                    <div className="feed-left-container">
                                        {/* Like Button (Display Only) */}
                                        <div className="like-icon">
                                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                                <path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 0 0 1-2-2v-7a2 0 0 1 2-2h3" />
                                            </svg>
                                            <span>{120 + (news.id || 0)}</span>
                                        </div>

                                        {/* Text Info */}
                                        <div className="feed-info">
                                            <h3>{news.title}</h3>
                                            <p>{news.content}</p>
                                        </div>
                                    </div>

                                    {/* Image Right (Reduced Height: aspect-ratio 1.8/1) */}
                                    <div className="feed-image">
                                        <img src={news.image} alt={news.title} onLoad={(e) => { if (!e.target.src.includes(logoImg)) e.target.style.objectFit = 'cover'; }} onError={(e) => { e.target.onerror = null; e.target.src = logoImg; e.target.style.objectFit = 'contain'; }} />
                                    </div>
                                </div>
                            ))}
                        </section>

                        {/* Pagination Numbers (Box Style) */}
                        {totalFeedPages > 1 && (
                            <div className="pagination-container">
                                {Array.from({ length: totalFeedPages }, (_, i) => i + 1).map((pageNum) => (
                                    <button
                                        key={pageNum}
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            setFeedPage(pageNum);
                                        }}
                                        className={`pagination-btn ${feedPage === pageNum ? 'active' : ''}`}
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
        <div className="science-page">
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

                {loading ? (
                    <div className="skeleton-container">
                        <SkeletonNews type="main" />
                        <div className="skeleton-grid">
                            <SkeletonNews type="grid" />
                            <SkeletonNews type="grid" />
                        </div>
                        <SkeletonNews type="feed" />
                    </div>
                ) : articleBlocks.length > 0 ? (
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