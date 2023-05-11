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

export default class ForgotPassword extends Component {
  static contextType = AppContext;

  constructor(props) {
    super(props);
    this.state = {
      username: "",
      password: "",
      confirmPassword: "",
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

  handleReset = (e, data) => {
    e.preventDefault();
    fetch(domainPath + "/reset-password/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    })
      .then((res) => res.json())
      .then((json) => {
        if (json.token) {
          this.props.history.push("/");
        }
      })
      .catch((err) => alert(err));
  };

  render() {
    TabTitle("Log In");

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
                    <h3 className="mb-0">Reset new password</h3>
                  </div>
                  <div className="text-center text-md-center mb-4 mt-md-0">
                    <Image className="" src={ReactLogo} height={80} />
                  </div>
                  <Form
                    className="mt-4"
                    onSubmit={(e) => this.handleReset(e, this.state)}
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
                          name="username"
                          value={this.state.username}
                          onChange={this.handleChange}
                        />
                      </InputGroup>
                    </Form.Group>
                    <Form.Group>
                      <Form.Group id="password" className="mb-4">
                        <Form.Label>New Password</Form.Label>
                        <InputGroup>
                          <InputGroup.Text>
                            <FontAwesomeIcon icon={faUnlockAlt} />
                          </InputGroup.Text>
                          <Form.Control
                            required
                            type="password"
                            placeholder="Password"
                            name="password"
                            value={this.state.password}
                            onChange={this.handleChange}
                          />
                        </InputGroup>
                      </Form.Group>
                      <Form.Group id="password" className="mb-4">
                        <Form.Label>Confirm Password</Form.Label>
                        <InputGroup>
                          <InputGroup.Text>
                            <FontAwesomeIcon icon={faUnlockAlt} />
                          </InputGroup.Text>
                          <Form.Control
                            required
                            type="password"
                            placeholder="Password"
                            name="password"
                            value={this.state.confirmPassword}
                            onChange={this.handleChange}
                          />
                        </InputGroup>
                      </Form.Group>
                      <div className="d-flex justify-content-center align-items-center mb-4">
                        <Card.Link  as={Link} to={Routes.Signin.path} className="small">
                          Back to Sign In
                        </Card.Link>
                      </div>
                    </Form.Group>
                    <Button variant="primary" type="submit" className="w-100">
                      Reset
                    </Button>
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
