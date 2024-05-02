import { useEffect, useState } from 'react';
import { useForm } from "react-hook-form";
import { yupResolver } from '@hookform/resolvers/yup';
import * as Yup from 'yup';
import { useSelector, useDispatch } from 'react-redux';
import { Button, Card, Col, Form, Row } from "react-bootstrap";

import { history } from 'tools/history';
import { authActions } from 'store';

export const Auth = () => {
    const [isLogin, setIsLogin] = useState(true);
    const handleToggle = () => {
      setIsLogin((prev) => !prev);
    };

    const dispatch = useDispatch();
    const authUser = useSelector(x => x.auth.user);
    const authError = useSelector(x => x.auth.error);

    useEffect(() => {
        // redirect to home if already logged in
        if (authUser) history.navigate('/');

        // eslint-disable-next-line react-hooks/exhaustive-deps
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

    function onSubmit({ username, password }) {
        return dispatch(authActions.login({ isLogin, username, password }));
    }

    return (
        <Row className="justify-content-center">
            <Col xs={10} md={4}>
                <Card className="my-5 px-5 py-3">
                    <h1 className="m-3 text-center">{isLogin ? "Log In" : "Sign Up"}</h1>
                    <Form onSubmit={handleSubmit(onSubmit)}>
                        <Form.Group className="my-2">
                            <Form.Label>Username</Form.Label>
                            <Form.Control name="username" type="text" {...register('username')} />
                            <div className="invalid-feedback">{errors.username?.message}</div>
                        </Form.Group>
                        <Form.Group className="my-2">
                            <Form.Label>Password</Form.Label>
                            <Form.Control name="password" type="password" {...register('password')} />
                            <div className="invalid-feedback">{errors.password?.message}</div>
                        </Form.Group>
                        {authError &&
                            <div className="alert alert-danger mt-3 mb-0">{authError.message}</div>
                        }

                        <div className="mt-3 text-center">
                            <p>
                                {isLogin ? "Don't" : "Already"} have an account ?{" "}
                                <Button
                                size="sm"
                                variant="outline-primary"
                                onClick={handleToggle}
                                >
                                {isLogin ? "Sign Up" : "Log In"}
                                </Button>
                            </p>
                            <Button className="btn btn-block" type="submit" disabled={isSubmitting}>
                                {isLogin ? "Log In" : "Sign Up"}
                            </Button>
                        </div>
                    </Form>
                </Card>
            </Col>
        </Row>
    )
}
