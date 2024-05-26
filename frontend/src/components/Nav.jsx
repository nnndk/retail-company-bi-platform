import { NavLink } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';

import { authActions } from 'store';
import { text_resources, languages } from '../resources'

export const Nav = ({ language, setLanguage }) => {
    const authUser = useSelector(x => x.auth.user);
    const dispatch = useDispatch();
    const logout = () => dispatch(authActions.logout());

    const changeLanguage = (e) => {
        e.preventDefault();
        let lang = e.target.value;
        setLanguage(lang)
    }
    
    return (
        <nav className="navbar navbar-expand navbar-dark bg-dark">
            <div className="navbar-nav w-100 justify-content-between">
                <NavLink to="/" className="nav-item nav-link">{text_resources["mainPage"][language]}</NavLink>
                <div className="ml-auto d-flex align-items-center">
                    <select
                        value={language}
                        onChange={changeLanguage}
                        className="form-select mr-2 custom-select-dark"
                    >
                        {languages.map((lang) => (
                            <option key={lang} value={lang}>{lang}</option>
                        ))}
                    </select>
                    {authUser && (
                        <button onClick={logout} className="btn btn-link nav-item nav-link">
                            {text_resources["logout"][language]}
                        </button>
                    )}
                </div>
            </div>
        </nav>
    );
}