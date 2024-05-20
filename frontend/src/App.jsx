import { Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom';
import { useState } from 'react';

import { history } from 'tools/history';
import { Nav } from 'components/Nav';
import { PrivateRoute } from 'components/PrivateRoute';
import { Main } from 'pages/Main';
import { Auth } from 'pages/Auth';


export const App = () => {
    history.navigate = useNavigate();
    history.location = useLocation();
    const [language, setLanguage] = useState("EN");

    return (
        <div className="app-container bg-light">
            <Nav language={language} setLanguage={setLanguage} />
            <div className="pt-4 pb-4 px-4">
                <Routes>
                    <Route
                        path="/"
                        element={
                            <PrivateRoute>
                                <Main language={language} />
                            </PrivateRoute>
                        }
                    />
                    <Route path="/login" element={<Auth language={language} />} />
                    <Route path="*" element={<Navigate to="/" />} />
                </Routes>
            </div>
        </div>
    );
}
