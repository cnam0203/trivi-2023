
import React, { useState, useEffect, useContext } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faBell, faCog, faEnvelopeOpen, faHouseUser, faSearch, faSignOutAlt, faUserShield } from "@fortawesome/free-solid-svg-icons";
import { faUserCircle } from "@fortawesome/free-regular-svg-icons";
import { Row, Col, Nav, Form, Image, Navbar, Dropdown, Container, ListGroup, InputGroup } from '@themesberg/react-bootstrap';
import { Link, useHistory } from 'react-router-dom';
import { Routes } from '../routes';



import NOTIFICATIONS_DATA from "../data/notifications";
import Profile3 from "../assets/img/team/profile-picture-3.jpg";
import { AppContext } from "../pages/AppContext";

export default (props) => {

  const [searchQuery, setSearchQuery] = useState('');
  const history = useHistory();

  const handleFormSubmit = (event) => {
    event.preventDefault();
    history.push(`/data-knowledge/search-result?query=${searchQuery}`);
  };

  return (
    <Navbar variant="dark" expanded className="ps-0 pe-2 pb-0">
      <Container fluid className="px-0">
        <div className="d-flex justify-content-between w-100">
          <div className="d-flex align-items-center">
            <Form className="navbar-search" onSubmit={handleFormSubmit}>
              <Form.Group id="topbarSearch" style={{width: '500px'}}>
                <InputGroup className="input-group-merge search-bar" required>
                  <InputGroup.Text><FontAwesomeIcon icon={faSearch} /></InputGroup.Text>
                  <Form.Control type="text" placeholder="Make a question about your data" 
                  value={searchQuery}
                  onChange={(event) => setSearchQuery(event.target.value)}/>
                </InputGroup>
              </Form.Group>
            </Form>
          </div>
          <Nav className="align-items-center">
            <Dropdown as={Nav.Item}>
              <Dropdown.Toggle as={Nav.Link} className="pt-1 px-0">
                <div className="media d-flex align-items-center">
                  {/* <Image src={faUserShield} className="user-avatar md-avatar rounded-circle" /> */}
                  <div className="media-body ms-2 text-dark align-items-center d-none d-lg-block">
                    <FontAwesomeIcon icon={faUserCircle} className="me-2" /> 
                    <span className="mb-0 font-small fw-bold">{localStorage.getItem('org_name')}, {localStorage.getItem('username')}</span>
                  </div>
                </div>
              </Dropdown.Toggle>
              <Dropdown.Menu className="user-dropdown dropdown-menu-right mt-2">
                <Dropdown.Item className="fw-bold" as={Link} to={Routes.Profile.path}>
                  <FontAwesomeIcon icon={faUserCircle} className="me-2" /> Change password
                </Dropdown.Item>
                <Dropdown.Item className="fw-bold" as={Link} to={Routes.Organization.path}>
                  <FontAwesomeIcon icon={faHouseUser} className="me-2" /> Change organization's info
                </Dropdown.Item>

                {/* <Dropdown.Item className="fw-bold">
                  <FontAwesomeIcon icon={faSignOutAlt} className="text-danger me-2" /> Logout
                </Dropdown.Item> */}
              </Dropdown.Menu>
            </Dropdown>
          </Nav>
        </div>
      </Container>
    </Navbar>
  );
};
