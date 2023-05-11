import React, { Component, useContext } from "react";
import { Link } from 'react-router-dom';
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faEnvelope, faUnlockAlt } from "@fortawesome/free-solid-svg-icons";
import {
  Col,
  Row,
  Form,
  Card,
  Container,
  InputGroup,
  Image,
  Button,
} from "@themesberg/react-bootstrap";
import ReactLogo from "../assets/img/technologies/logo.svg";
import { domainPath } from "../constants/utils";
import BgImage from "../assets/img/illustrations/signin.svg";
import { TabTitle } from "../constants/generalFunctions";
import { AppContext } from "./AppContext";
import { Routes } from "../routes";

export default class Signin extends Component {
  static contextType = AppContext;

  constructor(props) {
    super(props);
    this.state = {
      email: "",
      password: "",
    };
  }

  handleChange = (e) => {
    const name = e.target.name;
    const value = e.target.value;
    this.setState((prevstate) => {
      const newState = { ...prevstate };
      newState[name] = value;
      return newState;
    });
  };

  getUserInfo = () => {
    const {fetchRequest} = this.context;

    fetchRequest(`auth/user-info`, 'GET')
    .then((data) => {
      if (data != undefined) {
        localStorage.setItem('username', data.username);
        localStorage.setItem('org_name', data.org_name);
        this.props.history.push("/");
      }
    }).catch((err) => alert(err));
  }

  handleLogin = (e, data) => {
    e.preventDefault();
    fetch(domainPath + "/auth/sign-in", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    })
      .then((res) => res.json())
      .then((json) => {
        if (json.token) {
          localStorage.setItem('token',json.token);
          this.getUserInfo();
        } else {
          alert("Your account is invalid");
        }
      })
      .catch((err) => alert(err));
  };

  render() {
    TabTitle("Sign In");

    return (
      <main className="bg-dark vh-100">
        <section className="d-flex align-items-center my-5 mt-lg-6 mb-lg-5">
          <Container>
            <Row
              className="justify-content-center form-bg-image"
              style={{ backgroundImage: `url(${BgImage})` }}
            >
              <Col
                xs={5}
                className="d-flex align-items-center justify-content-center"
              >
                <div className="bg-white shadow-soft border rounded border-primary p-4 p-lg-5 w-100 fmxw-500">
                  <div className="text-center text-md-center mb-4 mt-md-0">
                    <h3 className="mb-0">Sign in to RecomSys</h3>
                  </div>
                  <div className="text-center text-md-center mb-4 mt-md-0">
                    <Image className="" src={ReactLogo} height={80} />
                  </div>
                  <Form
                    className="mt-4"
                    onSubmit={(e) => this.handleLogin(e, this.state)}
                  >
                    <Form.Group id="email" className="mb-4">
                      <Form.Label>Your Email</Form.Label>
                      <InputGroup>
                        <InputGroup.Text>
                          <FontAwesomeIcon icon={faEnvelope} />
                        </InputGroup.Text>
                        <Form.Control
                          autoFocus
                          required
                          type="text"
                          placeholder="example@company.com"
                          name="email"
                          value={this.state.email}
                          onChange={this.handleChange}
                        />
                      </InputGroup>
                    </Form.Group>
                    <Form.Group>
                      <Form.Group id="password" className="mb-4">
                        <Form.Label>Your Password</Form.Label>
                        <InputGroup>
                          <InputGroup.Text>
                            <FontAwesomeIcon icon={faUnlockAlt} />
                          </InputGroup.Text>
                          <Form.Control
                            minLength="8"
                            required
                            type="password"
                            placeholder="Password"
                            name="password"
                            value={this.state.password}
                            onChange={this.handleChange}
                          />
                        </InputGroup>
                      </Form.Group>
                      <div className="d-flex justify-content-center align-items-center mb-4">
                        <Card.Link  as={Link} to={Routes.ForgotPassword.path} className="small">
                          Forget password?
                        </Card.Link>
                      </div>
                    </Form.Group>
                    <Button variant="primary" type="submit" className="w-100">
                      Sign in
                    </Button>
                    <Link 
                      className="btn btn-light w-100 mt-2"
                      role="button"
                      to={Routes.Signup.path}
                      > 
                      Sign up
                      </Link>
                    {/* <Button variant="light" className="w-100 mt-2"
                    onClick={() => handleSignup("sign-up")}>
                      Sign up
                    </Button> */}
                  </Form>
                </div>
              </Col>
            </Row>
          </Container>
        </section>
      </main>
    );
  }
}
