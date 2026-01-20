import React, { useState, useEffect } from 'react';
import './App.css';
import axios from 'axios';
import { Main } from './pages/Main';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import ArticlePage from './pages/ArticlePage.jsx';
import CategoryPage from './pages/CategoryPage.jsx';
import CreateAccount from './pages/CreateAccount.jsx';
import Issues from './pages/Issues.jsx';
import Login from './components/Login.jsx';
import MyPage from './pages/MyPage.jsx';
import EditAccount from './pages/EditAccount.jsx';
import SearchResult from './pages/SearchResult.jsx';

import PoliticsPage from './pages/PoliticsPage.jsx';
import EconomicsPage from './pages/EconomicsPage.jsx';
import SocietyPage from './pages/SocietyPage.jsx';
import LivingCulturePage from './pages/LivingCulturePage.jsx';
import SciencePage from './pages/SciencePage.jsx';
import WorldPage from './pages/WorldPage.jsx';
import TotalMenuPage from './pages/TotalMenuPage.jsx';

function App() {
  return (
    <BrowserRouter future={{
      v7_startTransition: true,
      v7_relativeSplatPath: true,
    }}>
      <div className="App">
        <Routes>
          <Route path="/" element={<Main />} />
          <Route path="/article" element={<ArticlePage />} />
          <Route path="/politics" element={<PoliticsPage />} />
          <Route path="/economy" element={<EconomicsPage />} />
          <Route path="/society" element={<SocietyPage />} />
          <Route path="/living-culture" element={<LivingCulturePage />} />
          <Route path="/science" element={<SciencePage />} />
          <Route path="/world" element={<WorldPage />} />
          <Route path="/total" element={<TotalMenuPage />} />
          <Route path="/category/:name" element={<CategoryPage />} />
          <Route path="/issues" element={<Issues />} />
          <Route path='/login' element={<Login />} />
          <Route path='/CreateAccount' element={<CreateAccount />} />
          <Route path='/mypage' element={<MyPage />} />
          <Route path='/edit-account' element={<EditAccount />} />
          <Route path='/search' element={<SearchResult />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
