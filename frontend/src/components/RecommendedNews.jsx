import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import logoImg from './Logo.png';
import './RecommendedNews.css';

const RecommendedNews = ({ allArticles, userName, imageMap = {} }) => {
    const navigate = useNavigate();
    const [recommendedArticles, setRecommendedArticles] = useState([]);
    const [subscribedKeywords, setSubscribedKeywords] = useState([]); // [New]
    const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000'; // Make sure API_BASE_URL is available

    useEffect(() => {
        const fetchUserData = async () => {
            const loginId = localStorage.getItem('login_id');
            if (loginId) {
                try {
                    // Fetch user info to get subscribed keywords
                    // Assuming axios is available or imported. If not, need to import axios.
                    // Wait, axios is likely not imported in this component. I should add import axios.
                    // But I cannot see imports here. I will assume axios needs to be imported or use fetch.
                    // Let's use fetch for simplicity or assume axios is passed?
                    // Better to add `import axios` at top, but this tool edit is local.
                    // I will check imports later. For now, use fetch or assume axios.
                    // Let's use fetch to be safe if axios isn't imported.
                    const response = await fetch(`${API_BASE_URL}/users/${loginId}`);
                    if (response.ok) {
                        const data = await response.json();
                        setSubscribedKeywords(data.subscribed_keywords || []);
                    }
                } catch (e) {
                    console.error("Failed to fetch user subscriptions", e);
                }
            }
        };
        fetchUserData();
    }, []);

    useEffect(() => {
        // 1. Load User History
        const viewedTags = JSON.parse(localStorage.getItem('viewed_tags') || '[]');
        const viewedCats = JSON.parse(localStorage.getItem('viewed_categories') || '[]');
        const loginId = localStorage.getItem('login_id');

        // Condition 1: If no history & no login -> Hide (Return null)
        if (!loginId && viewedTags.length === 0 && viewedCats.length === 0) {
            setRecommendedArticles([]);
            return;
        }

        // 2. Filter Logic
        if (!allArticles || allArticles.length === 0) return;

        // Helper to parse keywords safely
        const parseKeywords = (art) => {
            if (Array.isArray(art.keywords)) return art.keywords;
            if (typeof art.keywords === 'string') {
                try { return JSON.parse(art.keywords); } catch { return []; }
            }
            return [];
        };

        // Score Articles
        // Subscribed Keyword: +5
        // Tag Match: +3 points
        // Category Match: +1 point
        const scored = allArticles.map(art => {
            let score = 0;
            const keywords = parseKeywords(art);

            // Subscribed Keyword matching (+5)
            const subMatchCount = keywords.filter(k => subscribedKeywords.includes(k)).length;
            score += subMatchCount * 5;

            // Tag matching (+3)
            const matchCount = keywords.filter(k => viewedTags.includes(k)).length;
            score += matchCount * 3;

            // Category matching (+1)
            if (viewedCats.includes(art.category_name)) {
                score += 1;
            }

            return { ...art, score };
        });

        // 3. Sort & Slice
        // Filter out 0 score items (unless we want to show popular as fallback, but user requested hide)
        // Actually, user said if "first time or not logged in" -> hide.
        // If user read 1 article, they are not "first time".
        // So we show items with score > 0.
        const filtered = scored.filter(a => a.score > 0)
            .sort((a, b) => b.score - a.score)
            .slice(0, 10); // Top 10

        setRecommendedArticles(filtered);

    }, [allArticles, subscribedKeywords]); // Add subscribedKeywords to dependency

    const scrollRef = React.useRef(null);

    const scroll = (direction) => {
        if (scrollRef.current) {
            const scrollAmount = 300;
            scrollRef.current.scrollBy({
                left: direction === 'left' ? -scrollAmount : scrollAmount,
                behavior: 'smooth'
            });
        }
    };

    if (recommendedArticles.length === 0) return null;

    return (
        <section className="recommended-news-section fade-in">
            <h3 className="recommended-header">
                {userName ? `${userName}님을 위한 추천 뉴스` : '회원님을 위한 추천 뉴스'}
            </h3>
            <div className="recommended-container-wrapper">
                <button className="rec-nav-btn rec-prev" onClick={() => scroll('left')}>&#x2039;</button>
                <div className="recommended-scroll-container" ref={scrollRef}>
                    {recommendedArticles.map((art, idx) => (
                        <div
                            key={art.report_id || idx}
                            className="recommended-card"
                            onClick={() => navigate(`/article/${art.report_id}`)}
                        >
                            <div className="recommended-img-wrapper">
                                <img
                                    src={imageMap[art.image] || imageMap[`cluster_${art.cluster_id}`] || logoImg}
                                    alt={art.title}
                                    onLoad={(e) => { if (!e.target.src.includes(logoImg)) e.target.style.objectFit = 'cover'; }}
                                    onError={(e) => { e.target.onerror = null; e.target.src = logoImg; e.target.style.objectFit = 'contain'; }}
                                />
                            </div>
                            <div className="recommended-info">
                                <h4 className="recommended-title">{art.title}</h4>
                                <p className="recommended-desc">{art.short_text || ''}</p>
                            </div>
                        </div>
                    ))}
                </div>
                <button className="rec-nav-btn rec-next" onClick={() => scroll('right')}>&#x203A;</button>
            </div>
        </section>
    );
};

export default RecommendedNews;
