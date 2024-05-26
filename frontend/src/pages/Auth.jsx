import { useEffect, useState } from 'react';
import { useForm } from "react-hook-form";
import { yupResolver } from '@hookform/resolvers/yup';
import * as Yup from 'yup';
import { useSelector, useDispatch } from 'react-redux';
import { Button, Card, Col, Form, Row } from "react-bootstrap";

import { history } from 'tools/history';
import { authActions } from 'store';
import { text_resources } from '../resources'


export const Auth = ({ language }) => {
    const [isLogin, setIsLogin] = useState(true);
    const handleToggle = () => {
      setIsLogin((prev) => !prev);
    };

    const dispatch = useDispatch();
    const authUser = useSelector(x => x.auth.user);
    const authError = useSelector(x => x.auth.error);

    useEffect(() => {
        // redirect to home if already logged in
        console.log(authUser)
        if (authUser) history.navigate('/');
    }, []);

    // form validation rules 
    const validationSchema = Yup.object().shape({
        username: Yup.string().required('Username is required'),
        password: Yup.string().required('Password is required')
    });
    const formOptions = { resolver: yupResolver(validationSchema) };

    // get functions to build form with useForm() hook
    const { register, handleSubmit, formState } = useForm(formOptions);
    const { errors, isSubmitting } = formState;

    const onSubmit = async ({ username, password }) => {
        const pingResponse = await fetch(`${process.env.REACT_APP_API_URL}/ping/`, {
            method: 'GET'
        });
        console.log(pingResponse)
        let pingData = await pingResponse.json();
        console.log(pingData)

        return dispatch(authActions.login({ isLogin, username, password }));
    }

    return (
        <Row className="justify-content-center">
            <Col xs={12} sm={10} md={8} lg={6} xl={4}>
                <Card className="my-5 px-5 py-3">
                    <h1 className="m-3 text-center">{isLogin ? text_resources["loginTitle"][language] : text_resources["signupTitle"][language]}</h1>
                    <Form onSubmit={handleSubmit(onSubmit)}>
                        <Form.Group className="my-2">
                            <Form.Label>{text_resources["username"][language]}</Form.Label>
                            <Form.Control name="username" type="text" {...register('username')} />
                            <div className="invalid-feedback">{errors.username?.message}</div>
                        </Form.Group>
                        <Form.Group className="my-2">
                            <Form.Label>{text_resources["password"][language]}</Form.Label>
                            <Form.Control name="password" type="password" {...register('password')} />
                            <div className="invalid-feedback">{errors.password?.message}</div>
                        </Form.Group>
                        {authError &&
                            <div className="alert alert-danger mt-3 mb-0">{authError.message}</div>
                        }

                        <div className="mt-3 text-center">
                            <p>
                                {isLogin ? text_resources["dontHaveAccount"][language] : text_resources["alreadyHaveAccount"][language]} {" "}
                                <br />
                                <Button
                                size="sm"
                                variant="outline-primary"
                                className="mt-2"
                                onClick={handleToggle}
                                >
                                {isLogin ? text_resources["signup"][language] : text_resources["login"][language]}
                                </Button>
                            </p>
                            <Button className="btn btn-block" type="submit" disabled={isSubmitting}>
                                {isLogin ? text_resources["login"][language] : text_resources["signup"][language]}
                            </Button>
                        </div>
                    </Form>
                </Card>
            </Col>
        </Row>
    )
}
