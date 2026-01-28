import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import Logo from '../components/Logo';
import Searchbar from '../components/Searchbar';
import UserMenu from '../components/UserMenu';
import { categories as categoryData } from '../components/categoryIcon/categoryData';
import './CreateAccount.css';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
export default function CreateAccount() {
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
        marketingAgree: false, // For the tracking agreement
    });

    const [selectedCategories, setSelectedCategories] = useState([]); // Stores chosen categories in order
    const [showPassword, setShowPassword] = useState(false);
    const [passwordStrength, setPasswordStrength] = useState({ score: 0, label: '', color: '#e0e0e0' });
    const [errors, setErrors] = useState({}); // To store validation error messages

    // --- Static Data ---
    const categoryOptions = categoryData
        .filter(cat => cat.label !== '전체메뉴' && cat.label !== '이슈' && cat.label !== '홈')
        .map(cat => cat.label);

    const ageGroups = ['10세 미만', '10~19세', '20~29세', '30~39세', '40~49세', '50~59세', '60~69세', '70세 이상', '비공개'];
    const genders = ['남성', '여성', '비공개'];

    // --- Password Logic ---
    // Runs every time the password field changes
    useEffect(() => {
        const pwd = formData.password;
        if (!pwd) {
            setPasswordStrength({ score: 0, label: '', color: '#e0e0e0' });
            return;
        }

        let score = 0;
        if (pwd.length >= 8) score++;          // Check length
        if (/[A-Z]/.test(pwd)) score++;        // Check uppercase
        if (/[0-9]/.test(pwd)) score++;        // Check numbers
        if (/[!@#$%^&*]/.test(pwd)) score++;   // Check special chars

        const strengthConfig = [
            { label: '매우 약함', color: '#ff4d4d' }, // 0
            { label: '약함', color: '#ff944d' },      // 1
            { label: '보통', color: '#ffda4d' },      // 2
            { label: '강함', color: '#90ee90' },      // 3
            { label: '매우 강함', color: '#2ecc71' }  // 4
        ];

        // Cap score at 4
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

        // Clear specific error when user types
        if (errors[name]) {
            setErrors(prev => ({ ...prev, [name]: null }));
        }

        // If password changes, also clear confirmPassword error
        if (name === 'password' && errors.confirmPassword) {
            setErrors(prev => ({ ...prev, confirmPassword: null }));
        }
    };

    const handleCategoryClick = (category) => {
        if (selectedCategories.includes(category)) {
            // If already selected, remove it (deselect)
            setSelectedCategories(selectedCategories.filter(item => item !== category));
        } else {
            // If not selected, add to the end
            setSelectedCategories([...selectedCategories, category]);
        }
        // Clear category error if user selects
        if (errors.categories) {
            setErrors(prev => ({ ...prev, categories: null }));
        }
    };

    // --- Validation Logic ---
    const validate = () => {
        let newErrors = {};

        // 1. Name Check
        if (!formData.name.trim()) {
            newErrors.name = "이름을 입력해주세요.";
        }

        // 2. Login ID Check (6+ chars, at least 2 numbers)
        const numberCount = (formData.loginId.match(/\d/g) || []).length;
        if (formData.loginId.length < 6 || numberCount < 2) {
            newErrors.loginId = "아이디는 6자 이상이며, 숫자가 2개 이상 포함되어야 합니다.";
        }

        // 3. Email Check (@ symbol)
        if (!formData.email.includes('@')) {
            newErrors.email = "유효한 이메일 형식이 아닙니다 (@ 누락).";
        }

        // 3-1. Age Group Check
        if (!formData.ageGroup) {
            newErrors.ageGroup = "연령대를 선택해주세요.";
        }

        // 3-2. Gender Check
        if (!formData.gender) {
            newErrors.gender = "성별을 선택해주세요.";
        }

        // 4. Password Check (Basic requirement check)
        if (formData.password.length < 8) {
            newErrors.password = "비밀번호는 최소 8자 이상이어야 합니다.";
        }

        // 4-1. Password Confirmation Check
        if (formData.password !== formData.confirmPassword) {
            newErrors.confirmPassword = "비밀번호가 일치하지 않습니다.";
        }

        // 5. Category Check (At least 3)
        if (selectedCategories.length < 3) {
            newErrors.categories = `최소 3개의 관심 분야를 선택해주세요. (현재 ${selectedCategories.length}개 선택)`;
        }

        // 6. Agreement Check
        if (!formData.marketingAgree) {
            newErrors.agreement = "서비스 이용을 위해 사용자 경험 데이터 수집에 동의해야 합니다.";
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (validate()) {
            // Prepare data for backend (matching UserCreateRequest schema)
            const submitData = {
                login_id: formData.loginId,
                user_real_name: formData.name,
                password_hash: formData.password, // Backend expects 'password_hash'
                email: formData.email,
                age_range: formData.ageGroup, // Backend expects 'age_range', not 'age_group'
                gender: formData.gender,
                subscribed_categories: selectedCategories,
                subscribed_keywords: [], // Optional field in backend
                marketing_agree: formData.marketingAgree
            };

            try {
                console.log("Sending signup request:", submitData);

                // POST request to backend
                const response = await fetch(`${API_BASE_URL}/users`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(submitData)
                });

                const data = await response.json();

                if (response.ok) {
                    // Success
                    console.log("Account created successfully:", data);
                    alert("회원가입이 완료되었습니다! 로그인 페이지로 이동합니다.");
                    navigate('/login');
                } else {
                    // Backend returned an error
                    console.error("Signup failed:", data);
                    alert(`회원가입 실패: ${data.detail || '알 수 없는 오류가 발생했습니다.'}`);
                }
            } catch (error) {
                // Network or other error
                console.error("Network error:", error);
                alert('서버와 연결할 수 없습니다. 나중에 다시 시도해주세요.');
            }
        }
    };

    return (
        <div className="create-account-container">
            <Header
                headerTop="on"
                headerMain="on"
                headerBottom="on"
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
            />
            <div className="create-account-box">
                <h2>회원가입</h2>
                <p className="description">
                    맞춤형 뉴스 서비스를 경험하기 위해 계정을 생성하세요.
                </p>

                <form onSubmit={handleSubmit}>

                    {/* 1. Name Section */}
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

                    {/* 2. Login ID Section */}
                    <div className="input-group">
                        <label>아이디</label>
                        <input
                            type="text"
                            name="loginId"
                            placeholder="영문+숫자 포함 6자 이상 (숫자 2개 필수)"
                            value={formData.loginId}
                            onChange={handleChange}
                            className={errors.loginId ? "input-error" : ""}
                        />
                        {errors.loginId && <span className="error-msg">{errors.loginId}</span>}
                    </div>

                    {/* 3. Password Section */}
                    <div className="input-group">
                        <label>비밀번호</label>
                        <div className="password-wrapper">
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
                                className="toggle-btn"
                                onClick={() => setShowPassword(!showPassword)}
                            >
                                {showPassword ? "숨기기" : "보기"}
                            </button>
                        </div>
                        {/* Strength Meter */}
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
                        {errors.password && <span className="error-msg">{errors.password}</span>}
                    </div>

                    {/* 3-1. Confirm Password Section */}
                    <div className="input-group">
                        <label>비밀번호 확인</label>
                        <div className="password-wrapper">
                            <input
                                type={showPassword ? "text" : "password"}
                                name="confirmPassword"
                                placeholder="비밀번호를 다시 입력해주세요"
                                value={formData.confirmPassword}
                                onChange={handleChange}
                                className={errors.confirmPassword ? "input-error" : ""}
                            />
                            <button
                                type="button"
                                className="toggle-btn"
                                onClick={() => setShowPassword(!showPassword)}
                            >
                                {showPassword ? "숨기기" : "보기"}
                            </button>
                        </div>
                        {formData.password && formData.confirmPassword && formData.password === formData.confirmPassword && (
                            <span className="success-msg" style={{ color: '#2ecc71', fontSize: '0.85rem', marginTop: '4px', display: 'block' }}>
                                비밀번호 일치
                            </span>
                        )}
                        {errors.confirmPassword && <span className="error-msg">{errors.confirmPassword}</span>}
                    </div>

                    {/* 4. Email Section */}
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

                    {/* 5. Category Selection (Interactive) */}
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

                    {/* 6. Agreement Section */}
                    <div className="agreement-section">
                        <label className="checkbox-container">
                            <input
                                type="checkbox"
                                name="marketingAgree"
                                checked={formData.marketingAgree}
                                onChange={handleChange}
                            />
                            <span className="checkmark"></span>
                            <span className="text">
                                (필수) 사용자 경험 향상 및 서비스 개선을 위한 활동 기록 수집에 동의합니다.
                            </span>
                        </label>
                        {errors.agreement && <span className="error-msg">{errors.agreement}</span>}
                    </div>

                    <button type="submit" className="submit-btn">계정 생성하기</button>

                    <div className="login-redirect">
                        이미 계정이 있으신가요? <span onClick={() => navigate('/login')}>로그인 하기</span>
                    </div>
                </form>
            </div>
        </div>
    );
}
