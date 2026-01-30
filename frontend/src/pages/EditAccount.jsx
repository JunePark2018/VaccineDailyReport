import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import Logo from '../components/Logo';
import Searchbar from '../components/Searchbar';
import UserMenu from '../components/UserMenu';
import { categories as categoryData } from '../components/categoryIcon/categoryData';
import './EditAccount.css';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
export default function EditAccount() {
    const navigate = useNavigate();

    // --- State Management ---
    const [formData, setFormData] = useState({
        name: '',
        loginId: '',
        password: '',
        confirmPassword: '',
        email: '',
        ageGroup: '',
        gender: '',
        marketingAgree: false,
    });

    const [selectedCategories, setSelectedCategories] = useState([]);
    const [showPassword, setShowPassword] = useState(false);
    const [passwordStrength, setPasswordStrength] = useState({ score: 0, label: '', color: '#e0e0e0' });
    const [errors, setErrors] = useState({});
    const [loading, setLoading] = useState(true);

    // --- Fetch User Data ---
    useEffect(() => {
        const fetchUserData = async () => {
            const login_id = localStorage.getItem('login_id');
            if (!login_id) {
                alert("로그인 정보가 없습니다.");
                navigate('/login');
                return;
            }

            try {
                const response = await axios.get(`${API_BASE_URL}/users/${login_id}`);
                const data = response.data;

                setFormData({
                    name: data.user_real_name || '',
                    loginId: data.login_id,
                    password: '', // 보안상 비밀번호는 비워둠
                    confirmPassword: '',
                    email: data.email || '',
                    ageGroup: data.age_range || '',
                    gender: data.gender || '',
                    marketingAgree: data.marketing_agree || false,
                });
                setSelectedCategories(data.subscribed_categories || []);
            } catch (error) {
                console.error("사용자 정보 로딩 실패:", error);
                alert("사용자 정보를 불러오는 데 실패했습니다.");
            } finally {
                setLoading(false);
            }
        };

        fetchUserData();
    }, [navigate]);

    // --- Static Data ---
    const categoryOptions = categoryData
        .filter(cat => cat.label !== '전체메뉴' && cat.label !== '이슈' && cat.label !== '홈')
        .map(cat => cat.label);

    const ageGroups = ['10세 미만', '10~19세', '20~29세', '30~39세', '40~49세', '50~59세', '60~69세', '70세 이상', '비공개'];
    const genders = ['남성', '여성', '비공개'];

    // --- Password Logic ---
    useEffect(() => {
        const pwd = formData.password;
        if (!pwd) {
            setPasswordStrength({ score: 0, label: '', color: '#e0e0e0' });
            return;
        }

        let score = 0;
        if (pwd.length >= 8) score++;
        if (/[A-Z]/.test(pwd)) score++;
        if (/[0-9]/.test(pwd)) score++;
        if (/[!@#$%^&*]/.test(pwd)) score++;

        const strengthConfig = [
            { label: '매우 약함', color: '#ff4d4d' },
            { label: '약함', color: '#ff944d' },
            { label: '보통', color: '#ffda4d' },
            { label: '강함', color: '#90ee90' },
            { label: '매우 강함', color: '#2ecc71' }
        ];

        const finalScore = Math.min(score, 4);
        setPasswordStrength({
            score: finalScore,
            label: strengthConfig[finalScore].label,
            color: strengthConfig[finalScore].color
        });
    }, [formData.password]);

    // --- Event Handlers ---
    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));

        if (errors[name]) {
            setErrors(prev => ({ ...prev, [name]: null }));
        }

        if (name === 'password' && errors.confirmPassword) {
            setErrors(prev => ({ ...prev, confirmPassword: null }));
        }
    };

    const handleCategoryClick = (category) => {
        if (selectedCategories.includes(category)) {
            setSelectedCategories(selectedCategories.filter(item => item !== category));
        } else {
            setSelectedCategories([...selectedCategories, category]);
        }
        if (errors.categories) {
            setErrors(prev => ({ ...prev, categories: null }));
        }
    };

    // --- Validation Logic ---
    const validate = () => {
        let newErrors = {};

        if (!formData.name.trim()) {
            newErrors.name = "이름을 입력해주세요.";
        }

        if (!formData.email.includes('@')) {
            newErrors.email = "유효한 이메일 형식이 아닙니다 (@ 누락).";
        }

        if (!formData.ageGroup) {
            newErrors.ageGroup = "연령대를 선택해주세요.";
        }

        if (!formData.gender) {
            newErrors.gender = "성별을 선택해주세요.";
        }

        if (formData.password && formData.password.length < 8) {
            newErrors.password = "비밀번호는 최소 8자 이상이어야 합니다.";
        }

        if (formData.password !== formData.confirmPassword) {
            newErrors.confirmPassword = "비밀번호가 일치하지 않습니다.";
        }

        if (selectedCategories.length < 3) {
            newErrors.categories = `최소 3개의 관심 분야를 선택해주세요. (현재 ${selectedCategories.length}개 선택)`;
        }

        // 6. Agreement Check - Disabled
        // if (!formData.marketingAgree) {
        //     newErrors.agreement = "서비스 이용을 위해 사용자 경험 데이터 수집에 동의해야 합니다.";
        // }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (validate()) {
            const submitData = {
                user_real_name: formData.name,
                email: formData.email,
                age_range: formData.ageGroup,
                gender: formData.gender,
                subscribed_categories: selectedCategories,
                marketing_agree: formData.marketingAgree
            };

            // 비밀번호가 입력된 경우에만 포함
            if (formData.password) {
                submitData.password = formData.password;
            }

            try {
                await axios.put(`${API_BASE_URL}/users/${formData.loginId}`, submitData);
                alert("회원 정보가 수정되었습니다.");
                navigate('/mypage'); // URL parameter 없이 이동하면, MyPage가 localStorage에서 ID를 읽어야 함.
                // MyPage.jsx를 확인해보니 useParams를 씀 (<Route path='/mypage/:login_id' />)
                // 따라서 navigate(`/mypage/${formData.loginId}`)로 수정 필요할 수 있음.
                // App.js: <Route path='/mypage/:login_id' element={<MyPage />} />
                navigate(`/mypage/${formData.loginId}`);
            } catch (error) {
                console.error("업데이트 실패:", error);
                alert("회원 정보 수정 중 오류가 발생했습니다.");
            }
        }
    };

    if (loading) {
        return <div className="edit-account-container" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>로딩 중...</div>;
    }

    return (
        <div className="edit-account-container">
            <Header
                headerTop="on"
                headerMain="on"
                headerBottom="off"
                leftChild={<Logo />}
                midChild={null}
                rightChild={
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0', justifyContent: 'flex-end', width: 'auto' }}>
                        <div className="mobile-hidden" style={{ position: 'relative' }}>
                            <Searchbar className="always-open" />
                        </div>
                        <UserMenu />
                    </div>
                }
                noSearchMobile={true}
            />
            <div className="edit-account-box">
                <h2>정보 수정</h2>
                <p className="description">
                    회원 정보를 수정하고 맞춤형 서비스를 계속 이용하세요.
                </p>

                <form onSubmit={handleSubmit}>

                    <div className="input-group">
                        <label>이름</label>
                        <input
                            type="text"
                            name="name"
                            placeholder="홍길동"
                            value={formData.name}
                            onChange={handleChange}
                            className={errors.name ? "input-error" : ""}
                        />
                        {errors.name && <span className="error-msg">{errors.name}</span>}
                    </div>

                    <div className="input-group">
                        <label>아이디</label>
                        <input
                            type="text"
                            name="loginId"
                            value={formData.loginId}
                            disabled
                            style={{ backgroundColor: '#f0f0f0', cursor: 'not-allowed' }}
                        />
                        <span className="sub-label" style={{ marginTop: '4px' }}>아이디는 변경할 수 없습니다.</span>
                    </div>

                    <div className="input-group">
                        <label>새 비밀번호 (변경 시에만 입력)</label>
                        <div className="input-group-joined">
                            <div className="input-row-joined top">
                                <input
                                    type={showPassword ? "text" : "password"}
                                    name="password"
                                    placeholder="8자 이상, 대문자/특수문자 포함 권장"
                                    value={formData.password}
                                    onChange={handleChange}
                                    className={errors.password ? "input-error" : ""}
                                />
                                <button
                                    type="button"
                                    className="toggle-btn-joined"
                                    onClick={() => setShowPassword(!showPassword)}
                                >
                                    {showPassword ? "숨기기" : "보기"}
                                </button>
                            </div>
                            <div className="input-row-joined bottom">
                                <input
                                    type={showPassword ? "text" : "password"}
                                    name="confirmPassword"
                                    placeholder="비밀번호 재확인"
                                    value={formData.confirmPassword}
                                    onChange={handleChange}
                                    className={errors.confirmPassword ? "input-error" : ""}
                                />
                            </div>
                        </div>
                        {/* Password Feedback (Strength & Match) */}
                        <div className="password-feedback">
                            {formData.password && (
                                <div className="strength-meter-container">
                                    <div
                                        className="strength-bar"
                                        style={{
                                            width: `${(passwordStrength.score + 1) * 20}%`,
                                            backgroundColor: passwordStrength.color
                                        }}
                                    ></div>
                                    <span style={{ color: passwordStrength.color }}>
                                        {passwordStrength.label}
                                    </span>
                                </div>
                            )}

                            {formData.password && formData.confirmPassword && formData.password === formData.confirmPassword && (
                                <span className="success-msg" style={{ color: '#2ecc71', fontSize: '13px', marginTop: '5px', display: 'block' }}>
                                    비밀번호가 일치합니다.
                                </span>
                            )}

                            {errors.password && <span className="error-msg">{errors.password}</span>}
                            {errors.confirmPassword && <span className="error-msg">{errors.confirmPassword}</span>}
                        </div>
                    </div>

                    <div className="input-group">
                        <label>이메일</label>
                        <input
                            type="email"
                            name="email"
                            placeholder="example@email.com"
                            value={formData.email}
                            onChange={handleChange}
                            className={errors.email ? "input-error" : ""}
                        />
                        {errors.email && <span className="error-msg">{errors.email}</span>}
                    </div>

                    {/* New Sections: Age Group and Gender */}
                    <div className="input-row">
                        <div className="input-group half">
                            <label>연령대</label>
                            <select
                                name="ageGroup"
                                value={formData.ageGroup}
                                onChange={handleChange}
                                className={errors.ageGroup ? "input-error" : ""}
                            >
                                <option value="">선택하세요</option>
                                {ageGroups.map(age => <option key={age} value={age}>{age}</option>)}
                            </select>
                            {errors.ageGroup && <span className="error-msg">{errors.ageGroup}</span>}
                        </div>
                        <div className="input-group half">
                            <label>성별</label>
                            <select
                                name="gender"
                                value={formData.gender}
                                onChange={handleChange}
                                className={errors.gender ? "input-error" : ""}
                            >
                                <option value="">선택하세요</option>
                                {genders.map(g => <option key={g} value={g}>{g}</option>)}
                            </select>
                            {errors.gender && <span className="error-msg">{errors.gender}</span>}
                        </div>
                    </div>

                    <div className="category-section">
                        <label>관심 분야 선택 <span className="sub-label">(우선순위대로 번호가 지정됩니다, 최소 3개)</span></label>
                        <div className="category-grid">
                            {categoryOptions.map((cat) => {
                                const index = selectedCategories.indexOf(cat);
                                const isSelected = index !== -1;
                                return (
                                    <div
                                        key={cat}
                                        className={`category-box ${isSelected ? 'selected' : ''}`}
                                        onClick={() => handleCategoryClick(cat)}
                                    >
                                        {cat}
                                        {isSelected && <div className="badge">{index + 1}</div>}
                                    </div>
                                )
                            })}
                        </div>
                        {errors.categories && <span className="error-msg">{errors.categories}</span>}
                    </div>

                    {/* Agreement Section Disabled */}
                    {/* 
                    <div className="agreement-section">
                        <label className="checkbox-container">
                            <input
                                type="checkbox"
                                name="marketingAgree"
                                checked={formData.marketingAgree}
                                onChange={handleChange}
                            />
                            <span className="checkmark-custom"></span>
                            <span className="text">
                                (필수) 사용자 경험 향상 및 서비스 개선을 위한 활동 기록 수집에 동의합니다.
                            </span>
                        </label>
                        {errors.agreement && <span className="error-msg">{errors.agreement}</span>}
                    </div>
                    */}

                    <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
                        <button type="submit" className="submit-btn outline-black" style={{ flex: 1, margin: 0 }}>수정 완료</button>
                        <button
                            type="button"
                            className="submit-btn outline-red"
                            style={{
                                flex: 1,
                                margin: 0
                            }}
                            onClick={() => navigate(-1)}
                        >
                            취소
                        </button>
                    </div>

                    {/* 
                    <div className="login-redirect">
                        <span onClick={() => navigate('/mypage')}>마이페이지로 돌아가기</span>
                    </div>
                    */}
                </form>
            </div>
        </div>
    );
}
