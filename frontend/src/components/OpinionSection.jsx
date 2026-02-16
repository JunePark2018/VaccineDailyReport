import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './OpinionSection.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const OpinionSection = ({ reportId }) => {
    const [opinions, setOpinions] = useState([]);
    const [isExpanded, setIsExpanded] = useState(false);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (!reportId) return;

        const fetchOpinions = async () => {
            setLoading(true);
            try {
                const response = await axios.get(
                    `${API_BASE_URL}/reports/${reportId}/opinions`
                );
                setOpinions(response.data);
            } catch (error) {
                console.error("[Opinions] 오피니언 분석 불러오기 실패:", error);
            } finally {
                setLoading(false);
            }
        };
        fetchOpinions();
    }, [reportId]);

    if (!loading && opinions.length === 0) return null;

    return (
        <div className="opinion-section">
            <h3 className="section-title" style={{ textAlign: 'left' }}>
                언론사별 오피니언 · 사설
            </h3>

            {loading ? (
                <p className="opinion-loading">오피니언 분석 중...</p>
            ) : (
                <>
                    <div className={`opinion-comparison-container ${isExpanded ? 'expanded' : 'collapsed'}`}>
                        <ul className="opinion-comparison-list">
                            {opinions.map((item, idx) => (
                                <li key={idx} className="opinion-comparison-item">
                                    <div className="opinion-company-header">
                                        <div className="opinion-badge-row">
                                            <span className="opinion-company-badge">
                                                {item.company}
                                            </span>
                                        </div>
                                        <div className="opinion-hashtags">
                                            {item.hashtags && item.hashtags.map((tag, tIdx) => (
                                                <span key={tIdx} className="opinion-hashtag-badge">{tag}</span>
                                            ))}
                                        </div>
                                    </div>
                                    <p className="opinion-summary-text">
                                        {item.summary}
                                    </p>
                                    {isExpanded && item.evidence && (
                                        <div className="opinion-evidence-text">
                                            {item.evidence}
                                        </div>
                                    )}
                                </li>
                            ))}
                        </ul>
                    </div>
                    {opinions.length > 0 && (
                        <div className="opinion-show-more">
                            <button onClick={() => setIsExpanded(!isExpanded)}>
                                {isExpanded ? '접기' : '더보기'}
                            </button>
                        </div>
                    )}
                </>
            )}
        </div>
    );
};

export default OpinionSection;
