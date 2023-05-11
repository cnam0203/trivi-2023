import React, { Component, useContext } from "react";
import { Link } from 'react-router-dom';
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faEnvelope, faHouseUser, faKey, faUnlockAlt } from "@fortawesome/free-solid-svg-icons";
import {
  Col,
  Row,
  Form,
  Card,
  Container,
  InputGroup,
  Image,
  Button,
  Alert
} from "@themesberg/react-bootstrap";
import ReactLogo from "../assets/img/technologies/logo.svg";
import { domainPath } from "../constants/utils";
import BgImage from "../assets/img/illustrations/signin.svg";
import { TabTitle } from "../constants/generalFunctions";
import { AppContext } from "./AppContext";
import { Routes } from "../routes";

export default class Signup extends Component {
  static contextType = AppContext;

  constructor(props) {
    super(props);
    this.state = {
      email: "",
      password: "",
      org_name: "",
      org_descript: "",
      showAlert: false,
      alertMessage: "",
      isSuccess: false,
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

  handleSignup = (e, data) => {
    e.preventDefault();
    console.log(domainPath + "/auth/sign-up");
    fetch(domainPath + "/auth/sign-up", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    })
      .then((res) => res.json())
      .then((json) => {
          this.setState({
            showAlert: true,
            alertMessage: json.message,
            isSuccess: json.status == 200 ? true : false
          })
      })
      .catch((err) => {
        this.setState({
          showAlert: true,
          alertMessage: err,
          isSuccess: false
        })
      });
  };

  render() {
    TabTitle("Sing Up");

    return (
      <>
      <main className="bg-dark">
      <div className="d-flex justify-content-end p-3">
      <Alert className="col-3" show={this.state.showAlert} variant={this.state.isSuccess ? 'success' : 'danger'}>
        <Alert.Heading className="d-flex justify-content-center">{this.state.alertMessage}</Alert.Heading>
          <hr />
          <div className="d-flex justify-content-center">
            {
              this.state.isSuccess ? 
              <Button variant="outline-success"
                    as={Link} to={Routes.Signin.path}>
                OK
              </Button> : 
              <Button variant="outline-danger" 
                  onClick={() => {
                    this.setState({
                      showAlert: false,
                      alertMessage: '',
                      isSuccess: false,
                      email: '',
                      password: '',
                      org_name: '',
                      org_descript: ''
                    })
                  }}>
                OK
              </Button>
            }
          </div>
        </Alert>
        </div>
        <section className="d-flex align-items-center my-5 mt-lg-5 mb-lg-6">
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
                    <h3 className="mb-0">Sign Up to RecomSys</h3>
                  </div>
                  {/* <div className="text-center text-md-center mb-4 mt-md-0">
                    <Image className="" src={ReactLogo} height={80} />
                  </div> */}
                  <Form
                    className="mt-4"
                    onSubmit={(e) => this.handleSignup(e, this.state)}
                  >

<div className="d-flex justify-content-center align-items-center mb-1">
                        <Card.Link className="fs-5 fw-bold">
                          Organization Information
                        </Card.Link>
                      </div>
                    <Form.Group id="orgname" className="mb-3">
                      <Form.Label>Name</Form.Label>
                      <InputGroup>
                        <InputGroup.Text>
                          <FontAwesomeIcon icon={faHouseUser} />
                        </InputGroup.Text>
                        <Form.Control
                          autoFocus
                          required
                          type="text"
                          placeholder="Trivi"
                          name="org_name"
                          value={this.state.org_name}
                          onChange={this.handleChange}
                        />
                      </InputGroup>
                    </Form.Group>
                    <Form.Group>
                      <Form.Group id="description" className="mb-4">
                        <Form.Label>Description</Form.Label>
                        <InputGroup>
                          <InputGroup.Text>
                            <FontAwesomeIcon icon={faKey} />
                          </InputGroup.Text>
                          <Form.Control
                            required
                            type="text"
                            placeholder="An export company"
                            name="org_descript"
                            value={this.state.org_descript}
                            onChange={this.handleChange}
                          />
                        </InputGroup>
                      </Form.Group>
                    </Form.Group>
                    <div className="d-flex justify-content-center align-items-center mb-1">
                        <Card.Link className="fs-5 fw-bold">
                          Account Information
                        </Card.Link>
                      </div>
                    <Form.Group id="email" className="mb-3">
                      <Form.Label>Email</Form.Label>
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
                      <Form.Group id="password" className="mb-3">
                        <Form.Label>New Password</Form.Label>
                        <InputGroup>
                          <InputGroup.Text>
                            <FontAwesomeIcon icon={faUnlockAlt} />
                          </InputGroup.Text>
                          <Form.Control
                            required
                            minLength="8"
                            type="password"
                            placeholder="Password"
                            name="password"
                            value={this.state.password}
                            onChange={this.handleChange}
                          />
                        </InputGroup>
                      </Form.Group>
                    </Form.Group>
                    <div className="d-flex justify-content-center align-items-center mb-4">
                        <Card.Link  as={Link} to={Routes.Signin.path} className="small">
                          Back to Sign In
                        </Card.Link>
                      </div>
                    <Button variant="primary" type="submit" className="w-100">
                      Sign up
                    </Button>
                    {/* <Link 
                      className="btn btn-light w-100 mt-2"
                      role="button"
                      to="/sign-in"
                      > 
                      Sign in
                      </Link> */}
                  </Form>
                </div>
              </Col>
            </Row>
          </Container>
        </section>
      </main>
      </>
    );
  }
}
