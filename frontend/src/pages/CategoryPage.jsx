import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import Logo from '../components/Logo';
import Searchbar from '../components/Searchbar';
import loginIcon from '../login_icon/login.png';
import './CategoryPage.css';

const CategoryPage = () => {
    const { name } = useParams();
    const navigate = useNavigate();
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [currentPage, setCurrentPage] = useState(1);
    const [displayArticles, setDisplayArticles] = useState([]);
    const [imageMap, setImageMap] = useState({});
    const itemsPerPage = 5;

    useEffect(() => {
        const token = localStorage.getItem('token');
        setIsLoggedIn(!!token);
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
                
                // Randomly shuffle articles when category changes
                if (articles.length > 0) {
                    const shuffled = [...articles].sort(() => Math.random() - 0.5);
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

    const RightHeaderIcon = (
        <img 
            src={loginIcon} 
            alt={isLoggedIn ? "마이페이지" : "로그인"} 
            width='35px' 
            onClick={() => navigate(isLoggedIn ? '/mypage' : '/login')} 
            style={{ cursor: 'pointer' }} 
        />
    );

    // Function to render the main content block (Featured, Highlights, Grid)
    // This is repeated 5 times as requested by the user
    const renderMainContent = (index) => {
        if (!displayArticles || displayArticles.length === 0) return null;

        // Use different articles for each loop from the shuffled list
        const baseIndex = (index * 3) % displayArticles.length;
        
        const featuredArticle = displayArticles[baseIndex];
        const gridArticle1 = displayArticles[(baseIndex + 1) % displayArticles.length];
        const gridArticle2 = displayArticles[(baseIndex + 2) % displayArticles.length];

        const featured = {
            title: featuredArticle?.title || "No Title",
            description: featuredArticle?.short_text || "No Description",
            image: featuredArticle ? (imageMap[featuredArticle.image] || featuredArticle.image) : null,
            category: name
        };

        const grid = [
            { 
                id: 1, 
                title: gridArticle1?.title || "No Title", 
                image: gridArticle1 ? (imageMap[gridArticle1.image] || gridArticle1.image) : null
            },
            { 
                id: 2, 
                title: gridArticle2?.title || "No Title", 
                image: gridArticle2 ? (imageMap[gridArticle2.image] || gridArticle2.image) : null
            }
        ];

        const highlights = [
            { keyword: '풍선으로 든 키워드', content: '"해당 키워드에 대한 요약된 내용"' },
            { keyword: '풍선으로 든 키워드', content: '"해당 키워드에 대한 요약된 내용"' },
            { keyword: '풍선으로 든 키워드', content: '"해당 키워드에 대한 요약된 내용"' }
        ];

        return (
            <React.Fragment key={index}>
                {/* Featured News Section */}
                <section className="featured-section" onClick={() => navigate('/article')} style={{ cursor: 'pointer' }}>
                    <div className="featured-image">
                        <img src={featured.image} alt="Featured" />
                        <div className="image-placeholder-text">IMAGE</div>
                    </div>
                    <div className="featured-info">
                        <h2>{featured.title}</h2>
                        <p>{featured.description}</p>
                        <div className="analysis-box">
                            <div className="analysis-placeholder">
                                <div className="analysis-x"></div>
                                <span className="analysis-text">분석</span>
                            </div>
                        </div>
                    </div>
                </section>

                {/* Highlights Section */}
                <section className="highlights-section">
                    {highlights.map((item, hIndex) => (
                        <div key={hIndex} className="highlight-box">
                            <span className="highlight-keyword">{item.keyword}</span>
                            <span className="highlight-content">{item.content}</span>
                        </div>
                    ))}
                </section>

                {/* Grid News Section */}
                <section className="grid-section">
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

    const totalPages = 5; // Fixed to 5 pages as requested for the loop

    return (
        <div className="category-page">
            <Header
                leftChild={<Logo />}
                midChild={<Searchbar maxWidth="400px" />}
                rightChild={RightHeaderIcon}
                headerTop="on"
                headerMain="on"
                headerBottom="on"
            />
            
            <main className="category-content">
                {/* Repeat the main content 5 times, offset by current page */}
                {displayArticles.length > 0 ? (
                    [...Array(5)].map((_, i) => renderMainContent(i + (currentPage - 1) * 5))
                ) : (
                    <div className="empty-category">
                        <p>해당 카테고리에 표시할 기사가 없습니다.</p>
                    </div>
                )}

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
