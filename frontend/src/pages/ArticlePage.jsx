import React, { useMemo, useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import Sources from '../components/Sources';
import RightSideBar from '../components/RightSideBar';
import NewsText from '../components/NewsText';
import Header from '../components/Header';
import Searchbar from '../components/Searchbar';
import Logo from '../components/Logo';
import logoImg from '../components/Logo.png';
import UserMenu from '../components/UserMenu';
import './ArticlePage.css';
import axios from 'axios';
import WordCloudComponent from '../components/WordCloud';
import Timeline from '../components/Timeline';
import AI_News_Recommendation from '../components/AI_News_Recommendation';
import { HiOutlineSpeakerWave, HiOutlinePrinter, HiOutlineDocumentDuplicate, HiOutlineBookmark, HiMiniBookmark } from 'react-icons/hi2';
import SkeletonNews from '../components/SkeletonNews'; // Import Skeleton



const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
function ArticlePage() {

  const { id } = useParams();

  const [loading, setLoading] = useState(true); // Add loading state
  const [article, setArticle] = useState({
    title: "기사를 찾을 수 없습니다.",
    contents: "기사 내용을 찾을 수 없습니다."
  });

  const [keywords, setKeywords] = useState([]);
  const [imgURL, setImgURL] = useState("");

  // Sidebar & Search State
  const [isSidebarOpen, setSidebarOpen] = useState(false);
  const [selectedSentence, setSelectedSentence] = useState(null);

  // Comparison State
  const [mediaNames, setMediaNames] = useState([]);
  const [isExpanded, setIsExpanded] = useState(false);
  // Evidence Map removed

  // Like State
  const [likeCount, setLikeCount] = useState(0);
  const [isLiked, setIsLiked] = useState(false);

  // Scrap State
  const [isScraped, setIsScraped] = useState(false);

  // Action Button States (Unified Popup State)
  // 'tts', 'font', or null (Share removed)
  const [activePopup, setActivePopup] = useState(null);
  const [fontSize, setFontSize] = useState(3);

  // TTS Specific States
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [ttsSpeed, setTtsSpeed] = useState(1.0); // 0.8, 1.0, 1.2
  const [voices, setVoices] = useState([]);
  const [selectedVoice, setSelectedVoice] = useState(null);

  // Load voices
  useEffect(() => {
    const loadVoices = () => {
      const avail = window.speechSynthesis.getVoices();
      const koVoices = avail.filter(v => v.lang.includes('ko') || v.lang.includes('KO'));
      setVoices(koVoices);
      if (koVoices.length > 0) setSelectedVoice(koVoices[0]);
    };

    loadVoices();
    window.speechSynthesis.onvoiceschanged = loadVoices;
  }, []);

  // Helper: Friendly Voice Name
  const getFriendlyVoiceName = (voice) => {
    const name = voice.name;
    // Google
    if (name.includes('Google')) return '여성 음성 (Google)';
    // Microsoft
    if (name.includes('Heami')) return '여성 음성 (Microsoft)';
    if (name.includes('InJoon')) return '남성 음성 (Microsoft)';

    // Clean up
    let cleanName = name
      .replace('Google', '')
      .replace('Microsoft', '')
      .replace('한국어', '')
      .replace('Korean', '')
      .replace('한국의', '')
      .replace(/[()\-]/g, '')
      .trim();

    return cleanName || '기본 음성';
  };

  // Popup Toggle Helper
  const togglePopup = (type) => {
    setActivePopup(prev => (prev === type ? null : type));
  };

  const closePopup = () => setActivePopup(null);

  const handlePrint = () => {
    window.print();
  };

  const handleCopy = async () => {
    if (!article.contents) return;
    try {
      await navigator.clipboard.writeText(article.contents);
      alert("기사 내용이 클립보드에 복사되었습니다.");
    } catch (err) {
      console.error('Failed to copy text: ', err);
      alert("복사에 실패했습니다.");
    }
  };

  const handleScrap = async () => {
    const login_id = localStorage.getItem('login_id');
    if (!login_id) {
      alert("로그인이 필요한 기능입니다.");
      return;
    }

    try {
      // Use report_id (integer) for scraps
      const reportId = parseInt(id, 10);

      const response = await axios.post(`${API_BASE_URL}/users/${login_id}/scraps`, {
        report_id: reportId
      });

      // Use explicit message from backend to determine state
      // Backend returns "Scrap added" or "Scrap removed"
      if (response.data.message.includes("added")) {
        setIsScraped(true);
        alert("스크랩 되었습니다.");
      } else {
        setIsScraped(false);
        alert("스크랩이 취소되었습니다.");
      }
    } catch (err) {
      console.error("Scrap failed:", err);
      alert("스크랩 처리 중 오류가 발생했습니다.");
    }
  };

  const handleSpeakToggle = () => {
    togglePopup('tts');
  };

  const handleFontToggle = () => {
    togglePopup('font');
  };

  // TTS Logic
  const startSpeaking = () => {
    if (isSpeaking) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
      return;
    }
    if (!article.contents) return;

    const utterance = new SpeechSynthesisUtterance(article.contents);
    utterance.lang = 'ko-KR';
    utterance.rate = ttsSpeed;
    if (selectedVoice) utterance.voice = selectedVoice;

    utterance.onend = () => setIsSpeaking(false);
    window.speechSynthesis.speak(utterance);
    setIsSpeaking(true);
  };

  const stopSpeaking = () => {
    window.speechSynthesis.cancel();
    setIsSpeaking(false);
  };

  const changeFontSize = (level) => {
    setFontSize(level);
  };

  // Evidence Fetching Removed

  const handleSentenceClick = (sentence) => {
    setSelectedSentence(sentence);
    setSidebarOpen(true);
  };

  const closeSidebar = () => {
    setSidebarOpen(false);
  };

  const highlightMediaText = (text) => {
    if (!text || mediaNames.length === 0) return text;
    const sortedNames = [...mediaNames].sort((a, b) => b.length - a.length);
    const regex = new RegExp(`(${sortedNames.join('|')})`, 'g');
    const parts = text.split(regex);
    return parts.map((part, index) => {
      if (mediaNames.includes(part)) {
        return (
          <span key={index} style={{ color: '#d32f2f', fontWeight: 'bold' }}>{part}</span>
        );
      }
      return part;
    });
  };

  useEffect(() => {
    window.scrollTo(0, 0);

    const fetchInfo = async () => {
      setLoading(true);
      try {
        const ai_news_response = await axios.get(`${API_BASE_URL}/reports/${id}`);
        const article = ai_news_response.data;
        setArticle(article);
        setLikeCount(article.like_count || 0);

        const login_id = localStorage.getItem('login_id');
        if (login_id) {
          // Check Like status
          try {
            const reactionResponse = await axios.get(`${API_BASE_URL}/users/${login_id}/reactions/${id}`);
            const userLiked = reactionResponse.data.value === 1;
            setIsLiked(userLiked);
          } catch (err) {
            setIsLiked(false);
          }

          // Check Scrap status
          // Need user info. calling read_user
          try {
            const userRes = await axios.get(`${API_BASE_URL}/users/${login_id}`);
            const reportId = parseInt(id, 10);
            const scraps = userRes.data.scraps || [];

            // Check if scraps contains the ID (int) or the current URL (legacy)
            // Ensure type safety comparison for ID
            const isScrapped = scraps.some(item =>
              item === reportId || item === window.location.href
            );

            setIsScraped(isScrapped);
          } catch (err) {
            console.error("Failed to check scrap status:", err);
          }
        }

        let parsedKeywords = [];
        if (typeof article.keywords === 'string') {
          try {
            parsedKeywords = JSON.parse(article.keywords);
          } catch (e) {
            console.error("Keyword parse error", e);
            parsedKeywords = [];
          }
        } else if (Array.isArray(article.keywords)) {
          parsedKeywords = article.keywords;
        }

        const filteredKeywords = parsedKeywords.filter(item => item.value > 20);
        setKeywords(filteredKeywords);

        const img_url_response = await axios.get(`${API_BASE_URL}/reports/clusters/${article.cluster_id}/news`);
        const newsList = img_url_response.data;
        const companies = [...new Set(newsList.map(n => n.company_name).filter(Boolean))];
        setMediaNames(companies);

        const allImgUrls = newsList.flatMap(news => news.img_urls ?? []).filter(Boolean);
        if (allImgUrls.length > 0) {
          const img_number = Math.floor(Math.random() * allImgUrls.length);
          setImgURL(allImgUrls[img_number]);
        }
      } catch (error) {
        console.error('Data Fetch Error:', error);
      } finally {
        setLoading(false);
      }
    };

    const login_id = localStorage.getItem('login_id');
    if (login_id) {
      axios.post(`${API_BASE_URL}/users/${login_id}/read/${id}`).catch(console.error);
    }

    fetchInfo();
  }, [id]);


  return (
    <div className={`ArticlePage ${isSidebarOpen ? 'sidebar-open' : ''} fs-${fontSize}`}>
      <div className="page-content">

        {/* Header */}
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
          headerTop="on" headerMain="on" headerBottom="on"
        />

        {/* Main */}
        <main className="main-content">
          {loading ? (
            <div style={{ padding: '40px 0' }}>
              <SkeletonNews type="article" />
            </div>
          ) : (
            <>
              <div className="article-content-wrapper">
                <div className='article-section'>
                  <div className='article-img'>
                    <img src={imgURL} onLoad={(e) => { if (!e.target.src.includes(logoImg)) e.target.style.objectFit = 'cover'; }} onError={(e) => { e.target.onerror = null; e.target.src = logoImg; e.target.style.objectFit = 'contain'; }} />
                  </div>

                  <div style={{ padding: '0 20px' }}>
                    <h1 className="article-head-title">{article.title}</h1>

                    {/* Metadata Row: Date (Left) + Buttons (Right) */}
                    <div className="article-meta-row">
                      <div className="meta-left">
                        {article.created_at && (
                          <>
                            <span style={{ padding: '4px 10px', backgroundColor: '#f0f0f0', borderRadius: '4px', fontSize: '0.85rem', color: '#666', fontWeight: '500' }}>AI 생성</span>
                            <span>
                              {new Date(article.created_at).getFullYear()}.
                              {String(new Date(article.created_at).getMonth() + 1).padStart(2, '0')}.
                              {String(new Date(article.created_at).getDate()).padStart(2, '0')}
                            </span>
                          </>
                        )}
                      </div>

                      <div className="meta-right">
                        {/* TTS Button */}
                        <div style={{ position: 'relative' }}>
                          <button className="action-btn" onClick={handleSpeakToggle} title="음성 듣기 설정">
                            <HiOutlineSpeakerWave style={{ color: isSpeaking ? '#4285F4' : 'inherit' }} />
                          </button>
                          {activePopup === 'tts' && (
                            <div className="popup-container tts-popup">
                              <div className="popup-header">
                                <h4 className="popup-title">본문 듣기 설정</h4>
                                <button className="popup-close-btn" onClick={closePopup}>×</button>
                              </div>
                              <div className="tts-section">
                                <span className="tts-label">목소리 (브라우저 제공)</span>
                                <div className="tts-options">
                                  {voices.length === 0 && <span style={{ fontSize: '0.8rem', color: '#999' }}>한국어 음성 없음</span>}
                                  {voices.map(v => (
                                    <label key={v.name} className="tts-radio-label">
                                      <input
                                        type="radio"
                                        name="voice"
                                        checked={selectedVoice?.name === v.name}
                                        onChange={() => { setSelectedVoice(v); }}
                                      />
                                      {getFriendlyVoiceName(v)}
                                    </label>
                                  ))}
                                </div>
                              </div>
                              <div className="tts-section">
                                <span className="tts-label">말하기 속도</span>
                                <div className="tts-options">
                                  <label className="tts-radio-label"><input type="radio" name="speed" checked={ttsSpeed === 0.8} onChange={() => setTtsSpeed(0.8)} /> 느림</label>
                                  <label className="tts-radio-label"><input type="radio" name="speed" checked={ttsSpeed === 1.0} onChange={() => setTtsSpeed(1.0)} /> 보통</label>
                                  <label className="tts-radio-label"><input type="radio" name="speed" checked={ttsSpeed === 1.2} onChange={() => setTtsSpeed(1.2)} /> 빠름</label>
                                </div>
                              </div>
                              <button className="tts-play-btn" onClick={isSpeaking ? stopSpeaking : startSpeaking}>
                                {isSpeaking ? '본문 듣기 중지' : '본문 듣기 시작'}
                              </button>
                            </div>
                          )}
                        </div>

                        {/* Font Size Button */}
                        <div style={{ position: 'relative' }}>
                          <button className="action-btn" onClick={handleFontToggle} title="글자 크기">
                            <span className="action-btn-text font-size-btn-content">
                              <span className="small-ga">가</span>
                              <span className="large-ga">가</span>
                            </span>
                          </button>
                          {activePopup === 'font' && (
                            <div className="popup-container font-size-popup-unified">
                              <div className="popup-header">
                                <h4 className="popup-title">글자 크기 설정</h4>
                                <button className="popup-close-btn" onClick={closePopup}>×</button>
                              </div>
                              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '4px' }}>
                                {[1, 2, 3, 4, 5].map((level) => (
                                  <button
                                    key={level}
                                    className={`font-option ${fontSize === level ? 'active' : ''}`}
                                    onClick={() => changeFontSize(level)}
                                  >
                                    {level}
                                  </button>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>

                        {/* Copy Button */}
                        <button className="action-btn" onClick={handleCopy} title="원문 복사 (기사 내용)">
                          <HiOutlineDocumentDuplicate />
                        </button>

                        {/* Print Button */}
                        <button className="action-btn" onClick={handlePrint} title="인쇄하기">
                          <HiOutlinePrinter />
                        </button>

                        {/* Scrap Button */}
                        <button className="action-btn" onClick={handleScrap} title={isScraped ? "스크랩 취소" : "스크랩"}>
                          {isScraped ? <HiMiniBookmark style={{ color: '#007bff' }} /> : <HiOutlineBookmark />}
                        </button>
                      </div>
                    </div>

                    <hr className="article-head-divider" /> {/* Keeping HR invisble via CSS or actually keep it? CSS hides it. */}

                    <div className="article-comparer" style={{ marginTop: '10px', marginBottom: '40px', borderTop: 'none' }}>
                      <h3 className="section-title">비교분석</h3>
                      <div className={`comparison-container ${isExpanded ? 'expanded' : 'collapsed'}`}>
                        <ul className="comparison-list">
                          {article?.analysis_result?.media_comparison_bullets?.map((item, idx) => {
                            // Backward compatibility: Handle string items
                            const isString = typeof item === 'string';
                            const analysisText = isString ? item : item.analysis;
                            const summaryText = isString ? null : item.summary;

                            return (
                              <li key={idx} className="comparison-item">
                                {summaryText && (
                                  <div className="summary-badge" style={{
                                    display: 'inline-block',
                                    backgroundColor: '#e3f2fd',
                                    color: '#0d47a1',
                                    padding: '4px 8px',
                                    borderRadius: '4px',
                                    fontSize: '0.9em',
                                    marginBottom: '6px',
                                    fontWeight: '600'
                                  }}>
                                    {summaryText}
                                  </div>
                                )}
                                <div className="analysis-text">
                                  {highlightMediaText(analysisText.replace(/^- /, '').replace(/\[/g, '').replace(/\]/g, ''))}
                                </div>
                              </li>
                            )
                          })}
                        </ul>
                      </div>
                      {article?.analysis_result?.media_comparison_bullets?.length > 0 && (
                        <div className="show-more-button-wrapper">
                          <button className="show-more-button link-style" onClick={() => setIsExpanded(!isExpanded)}>
                            {isExpanded ? '접기' : '펼쳐보기'}
                          </button>
                        </div>
                      )}
                    </div>
                  </div>

                  <NewsText
                    contents={article.contents}
                    onSentenceClick={handleSentenceClick}
                    articleId={id}
                    likeCount={likeCount}
                    isLiked={isLiked}
                    onLikeUpdate={(newCount, newIsLiked) => {
                      setLikeCount(newCount);
                      setIsLiked(newIsLiked);
                    }}
                    fontSize={fontSize}
                  />

                  <div className="wordcloud-section" style={{ marginTop: '60px', padding: '20px', backgroundColor: '#f9f9f9', borderRadius: '12px' }}>
                    <h3 className="section-title" style={{ textAlign: 'center', marginBottom: '30px' }}>기사 핵심 키워드</h3>
                    <div style={{ display: 'flex', justifyContent: 'center', width: '400px', maxWidth: '100%', margin: '0 auto', aspectRatio: '1/1' }}>
                      <WordCloudComponent keywords={keywords} width={400} height={400} />
                    </div>
                  </div>

                  <div className="timeline-section" style={{ marginTop: '40px', padding: '20px' }}>
                    <Timeline currentArticleId={id} />
                  </div>

                  <Sources clusterId={article.cluster_id} />
                </div>
              </div>

              <AI_News_Recommendation articleId={id} number_of_article={3} />
            </>
          )}
        </main>

        <RightSideBar
          isOpen={isSidebarOpen}
          onClose={closeSidebar}
          searchKeyword={selectedSentence}
          clusterId={article.cluster_id}
        />
      </div >
    </div >
  );
}

export default ArticlePage;
